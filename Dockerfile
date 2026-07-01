# 最終突破版V2！軽量ベース＆安全なダウンロード方式
FROM pytorch/pytorch:2.2.0-cuda12.1-cudnn8-runtime

USER root
WORKDIR /workspace

# 必要なパッケージをインストール
RUN apt-get update && apt-get install -y git wget libgl1 libglib2.0-0 && rm -rf /var/lib/apt/lists/*

# ComfyUI本体のインストール（キャッシュ無効化で容量節約）
RUN git clone https://github.com/comfyanonymous/ComfyUI.git && \
    cd ComfyUI && \
    git checkout ec6f16adb607fa8d14b26670106e1a09d8401e20 && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir numpy==1.26.4 insightface onnxruntime onnxruntime-gpu runpod

# エラーが起きたReActorプラグインを安全なgit cloneでインストール
RUN git clone https://github.com/Gourieff/comfyui-reactor-node.git /workspace/ComfyUI/custom_nodes/comfyui-reactor-node

# 【重要】AIが絵を描くための画材（モデルデータ）をサーバー内にダウンロード
RUN wget -O /workspace/ComfyUI/models/checkpoints/sdxl_lightning.safetensors "https://huggingface.co/ByteDance/SDXL-Lightning/resolve/main/sdxl_lightning_4step.safetensors"
RUN mkdir -p /workspace/ComfyUI/models/insightface/models && \
    wget -O /workspace/ComfyUI/models/insightface/models/inswapper_128.onnx "https://github.com/facefusion/facefusion-assets/releases/download/models/inswapper_128.onnx"
RUN mkdir -p /workspace/ComfyUI/models/facerestore_models && \
    wget -O /workspace/ComfyUI/models/facerestore_models/codeformer.pth "https://github.com/sczhou/CodeFormer/releases/download/v0.1.0/codeformer.pth"

COPY handler.py /workspace/handler.py
COPY workflow.json /workspace/workflow.json

CMD ["/bin/bash", "-c", "python3 /workspace/ComfyUI/main.py --listen > /workspace/comfyui.log 2>&1 & python3 /workspace/handler.py"]
