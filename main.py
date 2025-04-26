from kivy.app import App
from kivy.lang import Builder
from kivy.properties import ListProperty
from kivy.uix.boxlayout import BoxLayout

from kivy.uix.screenmanager import ScreenManager, Screen

class TitleScreen(Screen):
    pass

class GameScreen(Screen):
    pass

class ScreenManager(ScreenManager):
    pass

rootWidget = Builder.load_string('''
ScreenManager:
    TitleScreen:
    GameScreen:
    
<TitleScreen>:
    name: 'title'
    BoxLayout:
        orientation: 'vertical' 
        Label:
            text: 'Mine Sweeper'
        Button:
            text: 'Start Game'
            on_release: app.root.current = 'game'
            
<GameScreen>: 
    name: 'game'
    BoxLayout:
        orientation: 'vertical' 
        Label:
            text: 'Game Screen'
        Button:
            text: 'Back to Title'
            on_release: app.root.current = 'title'


      
''')

class ScreenManagerApp(App):
    def build(self):
        return rootWidget
    
if __name__ == '__main__':
    ScreenManagerApp().run()