# COLMAP dataset builder for Gaussian Splatting

사진 또는 동영상 프레임으로부터 [3D Gaussian Splatting](https://github.com/graphdeco-inria/gaussian-splatting)이 읽을 수 있는 COLMAP 데이터셋을 만듭니다.

생성되는 핵심 구조는 다음과 같습니다.

```text
dataset/
├── images/                 # undistorted images
└── sparse/
    └── 0/
        ├── cameras.bin
        ├── images.bin
        └── points3D.bin
```

## 준비

- Python 3.9 이상
- [COLMAP](https://colmap.github.io/install.html) 3.8 이상
- 서로 60~80% 정도 겹치고 흔들림이 적은 이미지 권장

COLMAP 실행 파일이 `PATH`에 없다면 `--colmap-exe`로 전체 경로를 지정할 수 있습니다.

## 실행

일반 사진 세트:

```bash
python colmap_pipeline.py ./source_images ./dataset
```

촬영 순서대로 추출한 동영상 프레임:

```bash
python colmap_pipeline.py ./frames ./dataset --matcher sequential
```

Windows에서 COLMAP 경로를 직접 지정하는 예:

```powershell
py colmap_pipeline.py .\source_images .\dataset `
  --colmap-exe "C:\Program Files\COLMAP\COLMAP.bat"
```

CUDA를 사용할 수 없는 환경:

```bash
python colmap_pipeline.py ./source_images ./dataset --use-cpu
```

기존 출력 폴더를 지우고 다시 처리하려면 `--overwrite`를 추가합니다. 실제 실행 없이 COLMAP 명령만 확인하려면 `--dry-run`을 사용합니다.

## 이미지 촬영 팁

- 피사체 주위를 천천히 이동하며 모든 방향에서 촬영합니다.
- 줌, 초점 거리, 해상도를 촬영 중 바꾸지 않습니다.
- 반사체, 투명체, 움직이는 사람과 강한 모션 블러를 피합니다.
- 하나의 카메라/렌즈로 촬영한 경우 기본 설정을 유지합니다.
- 여러 카메라가 섞였으면 `--multiple-cameras`를 사용합니다.

## 결과 확인

성공 후 `dataset/images`와 `dataset/sparse/0`을 Gaussian Splatting 데이터 경로로 전달합니다. 등록된 카메라 수가 원본 이미지 수보다 크게 적으면 이미지 겹침, 블러, 반복 무늬 여부를 먼저 확인하세요.

전체 옵션:

```bash
python colmap_pipeline.py --help
```
