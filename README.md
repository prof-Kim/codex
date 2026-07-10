# Gaussian Splatting용 COLMAP 데이터셋 생성기

[English](README_EN.md) | **한국어**

사진 또는 동영상 프레임 폴더로부터 [3D Gaussian Splatting](https://github.com/graphdeco-inria/gaussian-splatting)에서 바로 사용할 수 있는 COLMAP 데이터셋을 생성합니다.

생성되는 데이터셋 구조는 다음과 같습니다.

```text
dataset/
├── images/                 # 왜곡이 보정된 이미지
└── sparse/
    └── 0/
        ├── cameras.bin
        ├── images.bin
        └── points3D.bin
```

## 준비 사항

- Python 3.9 이상
- [COLMAP](https://colmap.github.io/install.html) 3.8 이상
- 인접한 장면끼리 약 60~80% 겹치도록 촬영한 선명한 이미지

COLMAP 실행 파일이 `PATH`에 없다면 `--colmap-exe` 옵션으로 전체 경로를 지정할 수 있습니다.

## 사용법

촬영 순서가 일정하지 않은 일반 사진 모음:

```bash
python colmap_pipeline.py ./source_images ./dataset
```

촬영 순서대로 저장된 동영상 프레임:

```bash
python colmap_pipeline.py ./frames ./dataset --matcher sequential
```

Windows에서 COLMAP 경로를 직접 지정하는 예시:

```powershell
py colmap_pipeline.py .\source_images .\dataset `
  --colmap-exe "C:\Program Files\COLMAP\COLMAP.bat"
```

CUDA 없이 CPU로 실행:

```bash
python colmap_pipeline.py ./source_images ./dataset --use-cpu
```

기존 출력 폴더를 지우고 다시 생성하려면 `--overwrite`를 추가합니다. 실제로 실행하지 않고 COLMAP 명령만 확인하려면 `--dry-run`을 사용합니다.

## 촬영 권장 사항

- 피사체 주위를 천천히 이동하면서 필요한 모든 방향에서 촬영합니다.
- 촬영 도중 줌, 초점 거리, 이미지 해상도를 변경하지 않습니다.
- 반사체, 투명체, 움직이는 사람, 모션 블러를 가능하면 피합니다.
- 모든 사진을 동일한 카메라와 렌즈로 촬영했다면 기본 단일 카메라 설정을 유지합니다.
- 서로 다른 카메라나 렌즈로 촬영한 이미지가 섞였다면 `--multiple-cameras`를 추가합니다.

## 결과 확인

작업이 완료되면 `images/`와 `sparse/0/`이 들어 있는 데이터셋 폴더를 Gaussian Splatting 학습기에 전달합니다. COLMAP에 등록된 카메라 수가 원본 이미지 수보다 크게 적다면 이미지 간 겹침 부족, 흔들림, 반복 무늬 등을 먼저 확인하세요.

전체 옵션 확인:

```bash
python colmap_pipeline.py --help
```
