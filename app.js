const recordBtn = document.getElementById('recordBtn');
const translateBtn = document.getElementById('translateBtn');
const inputText = document.getElementById('inputText');
const outputDiv = document.getElementById('output');
const languageSelect = document.getElementById('languageSelect');

let recognition = null;
let isRecording = false;

// Language mapping for speech recognition
const languageMapping = {
    'hi': 'hi-IN',
    'bn': 'bn-IN',
    'te': 'te-IN',
    'ta': 'ta-IN',
    'mr': 'mr-IN',
    'gu': 'gu-IN',
    'kn': 'kn-IN',
    'ml': 'ml-IN',
    'pa': 'pa-IN',
    'ur': 'ur-IN',
    'en': 'en-IN'  // Added English language mapping
};

function initializeSpeechRecognition(lang = 'en-IN') { // Set to 'en-IN' for initial English recognition
    if ('webkitSpeechRecognition' in window) {
        recognition = new webkitSpeechRecognition();
        recognition.continuous = true;
        recognition.interimResults = true;
        recognition.lang = lang;

        recognition.onstart = function() {
            isRecording = true;
            recordBtn.textContent = 'Stop Recording';
            recordBtn.style.backgroundColor = '#ff4444';
        };

        recognition.onresult = function(event) {
            let finalTranscript = '';
            for (let i = event.resultIndex; i < event.results.length; i++) {
                const transcript = event.results[i][0].transcript;
                if (event.results[i].isFinal) {
                    finalTranscript += transcript + ' ';
                }
            }
            if (finalTranscript !== '') {
                inputText.value = finalTranscript;
                detectLanguage(finalTranscript);
            }
        };

        recognition.onerror = function(event) {
            console.error('Error:', event.error);
            stopRecording();
        };

        recognition.onend = function() {
            stopRecording();
        };
    }
}

function detectLanguage(text) {
    fetch('http://127.0.0.1:5000/detect', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: text })
    })
    .then(response => response.json())
    .then(data => {
        if (data.detected_language) {
            const detectedLang = data.detected_language;
            console.log('Detected language:', detectedLang);
            
            // Update recognition language if it's different
            if (recognition && languageMapping[detectedLang]) {
                recognition.lang = languageMapping[detectedLang];
            }
        }
    })
    .catch(error => console.error('Language detection error:', error));
}

function stopRecording() {
    isRecording = false;
    recordBtn.textContent = 'Start Recording';
    recordBtn.style.backgroundColor = '#4CAF50';
    if (recognition) {
        recognition.stop();
    }
}

// Record button click handler
recordBtn.addEventListener('click', function() {
    if (!recognition) {
        initializeSpeechRecognition();
    }
    
    if (isRecording) {
        stopRecording();
    } else {
        recognition.start();
    }
});

// Input text change handler
inputText.addEventListener('input', function() {
    if (inputText.value.trim()) {
        detectLanguage(inputText.value);
    }
});

// Translate button click handler
translateBtn.addEventListener('click', function() {
    const text = inputText.value.trim();
    const targetLang = languageSelect.value;

    if (!text) {
        alert('Please speak or type some text first!');
        return;
    }

    outputDiv.textContent = 'Translating...';

    fetch('http://127.0.0.1:5000/translate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: text, target_lang: targetLang })
    })
    .then(response => response.json())
    .then(data => {
        if (data.translated_text) {
            outputDiv.textContent = `Translated Text: ${data.translated_text}`;
            
            // Speak the translated text
            const speech = new SpeechSynthesisUtterance(data.translated_text);
            speech.lang = targetLang;
            window.speechSynthesis.speak(speech);
        } else {
            outputDiv.textContent = `Error: ${data.error}`;
        }
    })
    .catch(error => {
        outputDiv.textContent = `Error: ${error.message}`;
        console.error('Translation error:', error);
    });
});

// Initialize with English
initializeSpeechRecognition('en-IN');  // Change to 'en-IN' for English initial recognition
