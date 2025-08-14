# icd10_kivy_app.py
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.clock import mainthread
import requests
import threading

API_URL = "https://clinicaltables.nlm.nih.gov/api/icd10cm/v3/search"

class ICD10Layout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', spacing=10, padding=10, **kwargs)

        # Search input
        self.search_input = TextInput(
            hint_text="Type diagnosis or code… e.g. fever, diabetes, I10",
            multiline=False,
            size_hint_y=None,
            height=50
        )
        self.search_input.bind(text=self.on_text_change)
        self.add_widget(self.search_input)

        # Status label
        self.status_label = Label(text="", size_hint_y=None, height=30)
        self.add_widget(self.status_label)

        # Results ScrollView
        self.scroll = ScrollView(size_hint=(1, 1))
        self.results_layout = GridLayout(cols=1, spacing=5, size_hint_y=None)
        self.results_layout.bind(minimum_height=self.results_layout.setter('height'))
        self.scroll.add_widget(self.results_layout)
        self.add_widget(self.scroll)

        # Copy button (copies last selected item)
        self.copy_btn = Button(text="Copy Selected", size_hint_y=None, height=50)
        self.copy_btn.bind(on_release=self.copy_selected)
        self.add_widget(self.copy_btn)

        self.selected_text = None
        self.search_delay = None

    def on_text_change(self, instance, value):
        if self.search_delay:
            self.search_delay.cancel()
        value = value.strip()
        if value:
            # Delay search to avoid too many API calls
            self.search_delay = threading.Timer(0.3, lambda: self.search(value))
            self.search_delay.start()
        else:
            self.clear_results()

    def search(self, query):
        threading.Thread(target=self.fetch_results, args=(query,), daemon=True).start()

    def fetch_results(self, query):
        self.update_status("Searching...")
        self.clear_results()
        try:
            params = {'sf': 'code,name', 'terms': query, 'maxList': 20}
            response = requests.get(API_URL, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()
            results = data[3]
            self.update_results(results, query)
        except Exception as e:
            self.update_status(f"Error fetching data: {str(e)}")

    @mainthread
    def update_results(self, results, query):
        if results:
            for code, name in results:
                lbl = Label(text=f"{code} - {name}", size_hint_y=None, height=40)
                lbl.bind(on_touch_down=self.on_label_touch)
                self.results_layout.add_widget(lbl)
            self.update_status(f"Found {len(results)} results for '{query}'")
        else:
            self.update_status("No results found.")

    @mainthread
    def update_status(self, text):
        self.status_label.text = text

    @mainthread
    def clear_results(self):
        self.results_layout.clear_widgets()
        self.selected_text = None

    def on_label_touch(self, instance, touch):
        if instance.collide_point(*touch.pos):
            self.selected_text = instance.text

    def copy_selected(self, instance):
        if self.selected_text:
            try:
                import pyperclip
                pyperclip.copy(self.selected_text)
                self.update_status(f"Copied: {self.selected_text}")
            except:
                self.update_status("Clipboard copy failed. Install 'pyperclip'.")

class ICD10App(App):
    def build(self):
        return ICD10Layout()

if __name__ == "__main__":
    ICD10App().run()
