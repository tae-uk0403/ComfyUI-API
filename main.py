from datetime import datetime
from pathlib import Path
from fastapi import FastAPI, File, UploadFile, status, Depends
import logging
import json
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.responses import PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Annotated
import shutil


from src.api.video_to_illustrate import run_video_to_illustrate
from src.api.flux_lora import flux_lora
from src.api.virtual_tryon import run_virtual_tryon


with open("error_code.json", "r") as f:
    responses = json.load(f)


app = FastAPI(
    title="ComfyUI API",
    version="0.0.0",
)

# app.mount("/static", StaticFiles(directory="static"), name="static")


logging.basicConfig(filename="app.log", level=logging.INFO)


# CORS 설정 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 출처 허용
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메서드 허용
    allow_headers=["*"],  # 모든 요청 헤더 허용
)


@app.post(
    "/api/v1.0/flux_lora",
    tags=["API Reference"],
    status_code=status.HTTP_200_OK,
    response_class=FileResponse,
    responses={
        **responses,
        200: {
            "content": {"image/png": {"example": "(binary image data)"}},
            "description": "Created",
        },
    },
)
async def flux_lora_api(
    lora_name: str,
    generate_prompt: str,
):
    now_date = datetime.now()
    sub_folder_name = now_date.strftime("%Y%m%d%H%M%S%f")
    task_folder_path = (
        Path("api/flux_lora") / "temp_process_task_files" / sub_folder_name
    )
    print("task_folder_path is ", task_folder_path)
    task_id = sub_folder_name
    task_folder_path.mkdir(parents=True, exist_ok=True)
    lora_name = lora_name + ".safetensors"
    print("lora_name i s ", lora_name)

    lora_model_path = Path(f"/mnt/nas4/nto/ComfyUI/models/loras/{lora_name}")
    lora_model_path.parent.mkdir(parents=True, exist_ok=True)
    print("lora_model_path is ", lora_model_path)

    result_image_path = flux_lora(task_folder_path, lora_name, generate_prompt)

    return FileResponse(
        result_image_path,
        media_type="image/png",
        status_code=status.HTTP_200_OK,
        headers={"Content-Disposition": f"attachment; filename={task_id}_image.png"},
    )


@app.post(
    "/api/v1.0/virtual_tryon",
    tags=["API Reference"],
    status_code=status.HTTP_200_OK,
    response_class=FileResponse,
    responses={
        **responses,
        200: {
            "content": {"image/png": {"example": "(binary image data)"}},
            "description": "Created",
        },
    },
)
async def virtual_tryon(
    model_image_file: Annotated[
        UploadFile, File(media_type="image/png", description="image for upper cloth")
    ],
    image_file: Annotated[
        UploadFile, File(media_type="image/png", description="image for model")
    ],
    mask_prompt: str,
):
    """
    - **Description**: This endpoint virtaully dress the cloth you choose

    - **Request Parameters**:
        - **`model_image_file`**: model image you want to dress up
            - **Example**:

                <img src='http://203.252.147.202:8000/static/virtual_tryon/origin.png' width=200, hegith=300>

        - **`image_file`**: cloth image to dress the model

            - **Example**:

                <img src='http://203.252.147.202:8000/static/virtual_tryon/cloth.png' width=200. height=300>


    - **Response**: Image of the model wearing the input cloth
        - **Example**:

            <img src='http://203.252.147.202:8000/static/virtual_tryon/tryon.png' width=200. height=300>
    """
    if not image_file:
        return {"error": "No file uploaded"}
    print("request succeed")

    now_date = datetime.now()
    sub_folder_name = now_date.strftime("%Y%m%d%H%M%S%f")
    task_folder_path = (
        Path("api/virtual_tryon") / "temp_process_task_files" / sub_folder_name
    )
    print("task_folder_path is ", task_folder_path)
    task_id = sub_folder_name
    task_folder_path.mkdir(parents=True, exist_ok=True)

    image_file_path = task_folder_path / Path("garment.jpg")
    input_file_path = Path(f"/mnt/nas4/nto/ComfyUI/input/{sub_folder_name}_cloth.png")
    image_file_path.parent.mkdir(parents=True, exist_ok=True)
    input_file_path.parent.mkdir(parents=True, exist_ok=True)

    with image_file_path.open("wb") as f:
        f.write(await image_file.read())

    shutil.copy(image_file_path, input_file_path)

    model_image_file_path = task_folder_path / Path("model.jpg")
    model_input_file_path = Path(
        f"/mnt/nas4/nto/ComfyUI/input/{sub_folder_name}_model.png"
    )
    model_image_file_path.parent.mkdir(parents=True, exist_ok=True)
    model_input_file_path.parent.mkdir(parents=True, exist_ok=True)

    with model_image_file_path.open("wb") as f:
        f.write(await model_image_file.read())

    shutil.copy(model_image_file_path, model_input_file_path)

    result_image_path = run_virtual_tryon(
        task_folder_path, sub_folder_name, mask_prompt
    )

    return FileResponse(
        result_image_path,
        media_type="image/png",
        status_code=status.HTTP_200_OK,
        headers={"Content-Disposition": f"attachment; filename={task_id}_image.png"},
    )


@app.post(
    "/api/v1.0/video_to_illustrate",
    tags=["API Reference"],
    status_code=status.HTTP_200_OK,
    response_class=FileResponse,
    responses={
        **responses,
        200: {
            "content": {"image/png": {"example": "(binary image data)"}},
            "description": "Created",
        },
    },
)
async def video_to_illustrate(
    face_video_file: Annotated[
        UploadFile,
        File(media_type="video/mp4", description="video to mimic the face movement"),
    ],
    image_file: Annotated[
        UploadFile,
        File(media_type="image/png", description="image you want to make the video"),
    ],
):
    """
    - **Description**: This endpoint virtaully dress the cloth you choose

    - **Request Parameters**:
        - **`face_video_file`**: video to mimic the face movement
            - **Example**:

                <img src='http://203.252.147.202:8000/static/virtual_tryon/origin.png' width=200, hegith=300>

        - **`image_file`**: image you want to make the video

            - **Example**:

                <img src='http://203.252.147.202:8000/static/virtual_tryon/cloth.png' width=200. height=300>


    - **Response**: video of mimic the face movement
        - **Example**:

            <img src='http://203.252.147.202:8000/static/virtual_tryon/tryon.png' width=200. height=300>
    """
    if not image_file:
        return {"error": "No file uploaded"}
    print("request succeed")

    now_date = datetime.now()
    sub_folder_name = now_date.strftime("%Y%m%d%H%M%S%f")
    task_folder_path = (
        Path("api/video_to_illustrate") / "temp_process_task_files" / sub_folder_name
    )
    print("task_folder_path is ", task_folder_path)
    task_id = sub_folder_name
    task_folder_path.mkdir(parents=True, exist_ok=True)

    image_file_path = task_folder_path / Path("face.jpg")
    input_file_path = Path(f"/mnt/nas4/nto/ComfyUI/input/{sub_folder_name}_face.png")
    image_file_path.parent.mkdir(parents=True, exist_ok=True)
    input_file_path.parent.mkdir(parents=True, exist_ok=True)

    with image_file_path.open("wb") as f:
        f.write(await image_file.read())

    shutil.copy(image_file_path, input_file_path)

    face_video_file_path = task_folder_path / Path("video.mp4")
    face_video_input_path = Path(
        f"/mnt/nas4/nto/ComfyUI/input/{sub_folder_name}_video.mp4"
    )
    face_video_file_path.parent.mkdir(parents=True, exist_ok=True)
    face_video_input_path.parent.mkdir(parents=True, exist_ok=True)

    with face_video_file_path.open("wb") as f:
        f.write(await face_video_file.read())

    shutil.copy(face_video_file_path, face_video_input_path)

    result_video_path = run_video_to_illustrate(task_folder_path, sub_folder_name)

    return FileResponse(
        result_video_path,
        media_type="video/mp4",
        status_code=status.HTTP_200_OK,
        headers={"Content-Disposition": f"attachment; filename={task_id}_video.mp4"},
    )
