FROM runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel-ubuntu22.04

USER root
WORKDIR /workspace

RUN apt-get update && apt-get install -y git wget && rm -rf /var/lib/apt/lists/*

# 古い安定版のComfyUIをピンポイントでダウンロード（相性問題を完全解決）
RUN git clone https://github.com/comfyanonymous/ComfyUI.git && \
    cd ComfyUI && \
    git checkout ec6f16adb607fa8d14b26670106e1a09d8401e20 && \
    pip install -r requirements.txt && \
    pip install numpy==1.26.4

# 必要なモジュールのインストール
RUN pip install insightface onnxruntime onnxruntime-gpu runpod

# 顔交換プラグイン（ReActor）のダウンロード
RUN cd /workspace/ComfyUI/custom_nodes && git clone https://github.com/Gourieff/comfyui-reactor-node.git

# 【重要】AIが絵を描くための画材（モデルデータ）をサーバー内にダウンロード
RUN wget -O /workspace/ComfyUI/models/checkpoints/sdxl_lightning.safetensors "https://huggingface.co/ByteDance/SDXL-Lightning/resolve/main/sdxl_lightning_4step.safetensors"
RUN mkdir -p /workspace/ComfyUI/models/insightface/models && \
    wget -O /workspace/ComfyUI/models/insightface/models/inswapper_128.onnx "https://github.com/facefusion/facefusion-assets/releases/download/models/inswapper_128.onnx"
RUN mkdir -p /workspace/ComfyUI/models/facerestore_models && \
    wget -O /workspace/ComfyUI/models/facerestore_models/codeformer.pth "https://github.com/sczhou/CodeFormer/releases/download/v0.1.0/codeformer.pth"

# ファイルの配置と起動コマンド
COPY handler.py /workspace/handler.py
COPY workflow.json /workspace/workflow.json

CMD /bin/bash -c "python3 /workspace/ComfyUI/main.py --listen > /workspace/comfyui.log 2>&1 & python3 /workspace/handler.py"
