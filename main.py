import os
import speech_recognition as sr
import datetime
import webbrowser
import google.generativeai as genai
from config import gemini_api_key
import pyaudio

# Configure Gemini API
genai.configure(api_key=gemini_api_key)

# --- Start of Fix ---

# It's good practice to list available models to ensure you're using a valid one.
# This step is for debugging and can be removed in production.
# for m in genai.list_models():
#     if 'generateContent' in m.supported_generation_methods:
#         print(m.name)

# Use a specific, supported model. "gemini-1.5-flash" is a good, recent choice.
model = genai.GenerativeModel("gemini-1.5-flash")

# --- End of Fix ---

# Speak function for Linux
def say(text):
    # Sanitize text to prevent shell injection issues
    sanitized_text = text.replace('"', '\\"')
    os.system(f'espeak "{sanitized_text}"')

# Get voice input from default mic
def take_command():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎤 Listening...")
        # Adjust for ambient noise to improve recognition
        r.adjust_for_ambient_noise(source)
        try:
            # Increased timeout for better listening
            audio = r.listen(source, timeout=10, phrase_time_limit=8)
            print("🔎 Recognizing...")
            query = r.recognize_google(audio, language='en-IN')
            print(f"🗣️ You said: {query}")
            return query
        except sr.WaitTimeoutError:
            print("Listening timed out. Please try again.")
            return ""
        except sr.UnknownValueError:
            print("I didn't catch that. Could you repeat?")
            return ""
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")
            say("Please check your internet connection.")
            return ""
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return ""

# Ask Gemini for a response
def chat_with_gemini(query):
    try:
        response = model.generate_content(query)
        # It's safer to access parts of the response
        if response.parts:
            answer = response.parts[0].text.strip()
        else:
            answer = "I couldn't generate a response."
        print("🤖 Gemini:", answer)
        say(answer)
        return answer
    except Exception as e:
        print("Gemini error:", e)
        say("Sorry, there was an issue with Gemini.")
        return ""

# Main logic
if __name__ == "__main__":
    print("✅ Welcome to Jarvis (Powered by Gemini)")
    say("Hello, I am Jarvis, powered by Gemini.")

    while True:
        query = take_command()
        if query:
            query = query.lower()

            if "open youtube" in query:
                webbrowser.open("https://www.youtube.com")
                say("Opening YouTube.")
            elif "open google" in query:
                webbrowser.open("https://www.google.com")
                say("Opening Google.")
            elif "open wikipedia" in query:
                webbrowser.open("https://www.wikipedia.org")
                say("Opening Wikipedia.")
            elif "what is the time" in query or "tell me the time" in query:
                now = datetime.datetime.now()
                current_time = f"The time is {now.strftime('%I:%M %p')}"
                print(current_time)
                say(current_time)
            elif "exit" in query or "quit" in query:
                say("Goodbye.")
                break
            else:
                chat_with_gemini(query)