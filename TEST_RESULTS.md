# Qwen3-Omni Q4 Vulkan test result

Tested on the hardware described in the README, through the gateway endpoint.

| Metric | Result |
|---|---:|
| Model | Qwen3-Omni-30B-A3B-Instruct Q4_K_M GGUF |
| Projector | Q8_0 GGUF |
| Prompt tokens | 18 |
| Generated tokens | 7 |
| Prompt processing | 147 tok/s |
| Generation | 97 tok/s |
| Generation time | 10.30 ms/token |

The test request returned `single Omni Q4 ready.` The result is for a short
warm text request; longer prompts, vision/audio input, or concurrent users
will reduce per-request throughput.
