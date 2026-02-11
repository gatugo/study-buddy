import os
import sys
import time
from pathlib import Path
from dotenv import load_dotenv
from google import genai
import ollama

load_dotenv()  # Load API Key from .env

# --- MODEL CONFIGURATION ---
LOCAL_TEXT_MODEL = "llama3.1"         # Logic Brain — text & code
LOCAL_VISION_MODEL = "moondream"     # Vision Brain — fastest local (~0.60 t/s)
CLOUD_MODEL = "gemini-2.0-flash"     # Cloud handles both text + vision natively

GEMINI_KEY = os.getenv("GEMINI_API_KEY")
SYSTEM_PROMPT_PATH = "TUTOR_PROMPT.md"
WORK_DIR = Path("01_active_lab")

# File type categories
CODE_EXTS = {'.js', '.py', '.html', '.css', '.ts', '.jsx', '.tsx', '.json', '.xml'}
TEXT_EXTS = {'.md', '.txt', '.csv', '.log'}
IMAGE_EXTS = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp', '.svg'}

# Try importing PyMuPDF for PDF reading
try:
    import fitz
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False


class HybridTutor:
    def __init__(self):
        self.mode = "local"
        self.history = []
        self.system_prompt = self.load_system_prompt()
        self.gemini_client = None
        self.gemini_chat = None
        # Explicit localhost to avoid OLLAMA_HOST=0.0.0.0 connection issues
        self.ollama_client = ollama.Client(host='http://localhost:11434')

        # Auto-discover workspace and inject into system prompt
        workspace_map = self.build_workspace_map()
        if workspace_map:
            self.system_prompt += f"\n\n**🗺️ WORKSPACE MAP (auto-discovered):**\n```\n{workspace_map}\n```"

    def load_system_prompt(self):
        if os.path.exists(SYSTEM_PROMPT_PATH):
            with open(SYSTEM_PROMPT_PATH, "r", encoding="utf-8") as f:
                return f.read()
        return "You are a helpful coding tutor."

    def build_workspace_map(self):
        """Scan 01_active_lab/ and build a tree map for the AI."""
        if not WORK_DIR.exists():
            return ""

        lines = []
        for item in sorted(WORK_DIR.iterdir()):
            if item.name.startswith(".") or not item.is_dir():
                continue
            lines.append(f"📂 {item.name}/")
            # Show 2 levels deep
            for child in sorted(item.iterdir()):
                if child.name.startswith("."):
                    continue
                if child.is_dir():
                    lines.append(f"    📂 {child.name}/")
                    for grandchild in sorted(child.iterdir()):
                        if grandchild.name.startswith("."):
                            continue
                        if grandchild.is_dir():
                            file_count = sum(1 for _ in grandchild.rglob("*") if _.is_file())
                            lines.append(f"        📂 {grandchild.name}/ ({file_count} files)")
                        else:
                            lines.append(f"        📄 {grandchild.name}")
                else:
                    lines.append(f"    📄 {child.name}")

        return "\n".join(lines) if lines else ""

    # ── Cloud Setup ──────────────────────────────────────────────

    def setup_gemini(self):
        if not GEMINI_KEY or "PASTE_YOUR_KEY" in GEMINI_KEY:
            print("⚠️ Error: GEMINI_API_KEY missing in .env file.")
            return False
        try:
            self.gemini_client = genai.Client(api_key=GEMINI_KEY)
            self.gemini_chat = self.gemini_client.chats.create(
                model=CLOUD_MODEL,
                config={"system_instruction": self.system_prompt}
            )
            return True
        except Exception as e:
            print(f"❌ Connection Error: {e}")
            return False

    # ── Text Brains ──────────────────────────────────────────────

    def chat_local(self, user_input):
        messages = [{'role': 'system', 'content': self.system_prompt}] + self.history
        messages.append({'role': 'user', 'content': user_input})
        print(f"\n🧠 (Local {LOCAL_TEXT_MODEL}) Thinking...", end="", flush=True)
        response = self.ollama_client.chat(model=LOCAL_TEXT_MODEL, messages=messages)
        return response['message']['content']

    def chat_cloud(self, user_input):
        print(f"\n☁️ (Cloud {CLOUD_MODEL}) Thinking...", end="", flush=True)
        response = self.gemini_chat.send_message(user_input)
        return response.text

    # ── Vision Brains ────────────────────────────────────────────

    def chat_vision_local(self, image_path, question):
        """Send image + prompt to the local vision model via Ollama."""
        abs_path = str(Path(image_path).resolve())
        if not Path(abs_path).exists():
            return f"❌ Image not found: {image_path}"

        print(f"\n👁️ (Local {LOCAL_VISION_MODEL}) Analyzing image...", end="", flush=True)
        messages = [
            {
                'role': 'user',
                'content': question or "Describe this image in detail.",
                'images': [abs_path],
            }
        ]
        response = self.ollama_client.chat(model=LOCAL_VISION_MODEL, messages=messages)
        return response['message']['content']

    def chat_vision_cloud(self, image_path, question):
        """Send image + prompt to Gemini Flash (already multimodal)."""
        abs_path = str(Path(image_path).resolve())
        if not Path(abs_path).exists():
            return f"❌ Image not found: {image_path}"

        print(f"\n☁️👁️ (Cloud {CLOUD_MODEL} Vision) Analyzing image...", end="", flush=True)
        try:
            uploaded = self.gemini_client.files.upload(file=abs_path)
            prompt = f"USER QUESTION about the image: {question or 'Describe this image in detail.'}"
            response = self.gemini_client.models.generate_content(
                model=CLOUD_MODEL,
                contents=[prompt, uploaded]
            )
            return response.text
        except Exception as e:
            return f"❌ Cloud vision error: {e}"

    # ── Smart File Reader ────────────────────────────────────────

    def read_file(self, file_path):
        """Smart file reader — picks the right tool based on extension."""
        path = Path(file_path)
        if not path.exists():
            # Try relative to work dir
            path = WORK_DIR / file_path
        if not path.exists():
            return f"❌ File not found: {file_path}"

        ext = path.suffix.lower()

        # PDF → PyMuPDF instant extraction
        if ext == '.pdf':
            if not PYMUPDF_AVAILABLE:
                return "❌ PyMuPDF not installed. Run: py -m pip install PyMuPDF"
            print(f"\n📄 Reading PDF with PyMuPDF...", end="", flush=True)
            try:
                doc = fitz.open(str(path))
                text = ""
                for page in doc:
                    text += page.get_text() + "\n"
                doc.close()
                if not text.strip():
                    return "⚠️ PDF appears to be scanned (no extractable text). Use `img` command to send pages as images."
                return f"📄 **{path.name}** ({len(text)} chars):\n\n{text[:8000]}"
            except Exception as e:
                return f"❌ PDF read error: {e}"

        # Images → route to vision brain
        if ext in IMAGE_EXTS:
            return None  # Signal to caller: use vision routing instead

        # Code files → direct read
        if ext in CODE_EXTS:
            print(f"\n💻 Reading code file...", end="", flush=True)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                return f"💻 **{path.name}** ({len(content.splitlines())} lines):\n\n```{ext[1:]}\n{content}\n```"
            except Exception as e:
                return f"❌ Read error: {e}"

        # Text/markdown → direct read
        if ext in TEXT_EXTS:
            print(f"\n📝 Reading text file...", end="", flush=True)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                return f"📝 **{path.name}** ({len(content.splitlines())} lines):\n\n{content[:8000]}"
            except Exception as e:
                return f"❌ Read error: {e}"

        return f"⚠️ Unknown file type: {ext}. Supported: PDF, images, code, text/markdown."

    def scan_workspace(self):
        """List all files in the active lab."""
        if not WORK_DIR.exists():
            return "⚠️ No workspace found. Run `py scripts/ingest.py` first."

        output = ["\n📂 Workspace Files:"]
        output.append("─" * 40)

        file_counts = {"code": 0, "text": 0, "image": 0, "pdf": 0, "other": 0}

        for path in sorted(WORK_DIR.rglob("*")):
            if path.is_dir() or path.name.startswith("."):
                continue
            rel = path.relative_to(WORK_DIR)
            ext = path.suffix.lower()

            if ext in CODE_EXTS:
                icon, file_counts["code"] = "💻", file_counts["code"] + 1
            elif ext in TEXT_EXTS:
                icon, file_counts["text"] = "📝", file_counts["text"] + 1
            elif ext in IMAGE_EXTS:
                icon, file_counts["image"] = "🖼️", file_counts["image"] + 1
            elif ext == '.pdf':
                icon, file_counts["pdf"] = "📄", file_counts["pdf"] + 1
            else:
                icon, file_counts["other"] = "📎", file_counts["other"] + 1

            output.append(f"  {icon} {rel}")

        output.append(f"\n{'─' * 40}")
        summary = " | ".join(f"{v} {k}" for k, v in file_counts.items() if v > 0)
        output.append(f"  Total: {summary}")
        output.append("\n💡 Use `read <path>` to load any file into the conversation.")
        return "\n".join(output)

    # ── Input Routing ────────────────────────────────────────────

    def parse_img_command(self, user_input):
        """Parse 'img <path> <question>' — returns (path, question) or None."""
        if not user_input.lower().startswith("img "):
            return None
        parts = user_input[4:].strip()
        if not parts:
            return None

        # Handle quoted paths
        if parts.startswith('"'):
            end_quote = parts.find('"', 1)
            if end_quote != -1:
                return (parts[1:end_quote], parts[end_quote + 1:].strip())

        # Smart split: find image extension
        img_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp', '.svg']
        parts_lower = parts.lower()
        for ext in img_extensions:
            idx = parts_lower.find(ext)
            if idx != -1:
                end = idx + len(ext)
                return (parts[:end], parts[end:].strip())

        # Fallback: simple split
        tokens = parts.split(maxsplit=1)
        return (tokens[0], tokens[1] if len(tokens) > 1 else "")

    def parse_read_command(self, user_input):
        """Parse 'read <path>' — returns path or None."""
        if not user_input.lower().startswith("read "):
            return None
        return user_input[5:].strip()

    # ── Commands ─────────────────────────────────────────────────

    def show_models(self):
        if self.mode == "no-ai":
            print("\n┌─────────────────────────────────────")
            print("│ Mode:         📂 FILE ONLY (No AI)")
            print("│ Available:    scan, read")
            print("└─────────────────────────────────────")
            return
        mode_label = "☁️ CLOUD" if self.mode == "cloud" else "🧠 LOCAL"
        print(f"\n┌─────────────────────────────────────")
        print(f"│ Mode:         {mode_label}")
        print(f"│ Text Brain:   {CLOUD_MODEL if self.mode == 'cloud' else LOCAL_TEXT_MODEL}")
        print(f"│ Vision Brain: {CLOUD_MODEL if self.mode == 'cloud' else LOCAL_VISION_MODEL}")
        print(f"└─────────────────────────────────────")

    def show_help(self):
        print("\n💡 Commands:")
        print("  read <path>           → Smart-read a file (PDF, code, text)")
        print("  scan                  → List all files in your workspace")
        if self.mode != "no-ai":
            print("  (just type)           → Ask any text/code question")
            print("  img <path> <question> → Send an image to the vision brain")
            print("  RESCUE                → Get full working solution immediately")
            print("  switch                → Toggle Cloud ↔ Local mode")
        else:
            print("  connect               → Connect to an AI brain")
        print("  models                → Show active model configuration")
        print("  help                  → Show this help")
        print("  quit                  → Exit the tutor")

    def format_time(self, elapsed):
        if elapsed >= 60:
            return f"{int(elapsed // 60)}m {int(elapsed % 60)}s"
        return f"{elapsed:.1f}s"

    # ── Main Loop ────────────────────────────────────────────────

    def connect_brain(self):
        """Brain selection menu — can be called at startup or via 'connect' command."""
        choice = input("Select Brain: [1] Gemini Flash (Cloud)  [2] Llama + Moondream (Local)  [3] No AI (Files Only): ")
        if choice == '1':
            if self.setup_gemini():
                self.mode = "cloud"
                print(f"✅ Connected to Cloud ({CLOUD_MODEL}).")
            else:
                self.mode = "local"
                print("⚠️ Fallback to Local.")
        elif choice == '3':
            self.mode = "no-ai"
            print("📂 File-only mode. Use 'scan' and 'read' to browse your materials.")
            print("   Type 'connect' anytime to activate an AI brain.")
        else:
            self.mode = "local"
            print(f"✅ Connected to Local (Text: {LOCAL_TEXT_MODEL} | Vision: {LOCAL_VISION_MODEL}).")

    def start(self):
        print("🤖 Antigravity Tutor (Smart Engine v2)")
        print("   Text Brain  → code & reasoning")
        print("   Vision Brain → images, OCR, screenshots")
        print("   File Reader → PDFs, code, text (instant)\n")

        self.connect_brain()

        self.show_help()

        while True:
            user_input = input("\nYou: ").strip()
            if not user_input:
                continue
            if user_input.lower() in ['quit', 'exit']:
                print("👋 See you next time!")
                break
            if user_input.lower() in ['switch', 'connect']:
                if self.mode == "no-ai":
                    self.connect_brain()
                elif self.mode == "local":
                    if self.setup_gemini():
                        self.mode = "cloud"
                    else:
                        print("⚠️ Could not connect to cloud. Staying local.")
                        continue
                else:
                    self.mode = "local"
                if self.mode not in ["no-ai"]:
                    print(f"🔄 Switched to {self.mode.upper()} mode.")
                self.show_models()
                continue
            if user_input.lower() == 'models':
                self.show_models()
                continue
            if user_input.lower() == 'help':
                self.show_help()
                continue
            if user_input.lower() == 'scan':
                print(self.scan_workspace())
                continue

            try:
                start_time = time.time()

                # ── Read command routing ──
                read_path = self.parse_read_command(user_input)
                if read_path:
                    result = self.read_file(read_path)
                    if result is None:
                        # Image file — route to vision
                        if self.mode == "no-ai":
                            response = "⚠️ AI not connected. Type 'connect' to activate a brain for image analysis."
                        elif self.mode == "cloud":
                            response = self.chat_vision_cloud(read_path, "Describe this image")
                        else:
                            response = self.chat_vision_local(read_path, "Describe this image")
                    else:
                        response = result
                        # Add AI summary if connected
                        if self.mode != "no-ai" and not response.startswith("❌") and not response.startswith("⚠️"):
                            if self.mode == "cloud":
                                ai_response = self.chat_cloud(f"I just loaded this file. Here's the content:\n\n{response}\n\nGive me a brief summary of what this file does.")
                            else:
                                ai_response = self.chat_local(f"I just loaded this file. Here's the content:\n\n{response}\n\nGive me a brief summary of what this file does.")
                            response = f"{response}\n\n{'─' * 40}\n🤖 AI Summary:\n{ai_response}"

                # ── Vision routing ──
                elif self.parse_img_command(user_input):
                    if self.mode == "no-ai":
                        response = "⚠️ AI not connected. Type 'connect' to activate a brain for image analysis."
                    else:
                        img_path, question = self.parse_img_command(user_input)
                        if self.mode == "cloud":
                            response = self.chat_vision_cloud(img_path, question)
                        else:
                            response = self.chat_vision_local(img_path, question)

                # ── Text routing ──
                else:
                    if self.mode == "no-ai":
                        response = "⚠️ AI not connected. Type 'connect' to activate a brain, or use 'read' and 'scan' to browse files."
                    elif self.mode == "cloud":
                        response = self.chat_cloud(user_input)
                    else:
                        response = self.chat_local(user_input)

                elapsed = time.time() - start_time
                print(f" done ({self.format_time(elapsed)})")
                print(f"\nTutor: {response}")
                self.history.append({'role': 'user', 'content': user_input})
                self.history.append({'role': 'assistant', 'content': response})

            except Exception as e:
                print(f"❌ Error: {e}")


if __name__ == "__main__":
    app = HybridTutor()
    app.start()
