FROM runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel-ubuntu22.04

USER root
WORKDIR /workspace

# システム要件のインストール
RUN apt-get update && apt-get install -y git wget && rm -rf /var/lib/apt/lists/*

# エラーの出ない安定版ComfyUIのダウンロード
RUN git clone https://github.com/comfyanonymous/ComfyUI.git && \
    cd ComfyUI && \
    git checkout 9e32085 && \
    pip install -r requirements.txt && \
    pip install "numpy<2"

# 顔交換（ReActor）とRunPodの通信モジュールのインストール
RUN pip install insightface onnxruntime onnxruntime-gpu runpod

# プログラムファイルの配置
COPY handler.py /workspace/handler.py
COPY workflow.json /workspace/workflow.json

# 起動コマンド
CMD /bin/bash -c "python3 /workspace/ComfyUI/main.py --listen > /workspace/comfyui.log 2>&1 & python3 /workspace/handler.py"
