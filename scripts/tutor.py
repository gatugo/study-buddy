import os
from dotenv import load_dotenv
import google.generativeai as genai
import ollama

load_dotenv() # Load API Key from .env

GEMINI_KEY = os.getenv("GEMINI_API_KEY") 
SYSTEM_PROMPT_PATH = "TUTOR_PROMPT.md"

class HybridTutor:
    def __init__(self):
        self.mode = "local"
        self.history = []
        self.system_prompt = self.load_system_prompt()
        self.gemini_chat = None

    def load_system_prompt(self):
        if os.path.exists(SYSTEM_PROMPT_PATH):
            with open(SYSTEM_PROMPT_PATH, "r") as f: return f.read()
        return "You are a helpful coding tutor."

    def setup_gemini(self):
        if not GEMINI_KEY or "PASTE_YOUR_KEY" in GEMINI_KEY:
            print("⚠️ Error: GEMINI_API_KEY missing in .env file.")
            return False
        try:
            genai.configure(api_key=GEMINI_KEY)
            # Use Flash for higher rate limits (Free Tier Friendly)
            self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
            self.gemini_chat = self.gemini_model.start_chat(history=[])
            return True
        except Exception as e:
            print(f"❌ Connection Error: {e}")
            return False

    def chat_local(self, user_input):
        messages = [{'role': 'system', 'content': self.system_prompt}] + self.history
        messages.append({'role': 'user', 'content': user_input})
        print("\n🧠 (Local Llama 3.1) Thinking...", end="", flush=True)
        response = ollama.chat(model='llama3.1', messages=messages)
        return response['message']['content']

    def chat_cloud(self, user_input):
        print("\n☁️ (Cloud Gemini Flash) Thinking...", end="", flush=True)
        full_prompt = f"{self.system_prompt}\n\nUSER QUESTION: {user_input}"
        response = self.gemini_chat.send_message(full_prompt)
        return response.text

    def start(self):
        print("🤖 Antigravity Tutor (Hybrid Engine)")
        choice = input("Select Brain: [1] Google Gemini (Cloud)  [2] Llama-3.1 (Local): ")
        if choice == '1':
            if self.setup_gemini():
                self.mode = "cloud"
                print("✅ Connected to Cloud.")
            else:
                self.mode = "local"
                print("⚠️ Fallback to Local.")
        else:
            self.mode = "local"
            print("✅ Connected to Local.")

        print("\n💡 Type 'quit' to exit, 'switch' to change brains, 'RESCUE' for help.")
        
        while True:
            user_input = input("\nYou: ")
            if user_input.lower() in ['quit', 'exit']: break
            if user_input.lower() == 'switch':
                self.mode = "local" if self.mode == "cloud" else "cloud"
                print(f"🔄 Switched to {self.mode.upper()} mode.")
                continue

            try:
                if self.mode == "cloud": response = self.chat_cloud(user_input)
                else: response = self.chat_local(user_input)
                
                print(f"\nTutor: {response}")
                self.history.append({'role': 'user', 'content': user_input})
                self.history.append({'role': 'assistant', 'content': response})

            except Exception as e: print(f"❌ Error: {e}")

if __name__ == "__main__":
    app = HybridTutor()
    app.start()
