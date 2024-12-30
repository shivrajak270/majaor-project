import streamlit as st
from googletrans import Translator
import pyttsx3
import speech_recognition as sr
from langdetect import detect
import pycountry
import pygame
import io
from gtts import gTTS
import webbrowser
from transformers import pipeline

# Set page config at the very beginning before any other Streamlit commands
st.set_page_config(page_title="Translation & Emotion Detection App", layout="wide")

# Initialize all components
@st.cache_resource
def load_emotion_classifier():
    return pipeline("text-classification", model="bhadresh-savani/distilbert-base-uncased-emotion")

# Initialize components with error handling
try:
    emotion_classifier = load_emotion_classifier()
    engine = pyttsx3.init('sapi5')
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[1].id)
    recognizer = sr.Recognizer()
    translator = Translator()
    pygame.mixer.init()
except Exception as e:
    st.error(f"Error initializing components: {str(e)}")
    st.stop()

# Helper functions
@st.cache_data
def speak(audio):
    try:
        engine.say(audio)
        engine.runAndWait()
    except Exception as e:
        st.error(f"Speech error: {str(e)}")

@st.cache_data
def detect_language(text):
    try:
        return detect(text)
    except:
        return "en"  # Default to English if detection fails

@st.cache_data
def get_lang_name(lang_code):
    try:
        language = pycountry.languages.get(alpha_2=lang_code)
        return language.name if language else "Unknown"
    except:
        return "Unknown"

def take_command():
    try:
        with sr.Microphone() as source:
            with st.spinner("Listening... Please speak now..."):
                recognizer.adjust_for_ambient_noise(source)
                audio = recognizer.listen(source)

        with st.spinner("Recognizing..."):
            query = recognizer.recognize_google(audio, language='en-in')
            st.info(f"You said: {query}")
            return query
    except sr.RequestError:
        st.error("Could not connect to speech recognition service")
    except sr.UnknownValueError:
        st.warning("Could not understand audio")
    except Exception as e:
        st.error(f"Error: {str(e)}")
    return None

@st.cache_data
def translate_text(text, source_lang, target_lang):
    try:
        translation = translator.translate(text, src=source_lang, dest=target_lang)
        return translation.text
    except Exception as e:
        st.error(f"Translation error: {str(e)}")
        return text

def text_to_speech(text, language_code):
    try:
        tts = gTTS(text=text, lang=language_code)
        mp3_fp = io.BytesIO()
        tts.write_to_fp(mp3_fp)
        mp3_fp.seek(0)
        pygame.mixer.music.load(mp3_fp)
        pygame.mixer.music.play()
    except Exception as e:
        st.error(f"Text-to-speech error: {str(e)}")

@st.cache_data
def detect_emotion(text):
    try:
        predictions = emotion_classifier(text)
        emotions = {item['label']: item['score'] for item in predictions}
        top_emotion = max(emotions, key=emotions.get)
        top_score = emotions[top_emotion]
        return top_emotion, top_score, emotions
    except Exception as e:
        st.error(f"Emotion detection error: {str(e)}")
        return "unknown", 0.0, {}

def display_emotion_analysis(original_text, translated_text=None):
    st.subheader("Emotion Analysis")
    
    # Original text emotions
    st.write("Original Text Emotions:")
    orig_emotion, orig_score, orig_emotions = detect_emotion(original_text)
    st.write(f"Primary Emotion: {orig_emotion.capitalize()} ({orig_score:.2%})")
    orig_emotion_data = {
        'Emotion': list(orig_emotions.keys()), 
        'Confidence': [score for score in orig_emotions.values()]
    }
    st.bar_chart(orig_emotion_data, x='Emotion', y='Confidence')
    
    # Translated text emotions (if provided)
    if translated_text:
        st.write("Translated Text Emotions:")
        trans_emotion, trans_score, trans_emotions = detect_emotion(translated_text)
        st.write(f"Primary Emotion: {trans_emotion.capitalize()} ({trans_score:.2%})")
        trans_emotion_data = {
            'Emotion': list(trans_emotions.keys()), 
            'Confidence': [score for score in trans_emotions.values()]
        }
        st.bar_chart(trans_emotion_data, x='Emotion', y='Confidence')

def handle_text_input(lang_code):
    input_text = st.text_area("Enter text to translate:", key="translate_text")
    source_language = st.selectbox("Source Language:", list(lang_code.keys()))
    target_language = st.selectbox("Target Language:", list(lang_code.keys()))
    
    if st.button("Translate and Speak"):
        if input_text:
            with st.spinner("Translating..."):
                source_lang_code = lang_code.get(source_language, 'en')
                target_lang_code = lang_code.get(target_language, 'en')
                translated_text = translate_text(input_text, source_lang_code, target_lang_code)
                st.success(f"Translated text: {translated_text}")
                text_to_speech(translated_text, target_lang_code)

                display_emotion_analysis(input_text, translated_text)
        else:
            st.warning("Please enter some text.")

def handle_speech_input(lang_code):
    source_language = st.selectbox("Source Language:", list(lang_code.keys()))
    target_language = st.selectbox("Target Language:", list(lang_code.keys()))
    
    if st.button("Start Recording"):
        spoken_text = take_command()
        if spoken_text:
            st.write(f"Original Text: {spoken_text}")
            detected_lang = detect_language(spoken_text)
            st.write(f"Detected Language: {get_lang_name(detected_lang)}")
            
            source_lang_code = lang_code.get(source_language, 'en')
            target_lang_code = lang_code.get(target_language, 'en')
            translated_text = translate_text(spoken_text, source_lang_code, target_lang_code)
            st.success(f"Translated text: {translated_text}")
            text_to_speech(translated_text, target_lang_code)

            display_emotion_analysis(spoken_text)

def handle_emotion_analysis():
    st.header("Additional Emotion Analysis")
    emotion_text = st.text_area("Enter text to analyze emotions:", key="emotion_text")
    
    if st.button("Analyze Emotions"):
        if emotion_text:
            display_emotion_analysis(emotion_text)
        else:
            st.warning("Please enter some text to analyze emotions.")
    
    # Add some spacing
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Helper section with custom styling
    st.markdown("""
        <style>
        .helper-section {
            padding: 20px;
            border-radius: 5px;
            background-color: #f0f2f6;
            margin-top: 20px;
        }
        </style>
        <div class='helper-section'>
        <h3>Need Help?</h3>
        </div>
    """, unsafe_allow_html=True)
    
    # Helper button with custom styling
    if st.button("Open Help Guide", key="helper_button", 
                 help="Click to open the help documentation"):
        try:
            st.write("Opening helper HTML page...")
            webbrowser.open_new_tab('C:\\Users\\shivr\\OneDrive\\Desktop\\tireeedd\\pages\\front page\\page1.html')
            st.success("Help guide opened in new tab!")
        except Exception as e:
            st.error(f"Error opening help guide: {str(e)}")
            st.info("Please make sure the help file exists at the specified location.")

def main():
    st.title("Voice Translation & Emotion Detection App")
    st.write("This app allows you to translate text/speech and analyze emotions.")

    # Create columns for the main layout
    col1, col2 = st.columns([2, 1])

    with col1:
        # Language codes mapping
        lang_code = {
            "English": "en", "Hindi": "hi", "Tamil": "ta", "Telugu": "te", "Bengali": "bn", 
            "Marathi": "mr", "Gujarati": "gu", "Punjabi": "pa", "Malayalam": "ml", "Kannada": "kn", 
            "Odia": "or", "Urdu": "ur", "Assamese": "as", "Maithili": "mai", "Konkani": "kok",
            "Sanskrit": "sa", "Sindhi": "sd", "Nepali": "ne", "Bhojpuri": "bho", "Rajasthani": "raj",
            "Kashmiri": "ks", "Santali": "sat", "Kundli": "ku", "Haryanvi": "hari"
        }

        # Translation Section
        st.header("Translation")
        input_method = st.radio("Choose Input Method:", ("Text Input", "Speech Input"))

        if input_method == "Text Input":
            handle_text_input(lang_code)
        else:
            handle_speech_input(lang_code)

    with col2:
        handle_emotion_analysis()

if __name__ == '__main__':
    main()