import streamlit as st
import speech_recognition as sr
from googletrans import Translator
import pyttsx3
from langdetect import detect
import pycountry
import pygame
import io
from gtts import gTTS
import webbrowser
from transformers import pipeline

# Set page config
st.set_page_config(page_title="Translation & Emotion Detection App", layout="wide")

# Initialize components with proper error handling
@st.cache_resource
def initialize_components():
    components = {}
    try:
        components['emotion_classifier'] = pipeline("text-classification", 
                                                 model="bhadresh-savani/distilbert-base-uncased-emotion")
        components['engine'] = pyttsx3.init('sapi5')
        components['translator'] = Translator()
        components['recognizer'] = sr.Recognizer()
        pygame.mixer.init()
        
        # Set voice properties
        voices = components['engine'].getProperty('voices')
        components['engine'].setProperty('voice', voices[1].id)
        
        return components
    except Exception as e:
        st.error(f"Error initializing components: {str(e)}")
        return None

# Initialize components
components = initialize_components()
if not components:
    st.stop()

# Helper functions
def speak(audio, engine):
    try:
        engine.say(audio)
        engine.runAndWait()
    except Exception as e:
        st.error(f"Speech error: {str(e)}")

def detect_language(text):
    try:
        return detect(text)
    except:
        return "en"

def get_lang_name(lang_code):
    try:
        language = pycountry.languages.get(alpha_2=lang_code)
        return language.name if language else "Unknown"
    except:
        return "Unknown"

def take_command(recognizer):
    try:
        with sr.Microphone() as source:
            with st.spinner("Listening... Please speak now..."):
                recognizer.adjust_for_ambient_noise(source)
                audio = recognizer.listen(source, timeout=5)

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

def translate_text(text, source_lang, target_lang, translator):
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
        
        # Wait for the audio to finish playing
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
    except Exception as e:
        st.error(f"Text-to-speech error: {str(e)}")

def detect_emotion(text, classifier):
    try:
        predictions = classifier(text)
        emotions = {item['label']: item['score'] for item in predictions}
        top_emotion = max(emotions, key=emotions.get)
        top_score = emotions[top_emotion]
        return top_emotion, top_score, emotions
    except Exception as e:
        st.error(f"Emotion detection error: {str(e)}")
        return "unknown", 0.0, {}

def display_emotion_analysis(text, classifier, label="Text"):
    if text:
        st.write(f"{label} Emotions:")
        emotion, score, emotions = detect_emotion(text, classifier)
        st.write(f"Primary Emotion: {emotion.capitalize()} ({score:.2%})")
        
        # Create emotion data for chart
        emotion_data = {
            'Emotion': list(emotions.keys()),
            'Confidence': [score for score in emotions.values()]
        }
        st.bar_chart(emotion_data, x='Emotion', y='Confidence')

def main():
    st.title("Voice Translation & Emotion Detection App")
    st.write("This app allows you to translate text/speech and analyze emotions.")

    # Language codes mapping
    lang_code = {
        "English": "en", "Hindi": "hi", "Tamil": "ta", "Telugu": "te", "Bengali": "bn",
        "Marathi": "mr", "Gujarati": "gu", "Punjabi": "pa", "Malayalam": "ml", "Kannada": "kn",
        "Odia": "or", "Urdu": "ur", "Spanish": "es", "French": "fr", "German": "de",
        "Italian": "it", "Portuguese": "pt", "Russian": "ru", "Japanese": "ja", "Korean": "ko"
    }

    # Create columns for the main layout
    col1, col2 = st.columns([2, 1])

    with col1:
        st.header("Translation")
        input_method = st.radio("Choose Input Method:", ("Text Input", "Speech Input"))

        if input_method == "Text Input":
            input_text = st.text_area("Enter text to translate:", key="translate_text")
            source_language = st.selectbox("Source Language:", list(lang_code.keys()), key="source1")
            target_language = st.selectbox("Target Language:", list(lang_code.keys()), key="target1")

            if st.button("Translate and Speak"):
                if input_text:
                    with st.spinner("Translating..."):
                        source_lang_code = lang_code[source_language]
                        target_lang_code = lang_code[target_language]
                        translated_text = translate_text(input_text, source_lang_code, 
                                                      target_lang_code, components['translator'])
                        
                        st.success(f"Translated text: {translated_text}")
                        text_to_speech(translated_text, target_lang_code)
                        
                        # Display emotion analysis
                        st.subheader("Emotion Analysis")
                        display_emotion_analysis(input_text, components['emotion_classifier'], 
                                              "Original Text")
                        display_emotion_analysis(translated_text, components['emotion_classifier'], 
                                              "Translated Text")
                else:
                    st.warning("Please enter some text.")

        else:  # Speech Input
            source_language = st.selectbox("Source Language:", list(lang_code.keys()), key="source2")
            target_language = st.selectbox("Target Language:", list(lang_code.keys()), key="target2")

            if st.button("Start Recording"):
                spoken_text = take_command(components['recognizer'])
                if spoken_text:
                    detected_lang = detect_language(spoken_text)
                    st.write(f"Detected Language: {get_lang_name(detected_lang)}")
                    
                    source_lang_code = lang_code[source_language]
                    target_lang_code = lang_code[target_language]
                    translated_text = translate_text(spoken_text, source_lang_code, 
                                                  target_lang_code, components['translator'])
                    
                    st.success(f"Translated text: {translated_text}")
                    text_to_speech(translated_text, target_lang_code)
                    
                    # Display emotion analysis
                    st.subheader("Emotion Analysis")
                    display_emotion_analysis(spoken_text, components['emotion_classifier'], 
                                          "Original Speech")

    with col2:
        st.header("Emotion Analysis")
        emotion_text = st.text_area("Enter text to analyze emotions:", key="emotion_text")
        
        if st.button("Analyze Emotions"):
            if emotion_text:
                display_emotion_analysis(emotion_text, components['emotion_classifier'])
            else:
                st.warning("Please enter some text to analyze emotions.")
        
        # Helper section
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
        
        if st.button("Open Help Guide"):
            try:
                webbrowser.open_new_tab('C:\\Users\\shivr\\OneDrive\\Desktop\\tireeedd\\pages\\front page\\page1.html')
                st.success("Help guide opened in new tab!")
            except Exception as e:
                st.error(f"Error opening help guide: {str(e)}")
                st.info("Please make sure the help file exists at the specified location.")

if __name__ == '__main__':
    main()