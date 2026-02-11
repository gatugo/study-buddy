# 🧠 Split-Brain Strategy — Future Roadmap

> **Status:** 🔮 Planned (Phase 2+) — Not yet implemented.
> This doc captures the architecture for when we're ready to add vision capabilities.

## Concept

A **Split-Brain Router** that sends inputs to the right model:

| Input Type | Brain | Model |
|---|---|---|
| Text / Code | Logic Brain | Llama 3.1 (local) or Gemini Flash (cloud) |
| Images | Vision Brain | LLaVA 7B or Llama 3.2 Vision (local) or Gemini Flash (cloud) |

## Why Split?

- Don't waste the "expensive" vision brain on simple text tasks
- Use the smallest viable model for each job → faster responses on CPU
- Cloud Gemini Flash handles both natively, so this mainly optimizes the **local** path

## Recommended Vision Models (CPU-Friendly)

| Model | Ollama Pull | RAM | Speed (tok/s) | Best For |
|---|---|---|---|---|
| **Qwen2.5-VL 3B** ⭐ | `ollama pull qwen2.5vl:3b` | ~4 GB | ~0.45 | OCR, doc reading, general utility — **recommended** |
| Moondream 2 | `ollama pull moondream` | ~2.5 GB | ~0.60 | Object detection, quick captions |
| Llama 3.2 Vision 1B | `ollama pull llama3.2-vision:1b` | ~1.5 GB | ~0.80 | Basic classification, ultra-low latency |
| Llama 3.2 Vision 11B | `ollama pull llama3.2-vision:11b` | ~10 GB | ~0.15 | Complex reasoning, highest accuracy |
| LLaVA 7B | `ollama pull llava` | ~5 GB | ~0.30 | Strong VQA, well-tested |

## Implementation Notes

- **Ollama route** (easiest): `ollama pull llava` → use `ollama.chat()` with `images` param
- **llama.cpp route** (more control): download GGUF, run `./main -m model.gguf --image img.jpg`
- **User input:** type `img path/to/image.png <question>` to trigger vision mode
- **Cloud mode:** Gemini Flash is already multimodal, no split needed

## Quick Start (When Ready)

```bash
# Pull the vision model via Ollama
ollama pull llava

# Or for a smaller model
ollama pull llava:7b-v1.5-q4_0
```

Then update `scripts/tutor.py` to add vision routing and the `img` command.
