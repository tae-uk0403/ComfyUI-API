# ComfyUI API
ComfyUI에서 만든 다양한 workflow를 FastAPI 기반 API로 자동화하였습니다. workflow에서 input으로 들어가는 parameter를 자유롭게 설정하고 결과물을 자동으로 받아볼 수 있습니다.


## 기능
- **Flux + LoRA**: Flux checkpoint와 LoRA 모델, prompt를 입력받아 이미지를 생성합니다.
- **Virtual-Tryon**: masking prompt, model_image, cloth_image를 사용하여 가상 착샷을 생성합니다.
- **Live-Portrait**: face image와 face video로 Live-portrait 기반 얼굴의 표정, 움직임을 모방한 영상을 생성합니다.






## API 기능

### 1. Flux_Lora
- **URL**: `/api/v1.0/flux_lora`
- **parameter**:
  - `lora_name`: 이미지 생성에 사용할 LoRA 모델 이름(example: `rapunzel`)
  - `generate_prompt`: 생성하고자 하는 이미지의 프롬프트

- **response**: 생성된 이미지 (image/png)
- **workflow**
![스크린샷 2024-12-18 오후 2 05 10](https://github.com/user-attachments/assets/d8cb0d63-fc2e-4b4a-9fb9-8aa8061133cf)

### 2. Virtual-Tryon
- **URL**: `/api/v1.0/virtual-tryon`

- **parameters**:
  - `model_image_file`: 옷을 입히고자 하는 모델 이미지
  - `image_file`: 입히고자 하는 옷 이미지
  - `mask_prompt`: 옷을 입히고자 하는 부분을 masking 하기 위한 prompt

- **response**: 생성된 이미지 파일 (형식: image/png)
- **workflow**
![스크린샷 2024-12-18 오후 2 01 18](https://github.com/user-attachments/assets/cba15da8-3bbb-4157-9833-5e9bb7833534)


### 3. Live-portrait
- **URL**: `/api/v1.0/video_to_illustrate`
- **parameter**:
  - `face_video_file`: 얼굴 움직임 영상
  - `image_file`: 얼굴 이미지

- **response**: 생성된 이미지 파일 

- **workflow**
![스크린샷 2024-12-18 오후 2 18 19](https://github.com/user-attachments/assets/9fc28b69-4b2c-49c9-97ca-c76a4202611b)
