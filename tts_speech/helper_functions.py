from faster_whisper import WhisperModel
from whisper_mic import WhisperMic
import pyaudio
import wave
import threading


def record_audio(file_path, pause_threshold=5):
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=1024)
    frames = []

    print('Recording...')
    
    # Flag to indicate if recording should continue
    recording = True
    
    def stop_recording():
        nonlocal recording
        print("Recording stopped due to inactivity.")
        recording = False

    # Start a timer thread to stop recording if no input is received
    timer_thread = threading.Timer(pause_threshold, stop_recording)
    timer_thread.start()
    
    try:
        while recording: 
            data = stream.read(1024)
            frames.append(data)
            # Reset the timer thread on new input
            timer_thread.cancel()
            timer_thread = threading.Timer(pause_threshold, stop_recording)
            timer_thread.start()
    except KeyboardInterrupt:
        pass
    
    print('Recording stopped.')

    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(file_path, 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
    wf.setframerate(16000)
    wf.writeframes(b''.join(frames))
    wf.close()

# transcribe_with_faster_whisper
def transcribe_with_faster_whisper(audio_file_path):
    model_identifier = 'base.en'

    model = WhisperModel(model_identifier, device='cuda', compute_type='float16')

    segments, info = model.transcribe(audio_file_path, beam_size=5)
    transcription = " ".join(segment.text for segment in segments)

    return transcription


if __name__ == '__main__':
    record_audio('test.wav')
    print(transcribe_with_faster_whisper('test.wav'))
    