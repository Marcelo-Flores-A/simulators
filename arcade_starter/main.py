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
    """An intelligent predator with human-like tracking behavior."""
    def __init__(self, x, y):
        self.center_x = x
        self.center_y = y
        self.size = PREDATOR_SIZE
        self.color = arcade.color.RED
        
        # Movement and physics
        self.velocity_x = 0.0
        self.velocity_y = 0.0
        self.max_speed = PREDATOR_SPEED
        self.acceleration = 400.0
        self.rotation = 0.0  # Visual rotation angle
        
        # AI behavior states
        self.state = "hunting"  # hunting, patrolling, intercepting
        self.state_timer = 0.0
        self.reaction_delay = random.uniform(0.1, 0.3)  # Human-like reaction time
        self.reaction_timer = 0.0
        
        # Target tracking
        self.target_x = x
        self.target_y = y
        self.last_player_x = x
        self.last_player_y = y
        self.player_velocity_x = 0.0
        self.player_velocity_y = 0.0
        
        # Human-like imperfection
        self.accuracy = random.uniform(0.7, 0.95)  # How accurate the predator is
        self.hesitation_timer = 0.0
        self.is_hesitating = False
        
        # Patrol behavior
        self.patrol_center_x = x
        self.patrol_center_y = y
        self.patrol_radius = random.uniform(80, 120)
        self.patrol_angle = random.uniform(0, 2 * math.pi)

    def update(self, delta_time, player_x, player_y, window_width, window_height):
        self.state_timer += delta_time
        self.reaction_timer += delta_time
        self.hesitation_timer += delta_time
        
        # Calculate player velocity for prediction
        if self.reaction_timer >= self.reaction_delay:
            self.player_velocity_x = (player_x - self.last_player_x) / self.reaction_delay
            self.player_velocity_y = (player_y - self.last_player_y) / self.reaction_delay
            self.last_player_x = player_x
            self.last_player_y = player_y
            self.reaction_timer = 0.0
        
        # Distance to player
        distance_to_player = math.sqrt((self.center_x - player_x)**2 + (self.center_y - player_y)**2)
        
        # State management
        if distance_to_player < 100:
            self.state = "hunting"
        elif distance_to_player > 200 and self.state == "hunting":
            self.state = "intercepting"
        elif distance_to_player > 300:
            self.state = "patrolling"
        
        # Random hesitation (human-like uncertainty)
        if self.hesitation_timer > random.uniform(3.0, 8.0):
            self.is_hesitating = True
            self.hesitation_timer = 0.0
        
        if self.is_hesitating and self.hesitation_timer > random.uniform(0.2, 0.8):
            self.is_hesitating = False
            self.hesitation_timer = 0.0
        
        # Calculate target based on state
        self._calculate_target(player_x, player_y, distance_to_player)
        
        # Apply human-like imperfection
        if not self.is_hesitating:
            self._move_towards_target(delta_time)
        else:
            # Slow down when hesitating
            self.velocity_x *= 0.5
            self.velocity_y *= 0.5
        
        # Update position
        self.center_x += self.velocity_x * delta_time
        self.center_y += self.velocity_y * delta_time
        
        # Handle wall collisions with more natural bouncing
        self._handle_wall_collisions(window_width, window_height)
        
        # Update visual rotation
        if abs(self.velocity_x) > 0.1 or abs(self.velocity_y) > 0.1:
            self.rotation = math.atan2(self.velocity_y, self.velocity_x)

    def _calculate_target(self, player_x, player_y, distance):
        """Calculate the target position based on current AI state."""
        if self.state == "hunting":
            # Direct pursuit with slight prediction
            prediction_time = distance / self.max_speed * 0.3
            self.target_x = player_x + self.player_velocity_x * prediction_time
            self.target_y = player_y + self.player_velocity_y * prediction_time
            
        elif self.state == "intercepting":
            # Predictive interception
            prediction_time = distance / self.max_speed * 0.8
            self.target_x = player_x + self.player_velocity_x * prediction_time
            self.target_y = player_y + self.player_velocity_y * prediction_time
            
            # Add some strategic offset to cut off escape routes
            if abs(self.player_velocity_x) > abs(self.player_velocity_y):
                self.target_y += 50 * (1 if self.center_y < player_y else -1)
            else:
                self.target_x += 50 * (1 if self.center_x < player_x else -1)
                
        elif self.state == "patrolling":
            # Patrol in a circle around the area
            self.patrol_angle += 0.5 * 0.016  # Approximate delta_time for smooth patrol
            self.target_x = self.patrol_center_x + math.cos(self.patrol_angle) * self.patrol_radius
            self.target_y = self.patrol_center_y + math.sin(self.patrol_angle) * self.patrol_radius
        
        # Apply accuracy imperfection
        error_x = random.uniform(-20, 20) * (1.0 - self.accuracy)
        error_y = random.uniform(-20, 20) * (1.0 - self.accuracy)
        self.target_x += error_x
        self.target_y += error_y

    def _move_towards_target(self, delta_time):
        """Move towards target with smooth acceleration and human-like movement."""
        # Calculate direction to target
        dx = self.target_x - self.center_x
        dy = self.target_y - self.center_y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance > 1.0:  # Avoid division by zero
            # Normalize direction
            dx /= distance
            dy /= distance
            
            # Calculate desired velocity
            desired_speed = min(self.max_speed, distance * 2)  # Slow down when close
            desired_vel_x = dx * desired_speed
            desired_vel_y = dy * desired_speed
            
            # Smooth acceleration towards desired velocity
            accel_x = (desired_vel_x - self.velocity_x) * self.acceleration * delta_time
            accel_y = (desired_vel_y - self.velocity_y) * self.acceleration * delta_time
            
            # Limit acceleration for more natural movement
            max_accel = self.acceleration * delta_time
            accel_magnitude = math.sqrt(accel_x*accel_x + accel_y*accel_y)
            if accel_magnitude > max_accel:
                accel_x = (accel_x / accel_magnitude) * max_accel
                accel_y = (accel_y / accel_magnitude) * max_accel
            
            self.velocity_x += accel_x
            self.velocity_y += accel_y
            
            # Limit maximum speed
            vel_magnitude = math.sqrt(self.velocity_x*self.velocity_x + self.velocity_y*self.velocity_y)
            if vel_magnitude > self.max_speed:
                self.velocity_x = (self.velocity_x / vel_magnitude) * self.max_speed
                self.velocity_y = (self.velocity_y / vel_magnitude) * self.max_speed

    def _handle_wall_collisions(self, window_width, window_height):
        """Handle wall collisions with natural bouncing behavior."""
        half_size = self.size / 2
        
        if self.center_x <= half_size:
            self.center_x = half_size
            self.velocity_x = abs(self.velocity_x) * 0.8  # Bounce with some energy loss
        elif self.center_x >= window_width - half_size:
            self.center_x = window_width - half_size
            self.velocity_x = -abs(self.velocity_x) * 0.8
            
        if self.center_y <= half_size:
            self.center_y = half_size
            self.velocity_y = abs(self.velocity_y) * 0.8
        elif self.center_y >= window_height - half_size:
            self.center_y = window_height - half_size
            self.velocity_y = -abs(self.velocity_y) * 0.8

    def draw(self):
        """Draw the predator with directional indicator."""
        # Draw main body
        arcade.draw_circle_filled(self.center_x, self.center_y, self.size // 2, self.color)
        
        # Draw direction indicator (small triangle pointing in movement direction)
        if abs(self.velocity_x) > 0.1 or abs(self.velocity_y) > 0.1:
            indicator_length = self.size // 3
            end_x = self.center_x + math.cos(self.rotation) * indicator_length
            end_y = self.center_y + math.sin(self.rotation) * indicator_length
            arcade.draw_line(self.center_x, self.center_y, end_x, end_y, arcade.color.WHITE, 2)

    def check_collision(self, player_x, player_y, player_size):
        """Check collision with player."""
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
