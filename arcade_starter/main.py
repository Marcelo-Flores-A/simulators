#!/usr/bin/env python
from typing import Set, List
import arcade
import random
import math

# --- Constants ---
WIDTH, HEIGHT = 960, 540
TITLE = "Arcade Starter - Experiments"
MOVE_SPEED = 300.0
PREDATOR_SPEED = 150.0
FRUIT_SIZE = 16
PREDATOR_SIZE = 24

class Fruit:
    """A colorful fruit that can be collected."""
    def __init__(self, x, y, color):
        self.center_x = x
        self.center_y = y
        self.size = FRUIT_SIZE
        self.color = color

    def draw(self):
        arcade.draw_circle_filled(self.center_x, self.center_y, self.size // 2, self.color)

    def check_collision(self, player_x, player_y, player_size):
        half_fruit = self.size / 2
        half_player = player_size / 2
        return (abs(self.center_x - player_x) < (half_fruit + half_player) and
                abs(self.center_y - player_y) < (half_fruit + half_player))


class Predator:
    """A simple predator that chases the player."""
    def __init__(self, x, y):
        self.center_x = x
        self.center_y = y
        self.size = PREDATOR_SIZE
        self.color = arcade.color.RED
        self.direction_x = random.choice([-1, 1])
        self.direction_y = random.choice([-1, 1])
        self.change_direction_timer = 0

    def update(self, delta_time, player_x, player_y, window_width, window_height):
        # Simple AI: move towards player with some randomness
        self.change_direction_timer += delta_time
        
        if self.change_direction_timer > 2.0:  # Change direction every 2 seconds
            self.change_direction_timer = 0
            if random.random() < 0.7:  # 70% chance to move towards player
                self.direction_x = 1 if player_x > self.center_x else -1
                self.direction_y = 1 if player_y > self.center_y else -1
            else:  # 30% chance for random movement
                self.direction_x = random.choice([-1, 1])
                self.direction_y = random.choice([-1, 1])

        # Move predator
        self.center_x += self.direction_x * PREDATOR_SPEED * delta_time
        self.center_y += self.direction_y * PREDATOR_SPEED * delta_time

        # Bounce off walls
        half_size = self.size / 2
        if self.center_x <= half_size or self.center_x >= window_width - half_size:
            self.direction_x *= -1
        if self.center_y <= half_size or self.center_y >= window_height - half_size:
            self.direction_y *= -1

        # Keep within bounds
        self.center_x = max(half_size, min(window_width - half_size, self.center_x))
        self.center_y = max(half_size, min(window_height - half_size, self.center_y))

    def draw(self):
        arcade.draw_circle_filled(self.center_x, self.center_y, self.size // 2, self.color)

    def check_collision(self, player_x, player_y, player_size):
        distance = math.sqrt((self.center_x - player_x)**2 + (self.center_y - player_y)**2)
        return distance < (self.size + player_size) / 2


class GameView(arcade.View):
    """Main application class with PACMAN-inspired mechanics."""

    def __init__(self, num_players: int):
        super().__init__()
        self.num_players = num_players
        arcade.set_background_color(arcade.color.DARK_SLATE_GRAY)

        # Game state
        self.game_over = False
        self.score = 0
        self.fruits_collected = 0

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

        # Create sprite lists
        self.player_list = arcade.SpriteList()
        self.player_list.append(self.player1)
        if self.num_players == 2:
            self.player_list.append(self.player2)

        # Create predators
        self.predators = []
        for _ in range(3):  # 3 predators
            x = random.randint(50, WIDTH - 50)
            y = random.randint(50, HEIGHT - 50)
            # Make sure predators don't spawn too close to players
            while (abs(x - self.player1.center_x) < 100 and abs(y - self.player1.center_y) < 100):
                x = random.randint(50, WIDTH - 50)
                y = random.randint(50, HEIGHT - 50)
            self.predators.append(Predator(x, y))

        # Create fruits
        self.fruits = []
        self.spawn_fruits()

    def spawn_fruits(self):
        """Spawn fruits randomly on the map with colorful colors."""
        # Define a list of vibrant fruit colors
        fruit_colors = [
            arcade.color.RED,
            arcade.color.ORANGE,
            arcade.color.YELLOW,
            arcade.color.GREEN,
            arcade.color.BLUE,
            arcade.color.PURPLE,
            arcade.color.PINK,
            arcade.color.LIME_GREEN,
            arcade.color.CYAN,
            arcade.color.MAGENTA,
            arcade.color.GOLD,
            arcade.color.SPRING_GREEN,
            arcade.color.DEEP_PINK,
            arcade.color.TURQUOISE,
            arcade.color.VIOLET
        ]
        
        for _ in range(15):  # 15 fruits
            # Pick a random color for each fruit
            color = random.choice(fruit_colors)
            x = random.randint(FRUIT_SIZE, WIDTH - FRUIT_SIZE)
            y = random.randint(FRUIT_SIZE, HEIGHT - FRUIT_SIZE)
            self.fruits.append(Fruit(x, y, color))

    def on_draw(self):
        self.clear()
        
        # Draw fruits
        for fruit in self.fruits:
            fruit.draw()
        
        # Draw predators
        for predator in self.predators:
            predator.draw()
        
        # Draw players
        self.player_list.draw()

        # HUD
        fps = f"FPS: {arcade.get_fps():.0f}"
        score_text = f"Score: {self.score}"
        fruits_text = f"Fruits: {self.fruits_collected}/15"
        p1_controls = "P1: WASD"
        p2_controls = "P2: Arrows" if self.num_players == 2 else ""
        menu_nav = "Fullscreen: F11 | Menu: ESC"
        
        arcade.draw_text(fps, 10, self.window.height - 24, arcade.color.WHITE, 14)
        arcade.draw_text(score_text, 10, self.window.height - 48, arcade.color.YELLOW, 16)
        arcade.draw_text(fruits_text, 10, self.window.height - 72, arcade.color.YELLOW, 14)
        arcade.draw_text(p1_controls, 10, 58, arcade.color.LIGHT_GRAY, 14)
        if self.num_players == 2:
            arcade.draw_text(p2_controls, 10, 34, arcade.color.LIGHT_GRAY, 14)
        arcade.draw_text(menu_nav, self.window.width - 10, 10, arcade.color.LIGHT_GRAY, 14, anchor_x="right")
        
        # Game over screen
        if self.game_over:
            arcade.draw_text(
                "GAME OVER!",
                self.window.width / 2,
                self.window.height / 2 + 50,
                arcade.color.RED,
                font_size=48,
                anchor_x="center"
            )
            arcade.draw_text(
                f"Final Score: {self.score}",
                self.window.width / 2,
                self.window.height / 2,
                arcade.color.WHITE,
                font_size=24,
                anchor_x="center"
            )
            arcade.draw_text(
                "Press ESC to return to menu",
                self.window.width / 2,
                self.window.height / 2 - 50,
                arcade.color.LIGHT_GRAY,
                font_size=18,
                anchor_x="center"
            )
        
        # Victory screen
        elif len(self.fruits) == 0:
            arcade.draw_text(
                "YOU WIN!",
                self.window.width / 2,
                self.window.height / 2 + 50,
                arcade.color.GREEN,
                font_size=48,
                anchor_x="center"
            )
            arcade.draw_text(
                f"Final Score: {self.score}",
                self.window.width / 2,
                self.window.height / 2,
                arcade.color.WHITE,
                font_size=24,
                anchor_x="center"
            )
            arcade.draw_text(
                "Press ESC to return to menu",
                self.window.width / 2,
                self.window.height / 2 - 50,
                arcade.color.LIGHT_GRAY,
                font_size=18,
                anchor_x="center"
            )

    def update_player(self, player: arcade.Sprite, keys: Set[str], delta_time: float):
        dx = (("right" in keys) - ("left" in keys)) * MOVE_SPEED * delta_time
        dy = (("up" in keys) - ("down" in keys)) * MOVE_SPEED * delta_time

        new_x = player.center_x + dx
        new_y = player.center_y + dy
        half_w, half_h = player.width / 2, player.height / 2
        
        player.center_x = max(half_w, min(self.window.width - half_w, new_x))
        player.center_y = max(half_h, min(self.window.height - half_h, new_y))

    def on_update(self, delta_time: float):
        if self.game_over or len(self.fruits) == 0:
            return  # Stop updating if game is over or won
        
        # Update players
        self.update_player(self.player1, self.player1_keys, delta_time)
        if self.num_players == 2:
            self.update_player(self.player2, self.player2_keys, delta_time)

        # Update predators (they chase the closest player)
        for predator in self.predators:
            # Find the closest player
            target_x, target_y = self.player1.center_x, self.player1.center_y
            
            if self.num_players == 2:
                # Calculate distances to both players
                dist_to_p1 = math.sqrt((predator.center_x - self.player1.center_x)**2 + 
                                     (predator.center_y - self.player1.center_y)**2)
                dist_to_p2 = math.sqrt((predator.center_x - self.player2.center_x)**2 + 
                                     (predator.center_y - self.player2.center_y)**2)
                
                # Target the closest player
                if dist_to_p2 < dist_to_p1:
                    target_x, target_y = self.player2.center_x, self.player2.center_y
            
            predator.update(delta_time, target_x, target_y, self.window.width, self.window.height)

        # Check fruit collection for player 1
        fruits_to_remove = []
        for fruit in self.fruits:
            if fruit.check_collision(self.player1.center_x, self.player1.center_y, self.player1.width):
                fruits_to_remove.append(fruit)
                self.score += 10
                self.fruits_collected += 1

        # Check fruit collection for player 2 (if exists)
        if self.num_players == 2:
            for fruit in self.fruits:
                if fruit.check_collision(self.player2.center_x, self.player2.center_y, self.player2.width):
                    if fruit not in fruits_to_remove:  # Avoid double-counting
                        fruits_to_remove.append(fruit)
                        self.score += 10
                        self.fruits_collected += 1

        # Remove collected fruits
        for fruit in fruits_to_remove:
            self.fruits.remove(fruit)

        # Check predator collisions with player 1
        for predator in self.predators:
            if predator.check_collision(self.player1.center_x, self.player1.center_y, self.player1.width):
                self.game_over = True
                break

        # Check predator collisions with player 2 (if exists)
        if self.num_players == 2:
            for predator in self.predators:
                if predator.check_collision(self.player2.center_x, self.player2.center_y, self.player2.width):
                    self.game_over = True
                    break

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
