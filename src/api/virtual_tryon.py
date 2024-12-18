import os
import json
import random
import websocket
import uuid
import io
from PIL import Image
from ..utils.utils import ComfyUIClient  # utils.py에서 ComfyUIClient 가져오기


def load_workflow(workflow_path):
    """
    워크플로우 JSON 파일 로드

    :param workflow_path: 워크플로우 JSON 파일 경로
    :return: 로드된 프롬프트 데이터
    """
    with open(workflow_path, "r", encoding="utf-8") as f:
        return json.load(f)


def update_prompt(prompt, sub_folder_name, mask_prompt):
    """
    프롬프트 업데이트

    :param prompt: 워크플로우 프롬프트 데이터
    :param sub_folder_name: 서브 폴더 이름
    :param mask_prompt: 마스크 프롬프트
    """
    prompt["19"]["inputs"]["image"] = f"{sub_folder_name}_model.png"
    prompt["21"]["inputs"]["image"] = f"{sub_folder_name}_cloth.png"
    prompt["26"]["inputs"]["prompt"] = mask_prompt
    random_seed = random.randint(0, 999999999)
    prompt["28"]["inputs"]["seed"] = random_seed


def get_workflow_path(workflow_name):
    """
    워크플로우 파일 경로를 생성합니다.

    :param workflow_name: 워크플로우 파일 이름 (확장자 제외)
    :return: 워크플로우 파일의 절대 경로
    """
    # 현재 파일의 절대 경로
    current_file_path = os.path.abspath(__file__)

    # 프로젝트 루트 경로 (src/api의 2단계 상위)
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_file_path)))

    # 워크플로우 파일 경로
    workflow_path = os.path.join(project_root, "src/workflows", workflow_name + ".json")

    return workflow_path


def run_virtual_tryon(task_folder_path, sub_folder_name, mask_prompt):
    """
    Virtual Try-On 실행

    :param task_folder_path: 작업 폴더 경로
    :param sub_folder_name: 서브 폴더 이름
    :param mask_prompt: 생성할 마스크 프롬프트
    :return: 최종 이미지 경로
    """
    server_address = "203.252.147.202:8188"
    client_id = str(uuid.uuid4())

    # ComfyUIClient 인스턴스 생성
    client = ComfyUIClient(server_address, client_id)

    # 워크플로우 로드
    workflow_path = get_workflow_path("virtual_tryon")
    prompt = load_workflow(workflow_path)

    # 프롬프트 업데이트
    update_prompt(prompt, sub_folder_name, mask_prompt)
    print("sub folder name is : ", sub_folder_name)

    # 웹소켓 연결 및 이미지 가져오기
    ws = websocket.WebSocket()
    ws.connect(f"ws://{client.server_address}/ws?clientId={client.client_id}")
    images = client.get_images(ws, prompt)

    # 최종 이미지 저장
    final_path = task_folder_path / "output.png"

    for node_id in images:
        for image_data in images[node_id]:
            image = Image.open(io.BytesIO(image_data))
        image.save(final_path, "png")

    return final_path
