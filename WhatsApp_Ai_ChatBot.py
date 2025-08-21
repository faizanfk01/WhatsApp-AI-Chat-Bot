from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from openai import OpenAI
import pyautogui
import pyperclip

# OpenAI API setup
client = OpenAI(api_key="your-api-here")

# Selenium setup
user_data_dir = r"C:/WhatsAppBotProfile"
options = webdriver.ChromeOptions()
options.add_argument(f"--user-data-dir={user_data_dir}")
options.add_argument("--profile-directory=Profile 2")
driver = webdriver.Chrome(options=options)

# open whatsapp
driver.get("https://web.whatsapp.com")
print("✅ WhatsApp Web opened")

time.sleep(10)  # wait for WhatsApp to load

# function to get last message
def get_last_message():
    script = """
        let msgs = document.querySelectorAll("div.message-in span.selectable-text");
        if (msgs.length > 0) {
            return msgs[msgs.length - 1].innerText;  // keeps emojis
        }
        return null;
    """
    return driver.execute_script(script)

# function to send a reply
def send_message(text):
    try:
        # Focus the textbox
        textbox = driver.find_element(By.CSS_SELECTOR, "div[contenteditable='true'][data-tab='10']")
        textbox.click()
        time.sleep(0.3)  # small delay

        # Copy text to clipboard
        pyperclip.copy(text)
        time.sleep(0.1)

        # Paste text with Ctrl+V
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(0.1)

        # Press Enter to send
        print("🤖 Replied:", text)
        pyautogui.press('enter')

    except Exception as e:
        print("❌ Failed to send message:", e)

conversation = [
    {"role": "system", "content": """
You are a person from Pakistan. You talk like a normal human (not an assistant).  
You are a coder. Match the vibe of the person you're chatting with:  
- If they are happy/casual → be funny, playful, and use lots of emojis.  
- If they are sad → cheer them up with supportive humor.  
- If they are serious → stay witty and lighthearted.  

Extra rules:  
- Always reply in the same language as the user (Urdu, English, mix, etc.).  
- If they use emojis, you also use emojis.  
- Keep replies short, natural, and casual (like WhatsApp chat).  
- If the person sends media (photo, sticker, voice note, doc, etc.), acknowledge it in a fun way. Example:
   - Sticker → "Sticker mast hai 😂🔥"  
   - Photo → "Wahh photo send ki! 📸🔥"  
   - Voice note → "Voice note aaya hai 🎤😂"  
   - Document → "File mil gayi 📂"  
Never say you are an AI or assistant. Always act human.
"""}
]

# function to get AI reply
def ai_reply(user_message):
    global conversation
    conversation.append({"role": "user", "content": user_message})
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=conversation
    )
    reply = response.choices[0].message.content.strip()
    conversation.append({"role": "assistant", "content": reply})
    return reply

print("🤖 Bot is running... Press CTRL+C to stop.")
last_seen = ""

while True:
    try:
        msg = get_last_message()
        if msg and msg != last_seen:  # new message detected
            print("📩 New message:", msg)
            reply = ai_reply(msg)
            send_message(reply)
            last_seen = msg
        time.sleep(3)  # check every 3 sec
    except KeyboardInterrupt:
        print("🛑 Bot stopped by user.")
        break
    except Exception as e:
        print("⚠️ Error in loop:", e)
        time.sleep(5)