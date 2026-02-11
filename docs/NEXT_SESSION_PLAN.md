# 🚀 Study Buddy AI — Next Session Action Plan

> **Date:** Feb 11, 2026
> **Status:** Ready to launch. All code is written and dependencies installed.

---

## ✅ Already Done (Today)

- [x] Project scaffold created (all 7 files)
- [x] `py -m pip install -r requirements.txt` — all dependencies installed
- [x] `.env` configured with Gemini API key
- [x] Git repo initialized with initial commit
- [x] `docs/SPLIT_BRAIN_ROADMAP.md` saved for future vision model work (Phase 2+)

---

## 🎯 Tomorrow's Steps (In Order)

### Step 1: Feed the System

Drop your **Class 29 materials** into the `00_inbox/` folder:

| Material | What to do |
|---|---|
| 📦 `class29-materials.zip` | Drop the zip directly into `00_inbox/` |
| 📂 `class29-materials/` folder | Or drop the unzipped folder into `00_inbox/` |
| 📄 Any PDF readings | Drop into `00_inbox/` — auto-converts to markdown |
| 📝 Any `.md` notes | Drop into `00_inbox/` — auto-moves to context folder |

### Step 2: Run the Ingest Pipeline

```bash
py scripts/ingest.py
```

**What happens:**
- Zips get extracted into `01_active_lab/`
- PDFs get converted to markdown in `01_active_lab/00_readings_and_context/`
- Folders get moved into `01_active_lab/`
- You'll see a tree printout of your organized workspace

**Verify:** Check that `01_active_lab/` contains your badge folders:
```
01_active_lab/
├── class29-materials/
│   ├── boulder-badge/
│   ├── cascade-badge/
│   ├── rainbow-badge/
│   └── thunder-badge/
└── 00_readings_and_context/
```

### Step 3: Launch the Tutor

```bash
py scripts/tutor.py
```

Choose your brain:
- **Option 1** → Gemini Flash (cloud, fast, uses API key)
- **Option 2** → Llama 3.1 (local, free, requires [Ollama](https://ollama.com) running)

### Step 4: Use the TUTOR_PROMPT Commands

| Command | What it does |
|---|---|
| Just type a question | Ask about any badge assignment |
| `RESCUE` | Stops Socratic mode → gives full working solution with comments |
| `switch` | Toggles between Cloud ↔ Local brain |
| `quit` | Exits the tutor |

**Remember the Badge Constraints:**
- 🟡 `thunder-badge` → Must use **Classes** (OOP)
- 🌈 `rainbow-badge` → Must use **Async/Await**

---

## 🔮 Future Phases (Not Tomorrow)

- **Phase 2:** Split-Brain Vision (see `docs/SPLIT_BRAIN_ROADMAP.md`)
- **Phase 3:** YouTube transcript ingestion via `links.txt`
- **Phase 4:** Knowledge base search across all ingested materials

---

## ⚠️ Prerequisites Checklist

- [ ] **Gemini API key** (if using Cloud mode): Already in `.env` ✅
- [ ] **Class 29 materials** ready to drop into `00_inbox/`

---

## 📥 Step 0: Download Local Models (Do This First)

> Run these **before** Step 1. Downloads can be large — do them on good Wi-Fi.

### Install Ollama

If you don't have Ollama yet:

1. Download from [ollama.com](https://ollama.com)
2. Run the installer
3. Verify it's running: `ollama --version`

### Pull the Text Brain (Required for Local Mode)

```bash
ollama pull llama3.1
```

| Detail | Value |
|---|---|
| Model | Llama 3.1 8B (quantized) |
| Size | ~4.7 GB download |
| Use | All text/code questions in the tutor |

### Pull a Vision Model (Split-Brain — Phase 2)

> Pick **one** to start. You can always pull more later.

```bash
# ⭐ Recommended: Best balance for dev work on CPU
ollama pull qwen2.5vl:3b
```

#### All Vision Model Options

| Model | Pull Command | RAM | Speed (tok/s) | Best For |
|---|---|---|---|---|
| **Qwen2.5-VL 3B** ⭐ | `ollama pull qwen2.5vl:3b` | ~4 GB | ~0.45 | OCR, doc reading, general utility |
| Moondream 2 | `ollama pull moondream` | ~2.5 GB | ~0.60 | Object detection, quick captions |
| Llama 3.2 Vision 1B | `ollama pull llama3.2-vision:1b` | ~1.5 GB | ~0.80 | Basic classification, ultra-low latency |
| Llama 3.2 Vision 11B | `ollama pull llama3.2-vision:11b` | ~10 GB | ~0.15 | Complex reasoning, highest accuracy |
| LLaVA 7B | `ollama pull llava` | ~5 GB | ~0.30 | Strong VQA, well-tested |

> **Tip:** Qwen2.5-VL 3B is recommended — small enough for your i9, smart enough for OCR and screenshots.

### Verify Your Models

```bash
ollama list
```

You should see at minimum:
```
NAME              SIZE
llama3.1:latest   4.7 GB
llava:latest      4.7 GB   ← optional for now
```

---

## 📸 Gemini Image-to-Text Capabilities

> Gemini can read and extract text from images you upload to the chat.

| Capability | Details |
|---|---|
| **Handwriting** | Reads handwritten notes (as long as they are reasonably legible) and types them out |
| **Printed Text** | Extracts text from screenshots, photos of documents, or PDF pages |
| **Translation** | Translates text in images directly from other languages |
| **Formatting** | Preserves basic structure like lists or tables |

**How to use:** Click the **Upload** button (usually a plus sign or image icon) and attach your image. Gemini will convert it to text immediately.
