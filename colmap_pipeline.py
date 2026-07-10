#!/usr/bin/env python3
"""Create a COLMAP dataset compatible with 3D Gaussian Splatting."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".tif", ".tiff", ".bmp", ".webp"}


def run(command: list[str], dry_run: bool = False) -> None:
    print("+", subprocess.list2cmdline(command), flush=True)
    if not dry_run:
        subprocess.run(command, check=True)


def find_colmap(requested: str) -> str:
    candidate = Path(requested).expanduser()
    if candidate.is_file():
        return str(candidate.resolve())
    found = shutil.which(requested)
    if found:
        return found
    raise FileNotFoundError(
        f"COLMAP executable '{requested}' was not found. Install COLMAP and add it "
        "to PATH, or pass --colmap-exe with its full path."
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run COLMAP and produce images/ plus sparse/0 for Gaussian Splatting."
    )
    parser.add_argument("images", type=Path, help="Directory containing source images")
    parser.add_argument("output", type=Path, help="Dataset output directory")
    parser.add_argument("--colmap-exe", default="colmap", help="COLMAP executable name or path")
    parser.add_argument(
        "--matcher",
        choices=("exhaustive", "sequential"),
        default="exhaustive",
        help="Use sequential for ordered video frames; exhaustive for unordered photos",
    )
    parser.add_argument(
        "--camera-model",
        default="OPENCV",
        help="COLMAP camera model used during feature extraction",
    )
    parser.add_argument(
        "--multiple-cameras",
        action="store_true",
        help="Estimate a separate camera for each image instead of sharing intrinsics",
    )
    parser.add_argument("--use-cpu", action="store_true", help="Disable CUDA SIFT")
    parser.add_argument("--overwrite", action="store_true", help="Replace an existing output directory")
    parser.add_argument("--dry-run", action="store_true", help="Print commands without running COLMAP")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    images = args.images.expanduser().resolve()
    output = args.output.expanduser().resolve()

    if not images.is_dir():
        raise NotADirectoryError(f"Image directory does not exist: {images}")
    image_count = sum(
        1 for path in images.rglob("*") if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS
    )
    if image_count < 2:
        raise ValueError(f"At least 2 supported images are required; found {image_count} in {images}")

    colmap = args.colmap_exe if args.dry_run else find_colmap(args.colmap_exe)
    if output.exists():
        if not args.overwrite:
            raise FileExistsError(f"Output already exists: {output}. Use --overwrite to replace it.")
        if not args.dry_run:
            shutil.rmtree(output)

    distorted = output / "distorted"
    database = distorted / "database.db"
    sparse = distorted / "sparse"
    if not args.dry_run:
        sparse.mkdir(parents=True)

    gpu = "0" if args.use_cpu else "1"
    run(
        [
            colmap,
            "feature_extractor",
            "--database_path", str(database),
            "--image_path", str(images),
            "--ImageReader.single_camera", "0" if args.multiple_cameras else "1",
            "--ImageReader.camera_model", args.camera_model,
            "--SiftExtraction.use_gpu", gpu,
        ],
        args.dry_run,
    )

    matcher_command = "sequential_matcher" if args.matcher == "sequential" else "exhaustive_matcher"
    run(
        [colmap, matcher_command, "--database_path", str(database), "--SiftMatching.use_gpu", gpu],
        args.dry_run,
    )
    run(
        [
            colmap,
            "mapper",
            "--database_path", str(database),
            "--image_path", str(images),
            "--output_path", str(sparse),
        ],
        args.dry_run,
    )

    model = sparse / "0"
    if not args.dry_run and not model.is_dir():
        raise RuntimeError(
            "COLMAP did not create distorted/sparse/0. Check image overlap and the COLMAP log."
        )
    run(
        [
            colmap,
            "image_undistorter",
            "--image_path", str(images),
            "--input_path", str(model),
            "--output_path", str(output),
            "--output_type", "COLMAP",
        ],
        args.dry_run,
    )

    # image_undistorter writes model files directly under sparse/. Most Gaussian
    # Splatting loaders expect sparse/0/ instead.
    final_sparse = output / "sparse"
    final_model = final_sparse / "0"
    if not args.dry_run:
        final_model.mkdir(exist_ok=True)
        for name in ("cameras.bin", "images.bin", "points3D.bin"):
            source = final_sparse / name
            if source.exists():
                shutil.move(str(source), str(final_model / name))
        print(f"\nDone: {output}")
        print(f"Registered model: {final_model}")
        print(f"Undistorted images: {output / 'images'}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (FileNotFoundError, NotADirectoryError, FileExistsError, RuntimeError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        raise SystemExit(1)

