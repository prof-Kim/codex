# COLMAP Dataset Builder for Gaussian Splatting

Build a COLMAP dataset that can be used directly with [3D Gaussian Splatting](https://github.com/graphdeco-inria/gaussian-splatting) from a directory of photos or extracted video frames.

The generated dataset has the expected layout:

```text
dataset/
?쒋?? images/                 # Undistorted images
?붴?? sparse/
    ?붴?? 0/
        ?쒋?? cameras.bin
        ?쒋?? images.bin
        ?붴?? points3D.bin
```

## Requirements

- Python 3.9 or newer
- [COLMAP](https://colmap.github.io/install.html) 3.8 or newer
- A set of sharp images with roughly 60??0% overlap between neighboring views

If the COLMAP executable is not available on `PATH`, provide its full path with `--colmap-exe`.

## Usage

For an unordered photo collection:

```bash
python colmap_pipeline.py ./source_images ./dataset
```

For video frames stored in capture order:

```bash
python colmap_pipeline.py ./frames ./dataset --matcher sequential
```

Windows example with an explicit COLMAP path:

```powershell
py colmap_pipeline.py .\source_images .\dataset `
  --colmap-exe "C:\Program Files\COLMAP\COLMAP.bat"
```

Run without CUDA SIFT:

```bash
python colmap_pipeline.py ./source_images ./dataset --use-cpu
```

Add `--overwrite` to replace an existing output directory. Use `--dry-run` to print every COLMAP command without executing it.

## Capture Recommendations

- Move slowly around the subject and capture it from every required direction.
- Keep the zoom, focal length, and image resolution fixed throughout the capture.
- Avoid reflective or transparent surfaces, moving people, and motion blur.
- Keep the default single-camera setting when all images use the same camera and lens.
- Add `--multiple-cameras` when images from different cameras or lenses are mixed.

## Validate the Result

After a successful run, pass the dataset directory containing `images/` and `sparse/0/` to the Gaussian Splatting trainer. If COLMAP registers far fewer cameras than the number of source images, first check for insufficient overlap, blur, or repetitive textures.

Show all options:

```bash
python colmap_pipeline.py --help
```

