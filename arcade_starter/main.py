#!/usr/bin/env python
from typing import Set, List
import arcade

# --- Constants ---
WIDTH, HEIGHT = 960, 540
TITLE = "Arcade Starter - Experiments"
MOVE_SPEED = 300.0

class GameView(arcade.View):
    """Main application class."""

    def __init__(self, num_players: int):
        super().__init__()
        self.num_players = num_players
        arcade.set_background_color(arcade.color.DARK_SLATE_GRAY)

        # --- Player 1 Setup ---
        self.player1 = arcade.SpriteSolidColor(32, 32, arcade.color.AZURE)
        self.player1.center_x = WIDTH // 2 - 50
        self.player1.center_y = HEIGHT // 2
        self.player1_keys: Set[str] = set()

        # --- Player 2 Setup ---
        if self.num_players == 2:
            self.player2 = arcade.SpriteSolidColor(32, 32, arcade.color.RED_ORANGE)
            self.player2.center_x = WIDTH // 2 + 50
            self.player2.center_y = HEIGHT // 2
            self.player2_keys: Set[str] = set()

        # Create a sprite list and add players
        self.player_list = arcade.SpriteList()
        self.player_list.append(self.player1)
        if self.num_players == 2:
            self.player_list.append(self.player2)

    def on_draw(self):
        self.clear()
        self.player_list.draw()

        # HUD
        fps = f"FPS: {arcade.get_fps():.0f}"
        p1_controls = "P1: WASD"
        p2_controls = "P2: Arrows" if self.num_players == 2 else ""
        menu_nav = "Fullscreen: F11 | Menu: ESC"
        
        arcade.draw_text(fps, 10, self.window.height - 24, arcade.color.WHITE, 14)
        arcade.draw_text(p1_controls, 10, 34, arcade.color.LIGHT_GRAY, 14)
        if self.num_players == 2:
            arcade.draw_text(p2_controls, 10, 10, arcade.color.LIGHT_GRAY, 14)
        arcade.draw_text(menu_nav, self.window.width - 10, 10, arcade.color.LIGHT_GRAY, 14, anchor_x="right")

    def update_player(self, player: arcade.Sprite, keys: Set[str], delta_time: float):
        dx = (("right" in keys) - ("left" in keys)) * MOVE_SPEED * delta_time
        dy = (("up" in keys) - ("down" in keys)) * MOVE_SPEED * delta_time

        new_x = player.center_x + dx
        new_y = player.center_y + dy
        half_w, half_h = player.width / 2, player.height / 2
        
        player.center_x = max(half_w, min(self.window.width - half_w, new_x))
        player.center_y = max(half_h, min(self.window.height - half_h, new_y))

    def on_update(self, delta_time: float):
        self.update_player(self.player1, self.player1_keys, delta_time)
        if self.num_players == 2:
            self.update_player(self.player2, self.player2_keys, delta_time)

    def on_key_press(self, symbol: int, modifiers: int):
        # --- Player 1 Controls (WASD) ---
        if symbol == arcade.key.A: self.player1_keys.add("left")
        elif symbol == arcade.key.D: self.player1_keys.add("right")
        elif symbol == arcade.key.W: self.player1_keys.add("up")
        elif symbol == arcade.key.S: self.player1_keys.add("down")

        # --- Player 2 Controls (Arrows) ---
        if self.num_players == 2:
            if symbol == arcade.key.LEFT: self.player2_keys.add("left")
            elif symbol == arcade.key.RIGHT: self.player2_keys.add("right")
            elif symbol == arcade.key.UP: self.player2_keys.add("up")
            elif symbol == arcade.key.DOWN: self.player2_keys.add("down")

        # --- Global Controls ---
        if symbol == arcade.key.F11:
            self.window.set_fullscreen(not self.window.fullscreen)
        if symbol == arcade.key.ESCAPE:
            menu_view = MenuView()
            self.window.show_view(menu_view)

    def on_key_release(self, symbol: int, modifiers: int):
        # --- Player 1 ---
        if symbol == arcade.key.A: self.player1_keys.discard("left")
        elif symbol == arcade.key.D: self.player1_keys.discard("right")
        elif symbol == arcade.key.W: self.player1_keys.discard("up")
        elif symbol == arcade.key.S: self.player1_keys.discard("down")

        # --- Player 2 ---
        if self.num_players == 2:
            if symbol == arcade.key.LEFT: self.player2_keys.discard("left")
            elif symbol == arcade.key.RIGHT: self.player2_keys.discard("right")
            elif symbol == arcade.key.UP: self.player2_keys.discard("up")
            elif symbol == arcade.key.DOWN: self.player2_keys.discard("down")


class TextButton:
    """A simple text-based button that changes color on hover."""
    def __init__(self, x, y, text, on_click_action):
        self.center_x = x
        self.center_y = y
        self.text = text
        self.on_click = on_click_action
        self.hovered = False
        self.width = len(text) * 12  # Approximate text width
        self.height = 30

    def draw(self):
        """Draw the text button with hover effect."""
        color = arcade.color.AZURE if self.hovered else arcade.color.WHITE
        arcade.draw_text(
            self.text, 
            self.center_x, 
            self.center_y, 
            color, 
            font_size=24, 
            anchor_x="center", 
            anchor_y="center"
        )

    def check_mouse_hover(self, x, y):
        """Check if the mouse is over the button."""
        half_w = self.width / 2
        half_h = self.height / 2
        self.hovered = (self.center_x - half_w < x < self.center_x + half_w and
                        self.center_y - half_h < y < self.center_y + half_h)


class MenuView(arcade.View):
    """View for the main menu."""
    def __init__(self):
        super().__init__()
        self.buttons: List[TextButton] = []
        self.setup()

    def setup(self):
        """Create menu buttons."""
        # Create buttons with placeholder positions - they'll be updated in on_draw
        self.buttons.append(TextButton(
            0, 0, "Single Player",
            lambda: self.window.show_view(GameView(num_players=1))
        ))
        self.buttons.append(TextButton(
            0, 0, "Two Players",
            lambda: self.window.show_view(GameView(num_players=2))
        ))

    def update_button_positions(self):
        """Update button positions based on current window size."""
        y_pos = self.window.height - 200
        for i, button in enumerate(self.buttons):
            button.center_x = self.window.width / 2
            button.center_y = y_pos - (i * 75)

    def on_show_view(self):
        """This is run once when we switch to this view."""
        arcade.set_background_color(arcade.color.DARK_BLUE_GRAY)

    def on_draw(self):
        """Draw the menu."""
        self.clear()
        
        # Update button positions based on current window size
        self.update_button_positions()
        
        arcade.draw_text(
            "Simulator Menu",
            self.window.width / 2,
            self.window.height - 100,
            arcade.color.WHITE,
            font_size=50,
            anchor_x="center",
        )
        
        # Draw instructions
        arcade.draw_text(
            "Click on an option below:",
            self.window.width / 2,
            self.window.height - 150,
            arcade.color.LIGHT_GRAY,
            font_size=16,
            anchor_x="center",
        )
        
        for button in self.buttons:
            button.draw()

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int):
        """Called when the user moves the mouse."""
        for button in self.buttons:
            button.check_mouse_hover(x, y)

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        """Called when the user presses a mouse button."""
        for btn in self.buttons:
            if btn.hovered:
                btn.on_click()


def main():
    """Main function"""
    window = arcade.Window(WIDTH, HEIGHT, TITLE, resizable=True)
    menu_view = MenuView()
    window.show_view(menu_view)
    arcade.run()


if __name__ == "__main__":
    main()
