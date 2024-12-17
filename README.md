# ComfyUI API

ComfyUI API는 이미지 생성 및 비디오 처리 기능을 제공하는 FastAPI 기반의 웹 서비스입니다. 이 API는 LoRA(저차원 회귀 분석) 모델을 사용하여 이미지를 생성하고, 비디오에서 얼굴 움직임을 모방하는 기능을 제공합니다.



## 기능
- **Flux LoRA**: LoRA 모델을 사용하여 주어진 프롬프트에 따라 이미지를 생성합니다.
- **비디오에서 얼굴 모방**: 주어진 비디오와 이미지를 사용하여 가상으로 옷을 입히는 기능을 제공합니다.

## 설치
1. 이 저장소를 클론합니다.
   ```bash
   git clone https://github.com/tae-uk0403/ComfyUI-API.git
   cd ComfyUI-API
   ```

2. 필요한 패키지를 설치합니다.
   ```bash
   pip install -r requirements.txt
   ```



## 사용법
API를 사용하기 위해서는 HTTP POST 요청을 통해 엔드포인트에 접근해야 합니다. 요청 본문에 필요한 매개변수를 포함해야 합니다.

## API 엔드포인트

### 1. 비디오에서 얼굴 모방
- **URL**: `/api/v1.0/video_to_illustrate`
- **메서드**: `POST`
- **요청 본문**:
  - `face_video_file`: 비디오 파일 (형식: video/mp4)
  - `image_file`: 이미지 파일 (형식: image/png)

- **응답**: 생성된 비디오 파일 (형식: video/mp4)

### 2. Flux LoRA
- **URL**: `/api/v1.0/flux_lora`
- **메서드**: `POST`
- **요청 본문**:
  - `lora_name`: 사용할 LoRA 모델의 이름 (예: `DARCHFLUX`)
  - `generate_prompt`: 이미지 생성을 위한 프롬프트 텍스트

- **응답**: 생성된 이미지 파일 (형식: image/png)


