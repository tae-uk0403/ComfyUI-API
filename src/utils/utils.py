import numpy as np
from PIL import Image
import cv2
from diffusers import AutoPipelineForInpainting
from diffusers.utils import load_image
import torch
import websocket  # NOTE: websocket-client (https://github.com/websocket-client/websocket-client)
import uuid
import json
import urllib.request
import urllib.parse
import random


# def queue_prompt(prompt):
#     p = {"prompt": prompt, "client_id": client_id}
#     data = json.dumps(p).encode("utf-8")
#     req = urllib.request.Request("http://{}/prompt".format(server_address), data=data)
#     return json.loads(urllib.request.urlopen(req).read())


# def get_image(filename, subfolder, folder_type):
#     data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
#     url_values = urllib.parse.urlencode(data)
#     with urllib.request.urlopen(
#         "http://{}/view?{}".format(server_address, url_values)
#     ) as response:
#         return response.read()


# def get_history(prompt_id):
#     with urllib.request.urlopen(
#         "http://{}/history/{}".format(server_address, prompt_id)
#     ) as response:
#         return json.loads(response.read())


# def get_images(ws, prompt):
#     prompt_id = queue_prompt(prompt)["prompt_id"]
#     output_images = {}
#     while True:
#         out = ws.recv()
#         if isinstance(out, str):
#             message = json.loads(out)
#             if message["type"] == "executing":
#                 data = message["data"]
#                 if data["node"] is None and data["prompt_id"] == prompt_id:
#                     break  # Execution is done
#         else:
#             continue  # previews are binary data

#     history = get_history(prompt_id)[prompt_id]
#     print("history is : ", history)
#     for o in history["outputs"]:
#         for node_id in history["outputs"]:
#             node_output = history["outputs"][node_id]
#             if "images" in node_output:
#                 images_output = []
#                 for image in node_output["images"]:
#                     image_data = get_image(
#                         image["filename"], image["subfolder"], image["type"]
#                     )
#                     images_output.append(image_data)
#             output_images[node_id] = images_output

#     return output_images


class ComfyUIClient:
    def __init__(self, server_address, client_id=None):
        """
        ComfyUI 서버와 상호작용하기 위한 클라이언트 초기화

        :param server_address: ComfyUI 서버 주소
        :param client_id: 클라이언트 ID (제공되지 않으면 랜덤 생성)
        """
        self.server_address = server_address
        self.client_id = client_id or str(uuid.uuid4())

    def queue_prompt(self, prompt):
        """
        프롬프트를 서버에 큐잉

        :param prompt: 실행할 프롬프트
        :return: 프롬프트 ID 등 응답 데이터
        """
        p = {"prompt": prompt, "client_id": self.client_id}
        data = json.dumps(p).encode("utf-8")
        req = urllib.request.Request(f"http://{self.server_address}/prompt", data=data)
        return json.loads(urllib.request.urlopen(req).read())

    def get_image(self, filename, subfolder, folder_type):
        """
        특정 이미지 가져오기

        :param filename: 이미지 파일명
        :param subfolder: 서브폴더
        :param folder_type: 폴더 타입
        :return: 이미지 데이터
        """
        data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
        url_values = urllib.parse.urlencode(data)
        with urllib.request.urlopen(
            f"http://{self.server_address}/view?{url_values}"
        ) as response:
            return response.read()

    def get_history(self, prompt_id):
        """
        특정 프롬프트의 히스토리 가져오기

        :param prompt_id: 프롬프트 ID
        :return: 프롬프트 히스토리
        """
        with urllib.request.urlopen(
            f"http://{self.server_address}/history/{prompt_id}"
        ) as response:
            return json.loads(response.read())

    def get_images(self, ws, prompt):
        """
        웹소켓을 통해 이미지 생성 및 가져오기

        :param ws: 웹소켓 연결
        :param prompt: 실행할 프롬프트
        :return: 생성된 이미지들
        """
        prompt_id = self.queue_prompt(prompt)["prompt_id"]
        output_images = {}

        while True:
            out = ws.recv()
            if isinstance(out, str):
                message = json.loads(out)
                if message["type"] == "executing":
                    data = message["data"]
                    if data["node"] is None and data["prompt_id"] == prompt_id:
                        break  # 실행 완료
            else:
                continue  # 미리보기는 이진 데이터

        history = self.get_history(prompt_id)[prompt_id]
        print("history is : ", history)

        for node_id in history["outputs"]:
            node_output = history["outputs"][node_id]
            if "images" in node_output:
                images_output = []
                for image in node_output["images"]:
                    image_data = self.get_image(
                        image["filename"], image["subfolder"], image["type"]
                    )
                    images_output.append(image_data)
                output_images[node_id] = images_output

        return output_images
