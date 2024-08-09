from dotenv import load_dotenv
from deepgram import DeepgramClient, LiveTranscriptionEvents, LiveOptions, Microphone
from threading import Event

load_dotenv()
event = Event()
def transcript_me():
    try:
        # Create a Deepgram client
        deepgram = DeepgramClient()

        # Set up live transcription connection
        dg_connection = deepgram.listen.live.v("1")

        # Variable to store the final transcript
        overall_transcript = []
        final_transcript = []
        def on_message(self, result, **kwargs):
            nonlocal overall_transcript
            is_final = result.is_final
            sentence = result.channel.alternatives[0].transcript.strip()  # Remove leading/trailing spaces
            if len(sentence) > 0:
                # Check if the sentence is already in the transcript
                if not overall_transcript or sentence != overall_transcript[-1]:
                    overall_transcript.append(sentence)

            if is_final:
                # If the result is final, stop the transcription process
                final_sentence = result.channel.alternatives[0].transcript.strip()
                final_transcript.append(final_sentence)
                event.set()  # Set the event to indicate final result received

        # Register event handler for transcript messages
        dg_connection.on(LiveTranscriptionEvents.Transcript, on_message)

        # Define options for live transcription
        options = LiveOptions(
            model="nova-2",
            punctuate=True,
            language="en-IN",
            encoding="linear16",
            channels=1,
            sample_rate=16000,
            interim_results=True,  # Receive interim results
            utterance_end_ms="1000",  # Trigger UtteranceEnd event after 1 second of silence
            vad_events=True,  # Use Voice Activity Detection (VAD) events
        )

        # Start the live transcription
        if not dg_connection.start(options):
            print("Failed to connect to Deepgram")
            return None

        # Open a microphone stream on the default input device
        microphone = Microphone(dg_connection.send)

        # Start the microphone stream
        microphone.start()

        # Wait for final result (indicated by setting the event)
        event.wait()

        # Finish the microphone stream
        microphone.finish()

        # Finish the live transcription
        dg_connection.finish()

        # Return the overall transcript as a single string
        return " ".join(final_transcript)

    except Exception as e:
        print(f"An error occurred during transcription: {e}")
        return None

if __name__ == "__main__":
    event = Event()  # Event to track final result
    user_input = input("Press enter to start transcription: ")
    if user_input.lower() == "":
        result_transcript = transcript_me()
        if result_transcript:
            print("\n\nOverall Transcript:")
            print(result_transcript)
        else:
            print("\n\nTranscription failed.")
