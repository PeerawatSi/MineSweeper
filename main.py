from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import NumericProperty, ObjectProperty
from kivy.metrics import dp
from kivy.core.window import Window
import random

class MinesweeperCell(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.is_mine = False
        self.adjacent_mines = 0
        self.revealed = False
        self.flagged = False
        self.font_size = dp(16)
        self.background_normal = ''
        self.background_color = (0.7, 0.7, 0.7, 1)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            if touch.button == 'right':
                self.flag_cell()
                return True
        return super().on_touch_down(touch)

    def flag_cell(self):
        if not self.revealed:
            self.flagged = not self.flagged
            self.text = "F" if self.flagged else ""
            self.background_color = (0.7, 0.7, 0.7, 1) if self.flagged else (0.7, 0.7, 0.7, 1)

class MinesweeperGrid(GridLayout):
    def __init__(self, rows=10, cols=10, mine_count=15, **kwargs):
        super().__init__(cols=cols, **kwargs)
        self.rows = rows
        self.cols = cols
        self.mine_count = mine_count
        self.cells = []
        self.spacing = [dp(2), dp(2)]
        self.padding = [dp(5), dp(5)]
        self.create_grid()

    def create_grid(self):
        self.cells = []
        self.clear_widgets()
        
        cell_size = self.calculate_cell_size()
        
        for _ in range(self.rows * self.cols):
            cell = MinesweeperCell(size_hint=(None, None), size=cell_size)
            cell.bind(on_press=self.reveal_cell)
            self.cells.append(cell)
            self.add_widget(cell)

        mines = random.sample(range(len(self.cells)), self.mine_count)
        for idx in mines:
            self.cells[idx].is_mine = True

        for idx, cell in enumerate(self.cells):
            if not cell.is_mine:
                cell.adjacent_mines = self.count_adjacent_mines(idx)

    def calculate_cell_size(self):
        # Calculate based on window width minus padding
        available_width = Window.width - (self.padding[0] * 2) - (self.cols * self.spacing[0])
        cell_size = min(available_width / self.cols, dp(50))  # Max 50dp per cell
        return (cell_size, cell_size)

    def count_adjacent_mines(self, idx):
        row, col = divmod(idx, self.cols)
        count = 0
        for r in range(max(0, row-1), min(row+2, self.rows)):
            for c in range(max(0, col-1), min(col+2, self.cols)):
                if r == row and c == col:
                    continue
                neighbor_idx = r * self.cols + c
                if self.cells[neighbor_idx].is_mine:
                    count += 1
        return count

    def reveal_cell(self, cell):
        if cell.flagged or cell.revealed:
            return

        cell.revealed = True
        if cell.is_mine:
            cell.text = "B"
            cell.background_color = (1, 0, 0, 1)
            self.game_over(False)
        else:
            colors = [
                (0.9, 0.9, 0.9, 1),  # 0
                (0.2, 0.2, 1, 1),     # 1
                (0.4, 0.5, 0.1, 1),       # 2
                (0.2, 0.6, 0.4, 1),     # 3
                (0, 0, 0.5, 1),       # 4
                (0.5, 0, 0.5, 1),       # 5
                (0, 0.5, 0.5, 1),     # 6
                (0, 0, 0, 1),         # 7
                (0.5, 1, 0.5, 1)    # 8
            ]
            cell.text = str(cell.adjacent_mines) if cell.adjacent_mines > 0 else ""
            cell.background_color = colors[cell.adjacent_mines]
            if cell.adjacent_mines == 0:
                self.reveal_adjacent_cells(cell)
            self.check_win()

    def reveal_adjacent_cells(self, cell):
        idx = self.cells.index(cell)
        row, col = divmod(idx, self.cols)
        for r in range(max(0, row-1), min(row+2, self.rows)):
            for c in range(max(0, col-1), min(col+2, self.cols)):
                neighbor_idx = r * self.cols + c
                neighbor = self.cells[neighbor_idx]
                if not neighbor.revealed and not neighbor.flagged:
                    self.reveal_cell(neighbor)

    def check_win(self):
        unrevealed_safe_cells = sum(1 for cell in self.cells 
                                  if not cell.is_mine and not cell.revealed)
        if unrevealed_safe_cells == 0:
            self.game_over(True)

    def game_over(self, won):
        message = "You Win!" if won else "Game Over!"
        popup = Popup(title=message, size_hint=(0.5, 0.5))
        popup.add_widget(Label(text=message, font_size=24))
        popup.open()

class TitleScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'title'
        
        main_layout = BoxLayout(orientation='vertical', padding=dp(30), spacing=dp(20))
        
        title = Label(text='MINESWEEPER', font_size=dp(40), bold=True)
        
        content = BoxLayout(orientation='vertical', spacing=dp(15), size_hint_y=None, height=dp(250))
        difficulty_label = Label(text='Select Difficulty', font_size=dp(24))
        
        btn_height = dp(45)
        easy_btn = Button(text='Easy (9x9, 10 Mines)', size_hint_y=None, height=btn_height)
        medium_btn = Button(text='Medium (16x16, 40 Mines)', size_hint_y=None, height=btn_height)
        hard_btn = Button(text='Hard (24x24, 99 Mines)', size_hint_y=None, height=btn_height)
        
        easy_btn.bind(on_release=self.start_game(9, 9, 10))
        medium_btn.bind(on_release=self.start_game(16, 16, 40))
        hard_btn.bind(on_release=self.start_game(24, 24, 99))
        
        content.add_widget(difficulty_label)
        content.add_widget(easy_btn)
        content.add_widget(medium_btn)
        content.add_widget(hard_btn)
        
        main_layout.add_widget(title)
        main_layout.add_widget(content)
        
        self.add_widget(main_layout)
    
    def start_game(self, rows, cols, mines):
        def callback(instance):
            game_screen = self.manager.get_screen('game')
            game_screen.rows = rows
            game_screen.cols = cols
            game_screen.mines = mines
            self.manager.current = 'game'
        return callback

class GameScreen(Screen):
    rows = NumericProperty(9)
    cols = NumericProperty(9)
    mines = NumericProperty(10)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'game'
        self.game_grid = None
        self.setup_ui()
    
    def setup_ui(self):
        main_layout = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(5))
        
        # Game grid container (takes most space)
        self.grid_container = BoxLayout(orientation='vertical', size_hint=(1, 1))
        
        # Bottom bar with back button
        bottom_bar = BoxLayout(size_hint=(1, None), height=dp(50), padding=(dp(10), 0))
        back_btn = Button(text='Back to Title', 
                         size_hint=(None, 1), 
                         width=dp(150),
                         background_color=(0.8, 0.2, 0.2, 1))
        back_btn.bind(on_release=self.go_back)
        
        bottom_bar.add_widget(Label())  # Spacer
        bottom_bar.add_widget(back_btn)
        bottom_bar.add_widget(Label())  # Spacer
        
        main_layout.add_widget(self.grid_container)
        main_layout.add_widget(bottom_bar)
        
        self.add_widget(main_layout)
    
    def on_enter(self):
        if self.game_grid:
            self.grid_container.remove_widget(self.game_grid)
        
        self.game_grid = MinesweeperGrid(
            rows=self.rows, 
            cols=self.cols, 
            mine_count=self.mines
        )
        self.grid_container.add_widget(self.game_grid)
    
    def go_back(self, instance):
        self.manager.current = 'title'

class MinesweeperApp(App):
    def build(self):
        # Set minimum window size
        Window.minimum_width = 400
        Window.minimum_height = 500
        
        sm = ScreenManager()
        sm.add_widget(TitleScreen())
        sm.add_widget(GameScreen())
        return sm

if __name__ == "__main__":
    MinesweeperApp().run()