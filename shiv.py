import streamlit as st
from googletrans import Translator
import pyttsx3
import speech_recognition as sr
from langdetect import detect
import pycountry
import pygame
import os
import io
from gtts import gTTS
import webbrowser

# Initialize pyttsx3 engine for speaking text
engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)  # Set to female voice

# Initialize speech recognizer and translator
recognizer = sr.Recognizer()
translator = Translator()

# Initialize pygame mixer for playing audio
pygame.mixer.init()

# Function to speak text
def speak(audio):
    engine.say(audio)
    engine.runAndWait()

# Function to detect language of input text
def detect_language(text):
    return detect(text)

# Function to get language name from language code
def get_lang_name(lang_code):
    language = pycountry.languages.get(alpha_2=lang_code)
    return language.name if language else "Unknown"

# Function to capture voice command
def take_command():
    with sr.Microphone() as source:
        st.write("Listening... Please speak now...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        st.write("Recognizing...")
        query = recognizer.recognize_google(audio, language='en-in')
        st.write(f"You said: {query}")
        return query
    except Exception as e:
        st.write("Could not recognize your speech, please try again.")
        return None

# Function to translate text
def translate_text(text, source_lang, target_lang):
    translation = translator.translate(text, src=source_lang, dest=target_lang)
    return translation.text

# Function to convert text to speech
def text_to_speech(text, language_code):
    tts = gTTS(text=text, lang=language_code)
    mp3_fp = io.BytesIO()
    tts.write_to_fp(mp3_fp)
    mp3_fp.seek(0)
    pygame.mixer.music.load(mp3_fp)
    pygame.mixer.music.play()

# Streamlit UI setup
st.title("Voice Translation App")
st.write("This app allows you to speak, translate, and hear translations in different languages.")

# Create a column for the main app and a column for the helper
col1, col2 = st.columns(2)

with col1:
    # Input method selection
    input_method = st.radio("Choose Input Method:", ("Text Input", "Speech Input"))

    # Mapping for language codes for Google Translate and gTTS
    lang_code = {
        "English": "en", "Hindi": "hi", "Tamil": "ta", "Telugu": "te", "Bengali": "bn", 
        "Marathi": "mr", "Gujarati": "gu", "Punjabi": "pa", "Malayalam": "ml", "Kannada": "kn", 
        "Odia": "or", "Urdu": "ur", "Assamese": "as", "Maithili": "mai", "Konkani": "kok",
        "Sanskrit": "sa", "Sindhi": "sd", "Nepali": "ne", "Bhojpuri": "bho", "Rajasthani": "raj",
        "Kashmiri": "ks", "Maithili": "mai", "Santali": "sat", "Kundli": "ku", "Haryanvi": "hari",
        "Hindi": "hi"
    }

    if input_method == "Text Input":
        input_text = st.text_area("Enter text to translate:")
        source_language = st.selectbox("Select Source Language:", list(lang_code.keys()))
        target_language = st.selectbox("Select Target Language:", list(lang_code.keys()))
        
        if st.button("Translate and Speak"):
            if input_text:
                source_lang_code = lang_code.get(source_language, 'en')
                target_lang_code = lang_code.get(target_language, 'en')
                translated_text = translate_text(input_text, source_lang_code, target_lang_code)
                st.write(f"Translated text: {translated_text}")
                text_to_speech(translated_text, target_lang_code)
            else:
                st.write("Please enter some text.")

    elif input_method == "Speech Input":
        source_language = st.selectbox("Select Source Language:", list(lang_code.keys()))
        target_language = st.selectbox("Select Target Language:", list(lang_code.keys()))
        
        if st.button("Start Recording"):
            spoken_text = take_command()
            if spoken_text:
                st.write(f"Original Text: {spoken_text}")
                # Detect language of spoken text
                detected_lang = detect_language(spoken_text)
                st.write(f"Detected Language: {get_lang_name(detected_lang)}")
                
                # Translate and speak the translated text
                source_lang_code = lang_code.get(source_language, 'en')
                target_lang_code = lang_code.get(target_language, 'en')
                translated_text = translate_text(spoken_text, source_lang_code, target_lang_code)
                st.write(f"Translated text: {translated_text}")
                text_to_speech(translated_text, target_lang_code)

with col2:
    # Helper button to open linked HTML page
    if st.button("Helper"):
        st.write("Opening helper HTML page...")
        webbrowser.open_new_tab('C:\\Users\\shivr\\OneDrive\\Desktop\\tireeedd\\pages\\front page\\page1.html')