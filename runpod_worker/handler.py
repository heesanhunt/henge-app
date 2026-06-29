import runpod
import os
import urllib.request
import urllib.parse
import json
import base64
import time

# ComfyUI server details
COMFYUI_HOST = "127.0.0.1:8188"

def check_server():
    """Wait for ComfyUI to be ready"""
    while True:
        try:
            req = urllib.request.Request(f"http://{COMFYUI_HOST}/system_stats")
            with urllib.request.urlopen(req) as response:
                if response.status == 200:
                    break
        except Exception:
            pass
        time.sleep(1)

def queue_prompt(prompt):
    """Send workflow prompt to ComfyUI"""
    p = {"prompt": prompt}
    data = json.dumps(p).encode('utf-8')
    req = urllib.request.Request(f"http://{COMFYUI_HOST}/prompt", data=data)
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read())

def get_image(filename, subfolder, folder_type):
    """Retrieve generated image from ComfyUI"""
    data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
    url_values = urllib.parse.urlencode(data)
    req = urllib.request.Request(f"http://{COMFYUI_HOST}/view?{url_values}")
    with urllib.request.urlopen(req) as response:
        return response.read()

def get_history(prompt_id):
    """Get history of a prompt execution"""
    req = urllib.request.Request(f"http://{COMFYUI_HOST}/history/{prompt_id}")
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read())

def handler(job):
    """RunPod Serverless Handler"""
    job_input = job.get("input", {})
    face_image_base64 = job_input.get("face_image")
    
    if not face_image_base64:
        return {"error": "No face image provided"}
        
    check_server()
    
    # 1. Save input image to ComfyUI input folder
    input_path = "/workspace/ComfyUI/input/face.jpg"
    with open(input_path, "wb") as f:
        f.write(base64.b64decode(face_image_base64))
        
    # 2. Load workflow (we will define this later)
    with open("/workspace/workflow.json", "r") as f:
        workflow = json.load(f)
        
    # 3. Queue prompt
    prompt_res = queue_prompt(workflow)
    prompt_id = prompt_res['prompt_id']
    
    # 4. Wait for completion
    while True:
        history = get_history(prompt_id)
        if prompt_id in history:
            break
        time.sleep(1)
        
    # 5. Extract image
    outputs = history[prompt_id]['outputs']
    for node_id in outputs:
        node_output = outputs[node_id]
        if 'images' in node_output:
            image_meta = node_output['images'][0]
            image_data = get_image(image_meta['filename'], image_meta['subfolder'], image_meta['type'])
            
            # Return as base64 string
            return {
                "image_base64": base64.b64encode(image_data).decode('utf-8')
            }

    return {"error": "Image generation failed"}

runpod.serverless.start({"handler": handler})
