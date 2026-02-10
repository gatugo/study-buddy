import os
import shutil
import zipfile
from pathlib import Path

# --- CONFIGURATION ---
BASE_DIR = Path(__file__).parent.parent
INBOX_DIR = BASE_DIR / "00_inbox"
WORK_DIR = BASE_DIR / "01_active_lab"
CONTEXT_DIR = WORK_DIR / "00_readings_and_context"

# Try importing power tools, fail gracefully if missing
try:
    from markitdown import MarkItDown
    from youtube_transcript_api import YouTubeTranscriptApi
    TOOLS_AVAILABLE = True
except ImportError:
    print("⚠️ Power Tools missing. Install requirements.txt")
    TOOLS_AVAILABLE = False

def setup_environment():
    for folder in [INBOX_DIR, WORK_DIR, CONTEXT_DIR]:
        folder.mkdir(parents=True, exist_ok=True)

def print_tree(directory, prefix=""):
    print(f"{prefix}📂 {directory.name}/")
    prefix += "    "
    for item in directory.iterdir():
        if item.name.startswith(".") or "__MACOSX" in item.name: continue
        if item.is_dir():
            print_tree(item, prefix)
        else:
            print(f"{prefix}📄 {item.name}")

def extract_recursive(item):
    print(f"📦 Extracting Archive: {item.name}")
    target_folder = WORK_DIR / item.stem
    target_folder.mkdir(exist_ok=True)
    try:
        with zipfile.ZipFile(item, 'r') as zip_ref:
            zip_ref.extractall(target_folder)
        item.unlink()
    except Exception as e:
        print(f"❌ Zip Error: {e}")

def move_folder_recursive(item):
    print(f"📂 Migrating Project Tree: {item.name}")
    dest_path = WORK_DIR / item.name
    if dest_path.exists(): shutil.rmtree(dest_path)
    shutil.move(str(item), str(dest_path))

def ingest_materials():
    print("🚀 Running Ultimate Ingest Pipeline (v5.1)...")
    items = list(INBOX_DIR.iterdir())
    if not items:
        print("⚠️ Inbox empty. Drop 'class29-materials' folder in /00_inbox")
        return

    for item in items:
        if item.name.startswith(".") or "__MACOSX" in item.name:
            if item.is_dir(): shutil.rmtree(item)
            continue

        if item.suffix in ['.zip', '.rar']: extract_recursive(item)
        elif item.is_dir(): move_folder_recursive(item)
        elif item.suffix == '.pdf' and TOOLS_AVAILABLE:
            try:
                md = MarkItDown()
                result = md.convert(str(item))
                with open(CONTEXT_DIR / (item.stem + ".md"), "w") as f:
                    f.write(result.text_content)
                item.unlink()
            except: shutil.move(str(item), str(CONTEXT_DIR / item.name))
        elif item.suffix == '.md':
            shutil.move(str(item), str(CONTEXT_DIR / item.name))

    print("\n✅ Ingest Complete. Current Workspace:")
    print_tree(WORK_DIR)

if __name__ == "__main__":
    setup_environment()
    ingest_materials()
