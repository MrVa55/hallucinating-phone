# fast_script.py
import os
import torch
import requests
from faster_whisper import WhisperModel

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

# Confirm that CUDA is running:
if torch.cuda.is_available():
    print(f"CUDA is available. Device: {torch.cuda.get_device_name(0)}")
else:
    print("CUDA is not available.")

# Load the Whisper model once
print("Loading faster-whisper model...")
model = WhisperModel("medium", device="cuda", compute_type="float32")
print("faster-whisper model loaded. Waiting for audio file...")

def transcribe_audio(audio_file):
    print("Transcribing audio...")

    # Transcribe the audio file using faster-whisper
    segments, info = model.transcribe(audio_file)
    
    # Collect the transcription
    transcription = " ".join([segment.text for segment in segments])
    
    # Print the transcription
    print("Transcription:", transcription)
    return transcription

def send_transcription_to_flask(transcription):
    url = "http://192.168.74.179:5000/submit"  # Replace with the correct URL for your Flask app
    data = {"text": transcription}
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            print("Transcription successfully sent to Flask app.")
        else:
            print(f"Failed to send transcription. Status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Error sending transcription to Flask app: {e}")

# Main loop: Wait for the slow script to provide an audio file
while True:
    if os.path.exists("output.wav"):  # Replace with your signaling mechanism
        transcription = transcribe_audio("output.wav")
        
        # Send the transcription to the Flask app
        send_transcription_to_flask(transcription)
        
        # Remove the audio file after processing
        os.remove("output.wav")
        
        print("Transcription completed and sent. Waiting for the next file...")