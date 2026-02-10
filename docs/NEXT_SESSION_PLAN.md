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

- [ ] **Ollama running** (if using Local mode): Download from [ollama.com](https://ollama.com), then `ollama pull llama3.1`
- [ ] **Gemini API key** (if using Cloud mode): Already in `.env` ✅
- [ ] **Class 29 materials** ready to drop into `00_inbox/`
