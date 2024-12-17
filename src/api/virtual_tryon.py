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


def run_virtual_tryon(task_folder_path, sub_folder_name, mask_prompt):

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
                if "images" in node_output:
                    images_output = []
                    for image in node_output["images"]:
                        image_data = get_image(
                            image["filename"], image["subfolder"], image["type"]
                        )
                        images_output.append(image_data)
                output_images[node_id] = images_output

        return output_images

    prompt_text = """

    """

    prompt = json.loads(prompt_text)
    # set the text prompt for our positive CLIPTextEncode
    # prompt["6"]["inputs"]["text"] = "masterpiece best quality man"

    # set the seed for our KSampler node
    prompt["19"]["inputs"]["image"] = f"{sub_folder_name}_model.png"
    prompt["21"]["inputs"]["image"] = f"{sub_folder_name}_cloth.png"
    prompt["26"]["inputs"]["prompt"] = mask_prompt
    print("sub folder name is : ", sub_folder_name)
    # str(task_folder_path / "garment.jpg")
    random_seed = random.randint(0, 999999999)
    prompt["28"]["inputs"]["seed"] = random_seed

    print(prompt)

    ws = websocket.WebSocket()
    ws.connect("ws://{}/ws?clientId={}".format(server_address, client_id))
    images = get_images(ws, prompt)

    # Commented out code to display the output images:
    final_path = task_folder_path / "output.png"
    print("final_path is")

    for node_id in images:
        for image_data in images[node_id]:
            from PIL import Image
            import io

            image = Image.open(io.BytesIO(image_data))
        image.save(final_path, "png")

    return final_path
