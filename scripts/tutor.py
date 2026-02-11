import os
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai
import ollama

load_dotenv()  # Load API Key from .env

# --- MODEL CONFIGURATION ---
# Change these to swap models without touching any other code.
LOCAL_TEXT_MODEL = "llama3.1"         # Logic Brain — text & code
LOCAL_VISION_MODEL = "qwen2.5vl:3b"  # Vision Brain — images, OCR, screenshots
CLOUD_MODEL = "gemini-1.5-flash"     # Cloud handles both text + vision natively

GEMINI_KEY = os.getenv("GEMINI_API_KEY")
SYSTEM_PROMPT_PATH = "TUTOR_PROMPT.md"


class HybridTutor:
    def __init__(self):
        self.mode = "local"
        self.history = []
        self.system_prompt = self.load_system_prompt()
        self.gemini_chat = None
        self.gemini_model = None

    def load_system_prompt(self):
        if os.path.exists(SYSTEM_PROMPT_PATH):
            with open(SYSTEM_PROMPT_PATH, "r") as f:
                return f.read()
        return "You are a helpful coding tutor."

    # ── Cloud Setup ──────────────────────────────────────────────

    def setup_gemini(self):
        if not GEMINI_KEY or "PASTE_YOUR_KEY" in GEMINI_KEY:
            print("⚠️ Error: GEMINI_API_KEY missing in .env file.")
            return False
        try:
            genai.configure(api_key=GEMINI_KEY)
            self.gemini_model = genai.GenerativeModel(CLOUD_MODEL)
            self.gemini_chat = self.gemini_model.start_chat(history=[])
            return True
        except Exception as e:
            print(f"❌ Connection Error: {e}")
            return False

    # ── Text Brains ──────────────────────────────────────────────

    def chat_local(self, user_input):
        messages = [{'role': 'system', 'content': self.system_prompt}] + self.history
        messages.append({'role': 'user', 'content': user_input})
        print(f"\n🧠 (Local {LOCAL_TEXT_MODEL}) Thinking...", end="", flush=True)
        response = ollama.chat(model=LOCAL_TEXT_MODEL, messages=messages)
        return response['message']['content']

    def chat_cloud(self, user_input):
        print(f"\n☁️ (Cloud {CLOUD_MODEL}) Thinking...", end="", flush=True)
        full_prompt = f"{self.system_prompt}\n\nUSER QUESTION: {user_input}"
        response = self.gemini_chat.send_message(full_prompt)
        return response.text

    # ── Vision Brains (Split-Brain) ──────────────────────────────

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
        response = ollama.chat(model=LOCAL_VISION_MODEL, messages=messages)
        return response['message']['content']

    def chat_vision_cloud(self, image_path, question):
        """Send image + prompt to Gemini Flash (already multimodal)."""
        abs_path = str(Path(image_path).resolve())
        if not Path(abs_path).exists():
            return f"❌ Image not found: {image_path}"

        print(f"\n☁️👁️ (Cloud {CLOUD_MODEL} Vision) Analyzing image...", end="", flush=True)
        try:
            uploaded = genai.upload_file(abs_path)
            prompt = f"{self.system_prompt}\n\nUSER QUESTION about the image: {question or 'Describe this image in detail.'}"
            response = self.gemini_model.generate_content([prompt, uploaded])
            return response.text
        except Exception as e:
            return f"❌ Cloud vision error: {e}"

    # ── Input Routing ────────────────────────────────────────────

    def parse_img_command(self, user_input):
        """Parse 'img <path> <question>' — returns (path, question) or None."""
        if not user_input.lower().startswith("img "):
            return None
        parts = user_input[4:].strip()
        if not parts:
            return None

        # Handle quoted paths: img "path with spaces.png" question
        if parts.startswith('"'):
            end_quote = parts.find('"', 1)
            if end_quote != -1:
                img_path = parts[1:end_quote]
                question = parts[end_quote + 1:].strip()
                return (img_path, question)

        # Simple split: img path.png question here
        tokens = parts.split(maxsplit=1)
        img_path = tokens[0]
        question = tokens[1] if len(tokens) > 1 else ""
        return (img_path, question)

    # ── Commands ─────────────────────────────────────────────────

    def show_models(self):
        """Print currently active models."""
        mode_label = "☁️ CLOUD" if self.mode == "cloud" else "🧠 LOCAL"
        print(f"\n┌─────────────────────────────────────")
        print(f"│ Mode:         {mode_label}")
        print(f"│ Text Brain:   {CLOUD_MODEL if self.mode == 'cloud' else LOCAL_TEXT_MODEL}")
        print(f"│ Vision Brain: {CLOUD_MODEL if self.mode == 'cloud' else LOCAL_VISION_MODEL}")
        print(f"└─────────────────────────────────────")

    def show_help(self):
        """Print available commands."""
        print("\n💡 Commands:")
        print("  (just type)           → Ask any text/code question")
        print("  img <path> <question> → Send an image to the vision brain")
        print("  RESCUE                → Get full working solution immediately")
        print("  switch                → Toggle Cloud ↔ Local mode")
        print("  models                → Show active model configuration")
        print("  help                  → Show this help")
        print("  quit                  → Exit the tutor")

    # ── Main Loop ────────────────────────────────────────────────

    def start(self):
        print("🤖 Antigravity Tutor (Split-Brain Engine)")
        print("   Text Brain  → code & reasoning")
        print("   Vision Brain → images, OCR, screenshots\n")

        choice = input("Select Brain: [1] Google Gemini (Cloud)  [2] Llama + Qwen (Local): ")
        if choice == '1':
            if self.setup_gemini():
                self.mode = "cloud"
                print(f"✅ Connected to Cloud ({CLOUD_MODEL}).")
            else:
                self.mode = "local"
                print("⚠️ Fallback to Local.")
        else:
            self.mode = "local"
            print(f"✅ Connected to Local (Text: {LOCAL_TEXT_MODEL} | Vision: {LOCAL_VISION_MODEL}).")

        self.show_help()

        while True:
            user_input = input("\nYou: ").strip()
            if not user_input:
                continue
            if user_input.lower() in ['quit', 'exit']:
                print("👋 See you next time!")
                break
            if user_input.lower() == 'switch':
                if self.mode == "local":
                    if self.setup_gemini():
                        self.mode = "cloud"
                    else:
                        print("⚠️ Could not connect to cloud. Staying local.")
                        continue
                else:
                    self.mode = "local"
                print(f"🔄 Switched to {self.mode.upper()} mode.")
                self.show_models()
                continue
            if user_input.lower() == 'models':
                self.show_models()
                continue
            if user_input.lower() == 'help':
                self.show_help()
                continue

            try:
                # ── Vision routing ──
                img_cmd = self.parse_img_command(user_input)
                if img_cmd:
                    img_path, question = img_cmd
                    if self.mode == "cloud":
                        response = self.chat_vision_cloud(img_path, question)
                    else:
                        response = self.chat_vision_local(img_path, question)
                else:
                    # ── Text routing ──
                    if self.mode == "cloud":
                        response = self.chat_cloud(user_input)
                    else:
                        response = self.chat_local(user_input)

                print(f"\nTutor: {response}")
                self.history.append({'role': 'user', 'content': user_input})
                self.history.append({'role': 'assistant', 'content': response})

            except Exception as e:
                print(f"❌ Error: {e}")


if __name__ == "__main__":
    app = HybridTutor()
    app.start()
