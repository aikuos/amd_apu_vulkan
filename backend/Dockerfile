FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive
ENV AMD_VULKAN_ICD=RADV

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential cmake curl git libvulkan-dev libvulkan1 \
    mesa-vulkan-drivers spirv-headers spirv-tools glslc vulkan-tools \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /tmp
RUN git clone --depth 1 https://github.com/ggml-org/llama.cpp.git
WORKDIR /tmp/llama.cpp
RUN cmake -B build -DGGML_VULKAN=ON -DCMAKE_BUILD_TYPE=Release \
    && cmake --build build --config Release -j"$(nproc)" \
    && cp build/bin/llama-server /usr/local/bin/llama-server

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
EXPOSE 8000
ENTRYPOINT ["/entrypoint.sh"]
