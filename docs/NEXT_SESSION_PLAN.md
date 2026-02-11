# 🚀 Study Buddy AI — Session Plan

> **Last Updated:** Feb 11, 2026
> **Status:** Core engine working. Smart file processing + auto-discovery live.

---

## ✅ Completed (Feb 11 Session)

- [x] Fixed `UnicodeDecodeError` (emoji crash) — added `encoding="utf-8"`
- [x] Migrated from deprecated `google.generativeai` to `google.genai` SDK
- [x] Fixed Gemini `files.upload()` API parameter (`file_path` → `file`)
- [x] Fixed Ollama connection (`OLLAMA_HOST=0.0.0.0` → explicit localhost)
- [x] Implemented Split-Brain Router (text + vision routing)
- [x] Upgraded ingest pipeline: PyMuPDF replaces markitdown (100x faster PDFs)
- [x] Added `read <path>` command — smart file reader (PDF, code, text)
- [x] Added `scan` command — lists all workspace files with type icons
- [x] Added `img` command — smart path parser handles spaces in filenames
- [x] Added response timer (shows elapsed time for each query)
- [x] Made TUTOR_PROMPT generic — no hardcoded class names
- [x] Auto-discovery: tutor scans `01_active_lab/` at startup, builds workspace map
- [x] Added No-AI file-only mode (option 3) with `connect` command
- [x] Switched local vision from Qwen2.5-VL to Moondream (faster: 0.60 vs 0.45 t/s)
- [x] All changes committed and pushed to GitHub

---

## 🎯 Next Session Goals

### Priority 1: Test & Polish
- [ ] Test `read` command with different file types (PDF, JS, HTML, CSS)
- [ ] Test cloud mode (Gemini Flash) — wait for rate limit reset
- [ ] Test `connect` command to upgrade from no-ai to cloud mid-session
- [ ] Test with a second class folder to verify auto-discovery

### Priority 2: Web UI (Terminal is clunky)
- [ ] Build simple local web interface (HTML + JS)
- [ ] Chat UI with markdown rendering and syntax highlighting
- [ ] File browser sidebar with click-to-load
- [ ] Drag-and-drop image support

### Priority 3: More Classes
- [ ] Drop additional class materials into `00_inbox/`
- [ ] Run `py scripts/ingest.py` to organize
- [ ] Verify tutor auto-discovers and adapts

### Priority 4: Future Phases
- [ ] YouTube transcript ingestion via `links.txt`
- [ ] Knowledge base search across all materials
- [ ] Per-class rule files (`TUTOR_RULES.md` in each folder)

---

## 🧠 Current Architecture

```
py scripts/ingest.py     ← Drop files in 00_inbox, run this to organize
py scripts/tutor.py      ← Launch the tutor

Select Brain:
  [1] Gemini Flash (Cloud) — fast, needs API key
  [2] Llama + Moondream (Local) — free, offline, slower
  [3] No AI (Files Only) — scan/read only, instant

Commands:
  scan                   → list workspace files
  read <path>            → smart-read any file (PDF, code, text)
  img <path> <question>  → send image to vision brain
  connect                → upgrade from no-ai to AI mode
  switch                 → toggle cloud ↔ local
  RESCUE                 → get full solution immediately
```

---

## 📥 Local Model Setup

```bash
ollama pull llama3.1      # Text brain (4.7 GB)
ollama pull moondream     # Vision brain (1.7 GB)
```

---

## 🔑 API Key

Gemini API key is in `.env` (gitignored). Get one at [aistudio.google.com](https://aistudio.google.com).
