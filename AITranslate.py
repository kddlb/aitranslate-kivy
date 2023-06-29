import threading
import os

from kivy.uix.floatlayout import FloatLayout
from kivy.app import App
from kivy.properties import ObjectProperty
from kivy.clock import mainthread
from kivy.lang.builder import Builder


import openai
# define here or use the environment variable
openai.api_key = os.environ["OPENAI_API_KEY"]


class AITranslate(FloatLayout):
    systemMessage = ObjectProperty(None)
    userMessage = ObjectProperty(None)
    assistantMessage = ObjectProperty(None)
    translateButton = ObjectProperty(None)
    translationProgress = ObjectProperty(None)

    def buttonClick(self):
        threading.Thread(target=self.do).start()

    @mainthread
    def set_assistant_text(self, text):
        self.assistantMessage.text = text

    @mainthread
    def calculate_progress(self):
        linesInSource = len(self.userMessage.text.split('\n'))
        linesInTarget = len(self.assistantMessage.text.split('\n'))
        if linesInTarget > linesInSource:
            self.translationProgress.max = 100
            self.translationProgress.value = 100
        else:
            self.translationProgress.max = linesInSource
            self.translationProgress.value = linesInTarget

    def do(self):
        stt = self.systemMessage.text
        utt = self.userMessage.text
        self.translateButton.disabled = True

        self.set_assistant_text("")
        self.calculate_progress()

        completion = openai.ChatCompletion.create(
            model='gpt-3.5-turbo',
            messages=[{
                "role": "system",
                "content": stt
            },
                {
                "role": "user",
                "content": utt
            }],
            max_tokens=2048,
            stream=True
        )

        assistantMessage = ""

        for message in completion:
            if "content" in message["choices"][0]["delta"]:
                assistantMessage += message["choices"][0]["delta"]["content"]
            self.set_assistant_text(assistantMessage)
            self.calculate_progress()

        self.translationProgress.max = 100
        self.translationProgress.value = 100

        self.translateButton.disabled = False


class AITranslateApp(App):
    def build(self):
        Builder.load_string('''#:kivy 1.0
<AITranslate>:
    systemMessage: systemMessage
    userMessage: userMessage
    assistantMessage: assistantMessage
    translateButton: translateButton
    translationProgress: translationProgress

    GridLayout:
        cols: 3
        rows: 3
        spacing: 10
        padding: 10
        Label:
            text: 'Steering (system message)'
            text_size: self.size
            size: self.texture_size
            halign: 'left'
            valign: 'top'
            size_hint: 1, None
        Label:
            text: 'Source (user message)'
            text_size: self.size
            size: self.texture_size
            halign: 'left'
            valign: 'top'
            size_hint: 1, None
        Label:
            text: 'Target (assistant message)'
            text_size: self.size
            size: self.texture_size
            halign: 'left'
            valign: 'top'
            size_hint: 1, None
        TextInput:
            id: systemMessage
            text: 'Produce a singable translation of these lyrics from these instructions:\\n\\n- If they arere in English, translate them to American Spanish.\\n- If they are in Spanish, translate them to English.\\n- If they are in any other language, translate them to American Spanish.\\n- ***Attempt to maintain the properties of rhyming and meter.***\\n- Remove song structure markers (intro, verse, chorus, bridge, etc).'
            size_hint: 0.33, 0.33
            size_hint_max_x: 200
            write_tab: False
        TextInput:
            id: userMessage
            font_size: 32
            write_tab: False
        TextInput:
            id: assistantMessage
            font_size: 32
            readonly: True
            write_tab: False
        Label:
            text_size: self.size
            size: self.texture_size
            size_hint: 1, None
        Button:
            id: translateButton
            text: 'Translate'
            size_hint: None, None
            size: self.texture_size[0] + 16,  self.texture_size[1] + 16
            on_press: root.buttonClick()
        ProgressBar:
            id: translationProgress
            max: 100
            value: 0
            size_hint: 1, None
            height: 15
        ''')
        return AITranslate()


if __name__ == '__main__':
    AITranslateApp().run()
