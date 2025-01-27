import speech_recognition as sr

def capture_voice_input():
    """
    Capture and transcribe voice input using the SpeechRecognition library.

    Returns:
        str: Transcribed text from the user's voice input.
    """
    recognizer = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            print("Listening... Please speak into the microphone.")
            audio = recognizer.listen(source, timeout=10)  # Timeout after 10 seconds
            print("Processing voice input...")
            # Recognize speech using Google Web Speech API
            transcribed_text = recognizer.recognize_google(audio)
            print(f"Transcribed Text: {transcribed_text}")
            return transcribed_text
    except sr.WaitTimeoutError:
        print("No speech detected within the timeout period.")
        return None
    except sr.UnknownValueError:
        print("Sorry, could not understand the audio.")
        return None
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")
        return None
