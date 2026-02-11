import os
import shutil
import time
import zipfile
from pathlib import Path

# --- CONFIGURATION ---
BASE_DIR = Path(__file__).parent.parent
INBOX_DIR = BASE_DIR / "00_inbox"
WORK_DIR = BASE_DIR / "01_active_lab"
CONTEXT_DIR = WORK_DIR / "00_readings_and_context"
IMAGES_DIR = CONTEXT_DIR / "images"

# Try importing tools, fail gracefully if missing
try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    print("⚠️ PyMuPDF missing. Run: py -m pip install PyMuPDF")
    PYMUPDF_AVAILABLE = False

try:
    from youtube_transcript_api import YouTubeTranscriptApi
    YT_AVAILABLE = True
except ImportError:
    YT_AVAILABLE = False


def setup_environment():
    for folder in [INBOX_DIR, WORK_DIR, CONTEXT_DIR, IMAGES_DIR]:
        folder.mkdir(parents=True, exist_ok=True)


def print_tree(directory, prefix=""):
    print(f"{prefix}📂 {directory.name}/")
    prefix += "    "
    for item in sorted(directory.iterdir()):
        if item.name.startswith(".") or "__MACOSX" in item.name:
            continue
        if item.is_dir():
            print_tree(item, prefix)
        else:
            size_kb = item.stat().st_size / 1024
            print(f"{prefix}📄 {item.name} ({size_kb:.0f} KB)")


# ── File Handlers ────────────────────────────────────────────────

def extract_zip(item):
    """Extract zip/rar archives into the work directory."""
    print(f"  📦 Extracting: {item.name}")
    target_folder = WORK_DIR / item.stem
    target_folder.mkdir(exist_ok=True)
    try:
        with zipfile.ZipFile(item, 'r') as zip_ref:
            zip_ref.extractall(target_folder)
        item.unlink()
        return True
    except Exception as e:
        print(f"  ❌ Zip Error: {e}")
        return False


def extract_pdf(item):
    """Extract text + images from PDF using PyMuPDF. Zero AI needed."""
    if not PYMUPDF_AVAILABLE:
        print(f"  ⚠️ Skipping PDF (PyMuPDF not installed): {item.name}")
        shutil.move(str(item), str(CONTEXT_DIR / item.name))
        return False

    print(f"  📄 Processing PDF: {item.name}")
    start = time.time()

    try:
        doc = fitz.open(str(item))
        pages_text = []
        img_count = 0

        for page_num, page in enumerate(doc):
            # Extract text
            text = page.get_text()
            if text.strip():
                pages_text.append(f"## Page {page_num + 1}\n\n{text}")

            # Extract embedded images
            for img_idx, img in enumerate(page.get_images(full=True)):
                xref = img[0]
                try:
                    pix = fitz.Pixmap(doc, xref)
                    if pix.n > 4:  # CMYK → RGB
                        pix = fitz.Pixmap(fitz.csRGB, pix)
                    img_name = f"{item.stem}_p{page_num + 1}_img{img_idx + 1}.png"
                    pix.save(str(IMAGES_DIR / img_name))
                    img_count += 1
                except Exception:
                    pass  # Skip problematic images

        doc.close()

        # Save extracted text as markdown
        if pages_text:
            md_content = f"# {item.stem}\n\n" + "\n\n---\n\n".join(pages_text)
            md_path = CONTEXT_DIR / (item.stem + ".md")
            with open(md_path, "w", encoding="utf-8") as f:
                f.write(md_content)

        elapsed = time.time() - start
        text_status = f"{len(pages_text)} pages" if pages_text else "⚠️ scanned (no text)"
        print(f"    ✅ {text_status}, {img_count} images ({elapsed:.1f}s)")

        item.unlink()
        return True

    except Exception as e:
        print(f"  ❌ PDF Error: {e}")
        shutil.move(str(item), str(CONTEXT_DIR / item.name))
        return False


def move_folder(item):
    """Move folder into work directory."""
    print(f"  📂 Migrating: {item.name}")
    dest_path = WORK_DIR / item.name
    if dest_path.exists():
        shutil.rmtree(dest_path)
    shutil.move(str(item), str(dest_path))
    return True


def move_image(item):
    """Copy image files to context/images folder."""
    print(f"  🖼️ Image: {item.name}")
    shutil.copy2(str(item), str(IMAGES_DIR / item.name))
    item.unlink()
    return True


def move_text(item):
    """Move markdown/text files to context folder."""
    print(f"  📝 Text: {item.name}")
    shutil.move(str(item), str(CONTEXT_DIR / item.name))
    return True


# ── Main Pipeline ────────────────────────────────────────────────

IMAGE_EXTS = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp', '.svg'}
TEXT_EXTS = {'.md', '.txt'}
ARCHIVE_EXTS = {'.zip', '.rar'}

def ingest_materials():
    print("🚀 Study Buddy Ingest Pipeline (v6.0 — Smart Processing)")
    print("─" * 50)

    items = [i for i in INBOX_DIR.iterdir()
             if not i.name.startswith(".") and "__MACOSX" not in i.name]

    if not items:
        print("⚠️ Inbox empty. Drop materials into /00_inbox")
        return

    stats = {"processed": 0, "skipped": 0}
    start_time = time.time()

    for item in items:
        if item.is_dir():
            if move_folder(item): stats["processed"] += 1
        elif item.suffix.lower() in ARCHIVE_EXTS:
            if extract_zip(item): stats["processed"] += 1
        elif item.suffix.lower() == '.pdf':
            if extract_pdf(item): stats["processed"] += 1
        elif item.suffix.lower() in IMAGE_EXTS:
            if move_image(item): stats["processed"] += 1
        elif item.suffix.lower() in TEXT_EXTS:
            if move_text(item): stats["processed"] += 1
        else:
            print(f"  ⏭️ Skipping: {item.name}")
            stats["skipped"] += 1

    elapsed = time.time() - start_time
    print(f"\n{'─' * 50}")
    print(f"✅ Done! {stats['processed']} processed, {stats['skipped']} skipped ({elapsed:.1f}s)")
    print(f"\n📂 Current Workspace:")
    print_tree(WORK_DIR)


if __name__ == "__main__":
    setup_environment()
    ingest_materials()
