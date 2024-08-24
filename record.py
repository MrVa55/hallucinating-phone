import pyaudio
import wave
import serial
import time

# Parameters for recording
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 1024
OUTPUT_FILENAME = "output.wav"  # Name of the output file

# Initialize PyAudio
audio = pyaudio.PyAudio()

# Initialize serial communication with Arduino
ser = serial.Serial('COM6', 9600)  # Replace 'COM3' with your Arduino port

# Initialize variables to control recording
is_recording = False
is_processing = False
frames = []

# Function to start recording
def start_recording():
    global is_recording, frames
    if not is_processing:  # Only start recording if not currently processing
        is_recording = True
        frames = []  # Clear any previous frames
        print("Recording started...")

# Function to stop recording, save the audio to a file, and trigger the fast script
def stop_recording():
    global is_recording, is_processing, frames
    if is_recording:  # Only stop if currently recording
        is_recording = False
        print("Recording stopped.")
        
        # Save the recorded frames as a WAV file
        wf = wave.open(OUTPUT_FILENAME, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()
        print(f"Audio saved to {OUTPUT_FILENAME}")
        
        # Trigger the fast script for transcription
        trigger_fast_module(OUTPUT_FILENAME)

# Function to handle microphone input while recording
def record_audio(stream):
    global frames
    if is_recording:
        data = stream.read(CHUNK)
        frames.append(data)

# Function to trigger the fast module
def trigger_fast_module(file_name):
    # Write the file name to a text file to be read by the fast module
    with open("file_to_process.txt", "w") as f:
        f.write(file_name)

    # Ensure the file is fully written before triggering the fast script
    time.sleep(0.5)  # Add a small delay (adjust the duration if needed)

    # Create the activation signal
    with open("activate.txt", "w") as f:
        f.write("activate")

    print("Fast module triggered for transcription.")

# Start the microphone stream
stream = audio.open(format=FORMAT, channels=CHANNELS,
                    rate=RATE, input=True,
                    frames_per_buffer=CHUNK)

print("Press the button on the Arduino to start/stop recording...")

try:
    while True:
        # Read the state from the Arduino
        if ser.in_waiting > 0:
            button_state = ser.readline().decode('utf-8').strip()
            
            if button_state == "PRESSED" and not is_recording and not is_processing:
                start_recording()
            elif button_state == "RELEASED" and is_recording:
                stop_recording()

        # Handle audio recording
        record_audio(stream)

except KeyboardInterrupt:
    print("Program terminated.")

# Stop the microphone stream and close it
stream.stop_stream()
stream.close()
audio.terminate()

ser.close()
