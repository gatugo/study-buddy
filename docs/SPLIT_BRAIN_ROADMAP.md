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

| Model | Size | RAM | Token Speed (i9-10900) | Notes |
|---|---|---|---|---|
| Llama 3.2 Vision 1B (q4_0) | ~1 GB | ~1.2 GB | ~0.5-0.7 t/s | Fastest, lightest |
| Llama 3.2 Vision 3B (q4_0) | ~2.5 GB | ~2.8 GB | ~0.35-0.45 t/s | Better accuracy |
| LLaVA 1.5 7B (q4_0) | ~4 GB | ~4-5 GB | ~0.25-0.35 t/s | Strong VQA, via `ollama pull llava` |
| Llama 3.2 Vision 11B (q4_0) | ~5-6 GB | ~7-9 GB | ~0.12-0.18 t/s | Best quality, slowest on CPU |

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
