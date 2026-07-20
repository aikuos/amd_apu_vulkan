#!/bin/bash
set -euo pipefail

: "${MODEL_FILE:?Set MODEL_FILE to a GGUF path inside /models}"
if [[ ! -f "$MODEL_FILE" ]]; then
  echo "Model not found: $MODEL_FILE" >&2
  exit 1
fi

args=(
  -m "$MODEL_FILE" --host 0.0.0.0 --port 8000
  -ngl "${LLAMA_NGL:-99}" -np "${LLAMA_NP:-8}" -c "${LLAMA_CTX:-65536}"
  -t "${LLAMA_THREADS:-32}" -b "${LLAMA_BATCH:-2048}" -ub "${LLAMA_UBATCH:-512}"
  --cache-type-k "${LLAMA_CACHE_TYPE_K:-q8_0}"
  --cache-type-v "${LLAMA_CACHE_TYPE_V:-q8_0}" --kv-unified --timeout 300 --mlock --fit off
)

if [[ -n "${MMPROJ_FILE:-}" && -f "$MMPROJ_FILE" ]]; then args+=(--mmproj "$MMPROJ_FILE"); fi
if [[ "${LLAMA_FLASH_ATTN:-0}" == "1" ]]; then args+=(--flash-attn); fi

vulkaninfo --summary 2>/dev/null | grep -E 'deviceName|deviceType' | head -4 || true
exec llama-server "${args[@]}"
