# Agent Guide

This repository serves one GGUF model with llama.cpp + Vulkan on AMD APUs.

- Keep `BACKEND_TYPE` out of scope: this package intentionally has one Vulkan
  backend and does not include vLLM or PyTorch ROCm.
- Model files stay in `./models/` and must never be committed.
- `MODEL_FILE` is a path inside the container, so it must start with `/models/`.
- Use `LLAMA_NGL=99` for full Vulkan offload on supported GPUs.
- The Radeon 8060S / gfx1151 path is Mesa RADV Vulkan. Check backend logs for
  the detected Vulkan device after changes.
- Only one large GPU model should run at a time on this shared-memory APU.
- Prefer Q4_K_M for capacity and bandwidth balance. Q5_K_M, Q6_K, and Q8_0
  can be selected by changing `MODEL_FILE`; higher quants consume more memory.
- Do not publish `.env`, model files, or API keys.
