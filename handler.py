import runpod
import os
import urllib.request
import urllib.parse
import json
import base64
import time

COMFYUI_HOST = "127.0.0.1:8188"

def print_log(msg):
    print(msg, flush=True)

def check_server():
    print_log("Waiting for ComfyUI to start...")
    start_time = time.time()
    while True:
        try:
            req = urllib.request.Request(f"http://{COMFYUI_HOST}/system_stats")
            with urllib.request.urlopen(req) as response:
                if response.status == 200:
                    print_log("ComfyUI is ready!")
                    break
        except Exception:
            pass
        
        if time.time() - start_time > 180:
            raise Exception("ComfyUI startup timeout.")
        time.sleep(2)

def queue_prompt(prompt):
    p = {"prompt": prompt}
    data = json.dumps(p).encode('utf-8')
    req = urllib.request.Request(f"http://{COMFYUI_HOST}/prompt", data=data)
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read())

def get_image(filename, subfolder, folder_type):
    data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
    url_values = urllib.parse.urlencode(data)
    req = urllib.request.Request(f"http://{COMFYUI_HOST}/view?{url_values}")
    with urllib.request.urlopen(req) as response:
        return response.read()

def get_history(prompt_id):
    req = urllib.request.Request(f"http://{COMFYUI_HOST}/history/{prompt_id}")
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read())

def handler(job):
    job_input = job.get("input", {})
    face_image_base64 = job_input.get("face_image")
    positive_prompt = job_input.get("positive_prompt")

    if not face_image_base64:
        return {"error": "No face image provided"}

    check_server()

    input_path = "/workspace/ComfyUI/input/face.jpg"
    os.makedirs(os.path.dirname(input_path), exist_ok=True)
    with open(input_path, "wb") as f:
        f.write(base64.b64decode(face_image_base64))
        
    with open("/workspace/workflow.json", "r") as f:
        workflow = json.load(f)
        
    if positive_prompt and "6" in workflow:
        workflow["6"]["inputs"]["text"] = positive_prompt
        
    prompt_res = queue_prompt(workflow)
    prompt_id = prompt_res['prompt_id']
    
    while True:
        history = get_history(prompt_id)
        if prompt_id in history:
            break
        time.sleep(1)
        
    outputs = history[prompt_id]['outputs']
    for node_id in outputs:
        node_output = outputs[node_id]
        if 'images' in node_output:
            image_meta = node_output['images'][0]
            image_data = get_image(image_meta['filename'], image_meta['subfolder'], image_meta['type'])
            return {"image_base64": base64.b64encode(image_data).decode('utf-8')}

    return {"error": "Image generation failed"}

runpod.serverless.start({"handler": handler})
