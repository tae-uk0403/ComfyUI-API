# import os
# from PIL import Image
# import cv2
# from diffusers import AutoPipelineForInpainting
# import numpy as np
# from diffusers.utils import load_image
# import torch
# import websocket #NOTE: websocket-client (https://github.com/websocket-client/websocket-client)
# import uuid
# import json
# import urllib.request
# import urllib.parse
# import random
# import pytube


# def run_flux_lora(task_folder_path, lora_name, generate_prompt):

#     server_address = "203.252.147.202:8188"
#     client_id = str(uuid.uuid4())

#     def queue_prompt(prompt):
#         p = {"prompt": prompt, "client_id": client_id}
#         data = json.dumps(p).encode('utf-8')
#         req =  urllib.request.Request("http://{}/prompt".format(server_address), data=data)
#         return json.loads(urllib.request.urlopen(req).read())

#     def get_image(filename, subfolder, folder_type):
#         data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
#         url_values = urllib.parse.urlencode(data)
#         with urllib.request.urlopen("http://{}/view?{}".format(server_address, url_values)) as response:
#             return response.read()

#     def get_history(prompt_id):
#         with urllib.request.urlopen("http://{}/history/{}".format(server_address, prompt_id)) as response:
#             return json.loads(response.read())

#     def get_images(ws, prompt):
#         prompt_id = queue_prompt(prompt)['prompt_id']
#         output_images = {}
#         while True:
#             out = ws.recv()
#             if isinstance(out, str):
#                 message = json.loads(out)
#                 if message['type'] == 'executing':
#                     data = message['data']
#                     if data['node'] is None and data['prompt_id'] == prompt_id:
#                         break #Execution is done
#             else:
#                 continue #previews are binary data

#         history = get_history(prompt_id)[prompt_id]
#         print("history is : ", history)
#         for o in history['outputs']:
#             for node_id in history['outputs']:
#                 node_output = history['outputs'][node_id]
#                 if 'images' in node_output:
#                     images_output = []
#                     for image in node_output['images']:
#                         image_data = get_image(image['filename'], image['subfolder'], image['type'])
#                         images_output.append(image_data)
#                 output_images[node_id] = images_output

#         return output_images


#     prompt_text = """
#   {
#     "5": {
#       "inputs": {
#         "width": 1024,
#         "height": 1024,
#         "batch_size": 1
#       },
#       "class_type": "EmptyLatentImage",
#       "_meta": {
#         "title": "Empty Latent Image"
#       }
#     },
#     "6": {
#       "inputs": {
#         "text": "sad, rainy, tired, house",
#         "clip": [
#           "29",
#           1
#         ]
#       },
#       "class_type": "CLIPTextEncode",
#       "_meta": {
#         "title": "CLIP Text Encode (Prompt)"
#       }
#     },
#     "8": {
#       "inputs": {
#         "samples": [
#           "13",
#           0
#         ],
#         "vae": [
#           "10",
#           0
#         ]
#       },
#       "class_type": "VAEDecode",
#       "_meta": {
#         "title": "VAE Decode"
#       }
#     },
#     "9": {
#       "inputs": {
#         "filename_prefix": "refrigerator",
#         "images": [
#           "8",
#           0
#         ]
#       },
#       "class_type": "SaveImage",
#       "_meta": {
#         "title": "Save Image"
#       }
#     },
#     "10": {
#       "inputs": {
#         "vae_name": "ae.safetensors"
#       },
#       "class_type": "VAELoader",
#       "_meta": {
#         "title": "Load VAE"
#       }
#     },
#     "11": {
#       "inputs": {
#         "clip_name1": "t5xxl_fp16.safetensors",
#         "clip_name2": "clip_l.safetensors",
#         "type": "flux"
#       },
#       "class_type": "DualCLIPLoader",
#       "_meta": {
#         "title": "DualCLIPLoader"
#       }
#     },
#     "13": {
#       "inputs": {
#         "noise": [
#           "25",
#           0
#         ],
#         "guider": [
#           "22",
#           0
#         ],
#         "sampler": [
#           "16",
#           0
#         ],
#         "sigmas": [
#           "17",
#           0
#         ],
#         "latent_image": [
#           "5",
#           0
#         ]
#       },
#       "class_type": "SamplerCustomAdvanced",
#       "_meta": {
#         "title": "SamplerCustomAdvanced"
#       }
#     },
#     "16": {
#       "inputs": {
#         "sampler_name": "euler"
#       },
#       "class_type": "KSamplerSelect",
#       "_meta": {
#         "title": "KSamplerSelect"
#       }
#     },
#     "17": {
#       "inputs": {
#         "scheduler": "simple",
#         "steps": 20,
#         "denoise": 1,
#         "model": [
#           "29",
#           0
#         ]
#       },
#       "class_type": "BasicScheduler",
#       "_meta": {
#         "title": "BasicScheduler"
#       }
#     },
#     "22": {
#       "inputs": {
#         "model": [
#           "29",
#           0
#         ],
#         "conditioning": [
#           "6",
#           0
#         ]
#       },
#       "class_type": "BasicGuider",
#       "_meta": {
#         "title": "BasicGuider"
#       }
#     },
#     "25": {
#       "inputs": {
#         "noise_seed": 526108353553606
#       },
#       "class_type": "RandomNoise",
#       "_meta": {
#         "title": "RandomNoise"
#       }
#     },
#     "27": {
#       "inputs": {
#         "unet_name": "flux1-dev.safetensors",
#         "weight_dtype": "fp8_e4m3fn"
#       },
#       "class_type": "UNETLoader",
#       "_meta": {
#         "title": "Load Diffusion Model"
#       }
#     },
#     "29": {
#       "inputs": {
#         "lora_name": "DARCHFLUX.safetensors",
#         "strength_model": 1,
#         "strength_clip": 1,
#         "model": [
#           "27",
#           0
#         ],
#         "clip": [
#           "11",
#           0
#         ]
#       },
#       "class_type": "LoraLoader",
#       "_meta": {
#         "title": "Load LoRA"
#       }
#     }
#   }
#     """

#     prompt = json.loads(prompt_text)
#     #set the text prompt for our positive CLIPTextEncode
#     # prompt["6"]["inputs"]["text"] = "masterpiece best quality man"

#     #set the seed for our KSampler node
#     prompt["29"]['inputs']["lora_name"] = lora_name
#     prompt["6"]['inputs']["text"] = generate_prompt
#     if lora_name == '3d.safetensors':
#           prompt["29"]['inputs']["strength_model"] = 1.2
#     if lora_name == 'Donald-Trump_Flux_v01e08.safetensors':
#           prompt["5"]['inputs']["width"] = 1280
#           prompt["5"]['inputs']["height"] = 720


#     # str(task_folder_path / "garment.jpg")

#     ws = websocket.WebSocket()
#     ws.connect("ws://{}/ws?clientId={}".format(server_address, client_id))
#     images = get_images(ws, prompt)

#     #Commented out code to display the output images:
#     final_path = task_folder_path / "output.png"
#     print('final_path is')

#     for node_id in images:
#         for image_data in images[node_id]:
#             from PIL import Image
#             import io
#             image = Image.open(io.BytesIO(image_data))
#         image.save(final_path, 'png')

#     return final_path

import os
import json
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


def update_prompt(prompt, lora_name, generate_prompt):
    """
    프롬프트 업데이트

    :param prompt: 워크플로우 프롬프트 데이터
    :param lora_name: LoRA 이름
    :param generate_prompt: 생성할 프롬프트
    """
    prompt["29"]["inputs"]["lora_name"] = lora_name
    prompt["6"]["inputs"]["text"] = generate_prompt

    if lora_name == "3d.safetensors":
        prompt["29"]["inputs"]["strength_model"] = 1.2
    if lora_name == "Donald-Trump_Flux_v01e08.safetensors":
        prompt["5"]["inputs"]["width"] = 1280
        prompt["5"]["inputs"]["height"] = 720


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


def flux_lora(task_folder_path, lora_name, generate_prompt):
    """
    Flux LoRA 실행

    :param task_folder_path: 작업 폴더 경로
    :param lora_name: LoRA 이름
    :param generate_prompt: 생성할 프롬프트
    :return: 최종 이미지 경로
    """
    server_address = "203.252.147.202:8188"
    client_id = str(uuid.uuid4())

    # ComfyUIClient 인스턴스 생성
    client = ComfyUIClient(server_address, client_id)

    # 워크플로우 로드
    workflow_path = get_workflow_path("flux_lora")
    prompt = load_workflow(workflow_path)

    # 프롬프트 업데이트
    update_prompt(prompt, lora_name, generate_prompt)
    print("sub folder name is : ", lora_name)

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
