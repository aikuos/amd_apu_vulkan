# AMD APU Vulkan GGUF Server

A small, self-contained Docker package for serving GGUF models on AMD APUs
with **llama.cpp + Vulkan/RADV** and an OpenAI-compatible API gateway.

It was validated on this server:

| Component | Value |
|---|---|
| CPU / APU | AMD Ryzen AI MAX+ 395 (Strix Halo) |
| GPU | Radeon 8060S, 40 CUs |
| GPU architecture | `gfx1151` (RDNA 3.5) |
| Memory | 96 GB LPDDR5X unified memory |
| Operating system | Ubuntu 24.04 LTS |
| Production acceleration | Mesa RADV Vulkan |

This package deliberately does not include vLLM/PyTorch ROCm. On the tested
hardware, Vulkan was the reliable inference route; PyTorch ROCm experiments
previously page-faulted under GPU workloads.

## Included model profile

The default `.env.example` targets Qwen3-Omni-30B-A3B-Instruct Q4_K_M:

- 18.6 GB Q4_K_M GGUF model
- 1.3 GB Q8_0 multimodal projector
- Text and image input; experimental audio input
- Native Qwen Talker speech output is not included in this GGUF path

See [TEST_RESULTS.md](TEST_RESULTS.md) for the validated short-request Q4 test.

## Quick start

```bash
cp .env.example .env
mkdir -p models/Qwen3-Omni-30B-A3B-Instruct-GGUF
hf download ggml-org/Qwen3-Omni-30B-A3B-Instruct-GGUF \
  Qwen3-Omni-30B-A3B-Instruct-Q4_K_M.gguf \
  mmproj-Qwen3-Omni-30B-A3B-Instruct-Q8_0.gguf \
  --local-dir models/Qwen3-Omni-30B-A3B-Instruct-GGUF
docker compose up -d --build
curl http://localhost:1987/health
```

Set a real `API_KEY` in `.env`. Then test it:

```bash
curl http://localhost:1987/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer YOUR_API_KEY' \
  -d '{"model":"gpu-Qwen3-Omni-30B-A3B-Instruct-Q4_K_M.gguf","messages":[{"role":"user","content":"Say hello."}],"max_tokens":64}'
```

## Using Q4, Q5, Q6, or Q8

The Docker package is model-agnostic: it serves the GGUF file named by
`MODEL_FILE`. Download a compatible GGUF quantization, put it under `models/`,
then update `.env` and recreate the backend.

| Quantization | Typical trade-off |
|---|---|
| Q4_K_M | Recommended default: quality, size, and bandwidth balance |
| Q5_K_M / Q6_K | Higher quality and memory use; lower speed than Q4 |
| Q8_0 | Highest local quant quality; substantially more memory bandwidth |

```dotenv
# Example: choose the Q5 file after downloading it.
MODEL_FILE=/models/your-model/your-model-Q5_K_M.gguf
# Leave MMPROJ_FILE empty for text-only models.
MMPROJ_FILE=
```

```bash
docker compose up -d --force-recreate backend
```

Use a projector matching the selected model whenever vision support is needed.
Q4/Q5/Q6/Q8 are weight quantizations, not Docker image variants.

## API and operations

The gateway exposes `http://HOST:1987/v1`. Prefix the model ID with `gpu-` so
the gateway sends it to Vulkan. Streaming works by adding `"stream": true`.

```bash
docker compose logs -f backend
docker compose ps
docker compose down
```

`LLAMA_CTX` is shared across `LLAMA_NP` parallel slots. For long documents,
reduce `LLAMA_NP` before increasing context. Keep `LLAMA_FLASH_ATTN=0` unless
you benchmark it on your own Vulkan driver.
