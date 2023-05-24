from langchain.callbacks.base import BaseCallbackHandler
import azure.cognitiveservices.speech as speechsdk
import os

class StreamDisplayHandler(BaseCallbackHandler):
    def __init__(self, container, initial_text="", display_method='markdown'):
        self.container = container
        self.text = initial_text
        self.display_method = display_method
        self.new_sentence = ""

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        self.text += token
        self.new_sentence += token

        display_function = getattr(self.container, self.display_method, None)
        if display_function is not None:
            display_function(self.text)
        else:
            raise ValueError(f"Invalid display_method: {self.display_method}")

    def on_llm_end(self, response, **kwargs) -> None:
        self.text=""


class StreamSpeakHandler(BaseCallbackHandler):
    def __init__(self, recognition="zh-CN", synthesis="zh-CN-XiaoxiaoNeural"):
        self.new_sentence = ""
        # Initialize the speech synthesizer
        self.speech_recognizer, self.speech_synthesizer = self.settings(recognition, synthesis)

    def settings(self, recognition, synthesis):
        speech_config = speechsdk.SpeechConfig(
            subscription=os.environ.get('SPEECH_KEY'), 
            region=os.environ.get('SPEECH_REGION')
        )
        audio_output_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)
        audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)

        speech_config.speech_recognition_language=recognition
        speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

        speech_config.speech_synthesis_voice_name=synthesis

        speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_output_config)
        return speech_recognizer, speech_synthesizer

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        self.new_sentence += token
        # Check if the new token forms a sentence.
        if token in ".:!?。：！？\n":
            # Synthesize the new sentence
            speak_this = self.new_sentence
            self.speak_text_async(speak_this)
            self.new_sentence = ""

    def on_llm_end(self, response, **kwargs) -> None:
        self.new_sentence = ""

    def speak_text_async(self, text):
        speech_synthesis_result = self.speech_synthesizer.speak_text_async(text).get()
        if speech_synthesis_result.reason != speechsdk.ResultReason.SynthesizingAudioCompleted:
            print(f'Error synthesizing speech: {speech_synthesis_result.reason}')
