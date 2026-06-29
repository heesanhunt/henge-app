FROM runpod/pytorch:2.2.1-py3.10-cuda12.1.1-devel-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Install dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    wget \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

# Install ComfyUI
RUN git clone https://github.com/comfyanonymous/ComfyUI.git /workspace/ComfyUI
WORKDIR /workspace/ComfyUI
RUN pip install -r requirements.txt

# Install Custom Nodes (ReActor for Face Swap)
WORKDIR /workspace/ComfyUI/custom_nodes
RUN git clone https://github.com/Gourieff/comfyui-reactor-node.git
WORKDIR /workspace/ComfyUI/custom_nodes/comfyui-reactor-node
RUN pip install -r requirements.txt

# Download Models (SDXL Lightning + insightface models for ReActor)
# We will download these during build to bake them into the image for instant boot
WORKDIR /workspace/ComfyUI/models/checkpoints
RUN wget -O sdxl_lightning.safetensors "https://huggingface.co/ByteDance/SDXL-Lightning/resolve/main/sdxl_lightning_4step.safetensors"

WORKDIR /workspace/ComfyUI/models/facerestore_models
RUN wget -O codeformer.pth "https://github.com/sczhou/CodeFormer/releases/download/v0.1.0/codeformer.pth"

WORKDIR /workspace/ComfyUI/models/insightface/models
# ReActor requires buffalo_l model which is usually downloaded automatically, but we can pre-download it if needed.

WORKDIR /workspace
COPY handler.py /workspace/handler.py
COPY workflow.json /workspace/workflow.json

RUN pip install runpod

# Start ComfyUI in background and run handler
CMD python3 /workspace/ComfyUI/main.py --listen & python3 /workspace/handler.py
