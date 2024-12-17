import os
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


def run_video_to_illustrate(task_folder_path, sub_folder_name):

    server_address = "203.252.147.202:8188"
    client_id = str(uuid.uuid4())

    def queue_prompt(prompt):
        p = {"prompt": prompt, "client_id": client_id}
        data = json.dumps(p).encode("utf-8")
        req = urllib.request.Request(
            "http://{}/prompt".format(server_address), data=data
        )
        return json.loads(urllib.request.urlopen(req).read())

    def get_image(filename, subfolder, folder_type):
        data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
        url_values = urllib.parse.urlencode(data)
        with urllib.request.urlopen(
            "http://{}/view?{}".format(server_address, url_values)
        ) as response:
            return response.read()

    def get_history(prompt_id):
        with urllib.request.urlopen(
            "http://{}/history/{}".format(server_address, prompt_id)
        ) as response:
            return json.loads(response.read())

    def get_images(ws, prompt):
        prompt_id = queue_prompt(prompt)["prompt_id"]
        output_images = {}
        while True:
            out = ws.recv()
            if isinstance(out, str):
                message = json.loads(out)
                if message["type"] == "executing":
                    data = message["data"]
                    if data["node"] is None and data["prompt_id"] == prompt_id:
                        break  # Execution is done
            else:
                continue  # previews are binary data

        history = get_history(prompt_id)[prompt_id]
        print("history is : ", history)
        for o in history["outputs"]:
            for node_id in history["outputs"]:
                node_output = history["outputs"][node_id]
                if "gifs" in node_output:
                    images_output = []
                    for image in node_output["gifs"]:
                        print("img is : ", image)
                        print("img filename is", image["filename"])
                #         image_data = get_image(image['filename'], image['subfolder'], image['type'])
                #         images_output.append(image_data)
                # output_images[node_id] = images_output

        return image["filename"]

    # 현재 파일의 절대 경로
    current_file_path = os.path.abspath(__file__)

    # 프로젝트 루트 경로 (src/api의 2단계 상위)
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_file_path)))

    # 워크플로우 파일 경로
    workflow_path = os.path.join(project_root, "workflows", "video_to_illustrate.json")

    with open(workflow_path, "r", encoding="utf-8") as f:
        prompt = json.load(f)

    # set the seed for our KSampler node
    prompt["1"]["inputs"][
        "video"
    ] = f"/mnt/nas4/nto/ComfyUI/input/{sub_folder_name}_video.mp4"
    prompt["33"]["inputs"][
        "image"
    ] = f"/mnt/nas4/nto/ComfyUI/input/{sub_folder_name}_face.png"

    print("sub folder name is : ", sub_folder_name)
    # str(task_folder_path / "garment.jpg")

    ws = websocket.WebSocket()
    ws.connect("ws://{}/ws?clientId={}".format(server_address, client_id))
    video_name = get_images(ws, prompt)

    # Commented out code to display the output images:
    final_path = f"/mnt/nas4/nto/ComfyUI/output/{video_name}"
    print("final_path is")

    return final_path
