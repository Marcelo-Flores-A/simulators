#!/usr/bin/env python
from typing import Set

import arcade

WIDTH, HEIGHT = 960, 540
TITLE = "Arcade Starter - Experiments"
MOVE_SPEED = 300.0


class App(arcade.Window):
    def __init__(self):
        super().__init__(WIDTH, HEIGHT, TITLE, resizable=True, update_rate=1 / 120)
        arcade.set_background_color(arcade.color.DARK_SLATE_GRAY)

        # Simple controllable player sprite
        self.player = arcade.SpriteSolidColor(32, 32, arcade.color.AZURE)
        self.player.center_x = WIDTH // 2
        self.player.center_y = HEIGHT // 2
        self.player_list = arcade.SpriteList()
        self.player_list.append(self.player)

        # Track pressed directions
        self.keys: Set[str] = set()

    def on_draw(self):
        self.clear()
        self.player_list.draw()

        # HUD
        controls = "Move: WASD / Arrows   Fullscreen: F11   Quit: ESC"
        arcade.draw_text(controls, 10, 10, arcade.color.LIGHT_GRAY, 14)

    def on_update(self, delta_time: float):
        dx = (("right" in self.keys) - ("left" in self.keys)) * MOVE_SPEED * delta_time
        dy = (("up" in self.keys) - ("down" in self.keys)) * MOVE_SPEED * delta_time

        # Clamp to window bounds
        new_x = self.player.center_x + dx
        new_y = self.player.center_y + dy
        half_w = self.player.width / 2
        half_h = self.player.height / 2
        self.player.center_x = max(half_w, min(self.width - half_w, new_x))
        self.player.center_y = max(half_h, min(self.height - half_h, new_y))

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.ESCAPE:
            arcade.exit()

        elif symbol in (arcade.key.LEFT, arcade.key.A):
            self.keys.add("left")
        elif symbol in (arcade.key.RIGHT, arcade.key.D):
            self.keys.add("right")
        elif symbol in (arcade.key.UP, arcade.key.W):
            self.keys.add("up")
        elif symbol in (arcade.key.DOWN, arcade.key.S):
            self.keys.add("down")

        elif symbol == arcade.key.F11:
            self.set_fullscreen(not self.fullscreen)

    def on_key_release(self, symbol: int, modifiers: int):
        if symbol in (arcade.key.LEFT, arcade.key.A):
            self.keys.discard("left")
        elif symbol in (arcade.key.RIGHT, arcade.key.D):
            self.keys.discard("right")
        elif symbol in (arcade.key.UP, arcade.key.W):
            self.keys.discard("up")
        elif symbol in (arcade.key.DOWN, arcade.key.S):
            self.keys.discard("down")


if __name__ == "__main__":
    app = App()
    arcade.run()
