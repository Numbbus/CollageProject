import os
import time
import vizdoom as vzd
from pynput import keyboard
import cv2 
import numpy as np

import collageGeneratorOPTOMIZED as collage


# ----------------
# Setup collage
# ----------------
LUT = np.load("lut.npy")
cachedImages = collage.cacheInputImages()
RESOLUTION = 5

path = "vizdoomFrame"
# -----------------------------
# Setup ViZDoom
# -----------------------------
game = vzd.DoomGame()



game.set_doom_game_path("DOOM.WAD")
game.set_window_visible(True)
game.set_mode(vzd.Mode.PLAYER)
game.set_console_enabled(True)
game.set_screen_resolution(vzd.ScreenResolution.RES_640X480)
game.set_render_hud(True)
game.set_render_weapon(True)
game.set_render_crosshair(True)
game.set_render_decals(True)
game.set_render_particles(True)
# -----------------------------
# Add buttons
# -----------------------------
game.clear_available_buttons()

# Movement
game.add_available_button(vzd.Button.MOVE_FORWARD)   # 0
game.add_available_button(vzd.Button.MOVE_BACKWARD)  # 1
game.add_available_button(vzd.Button.TURN_LEFT)      # 2
game.add_available_button(vzd.Button.TURN_RIGHT)     # 3
game.add_available_button(vzd.Button.ATTACK)         # 4
game.add_available_button(vzd.Button.USE)            # 5
game.add_available_button(vzd.Button.MOVE_LEFT)      # 6 (strafe left)
game.add_available_button(vzd.Button.MOVE_RIGHT)     # 7 (strafe right)
game.add_available_button(vzd.Button.ALTATTACK)      # 8 (if needed)

# Weapons 1–7
for i in range(1, 8):
    game.add_available_button(getattr(vzd.Button, f"SELECT_WEAPON{i}"))

game.init()

# -----------------------------
# Key mapping
# -----------------------------
button_map = {
    # Movement
    keyboard.KeyCode.from_char('w'): 0,  # MOVE_FORWARD
    keyboard.KeyCode.from_char('s'): 1,  # MOVE_BACKWARD
    keyboard.KeyCode.from_char('a'): 2,  # TURN_LEFT
    keyboard.KeyCode.from_char('d'): 3,  # TURN_RIGHT
    keyboard.KeyCode.from_char('q'): 6,  # MOVE_LEFT (strafe left)
    keyboard.KeyCode.from_char('e'): 7,  # MOVE_RIGHT (strafe right)

    # Combat
    keyboard.Key.space: 4,                  # ATTACK
    keyboard.Key.shift: 8,                  # ALTATTACK

    # Interact
    keyboard.KeyCode.from_char('f'): 5,    # USE (open doors)

    # Weapon selection
    keyboard.KeyCode.from_char('1'): 9,
    keyboard.KeyCode.from_char('2'): 10,
    keyboard.KeyCode.from_char('3'): 11,
    keyboard.KeyCode.from_char('4'): 12,
    keyboard.KeyCode.from_char('5'): 13,
    keyboard.KeyCode.from_char('6'): 14,
    keyboard.KeyCode.from_char('7'): 15,
}

# Track pressed keys
pressed_keys = set()

def on_press(key):
    pressed_keys.add(key)

def on_release(key):
    pressed_keys.discard(key)

listener = keyboard.Listener(on_press=on_press, on_release=on_release)
listener.start()

print("Controls:")
print("W/S = forward/backward, A/D = turn, Q/E = strafe, SPACE = shoot")
print("SHIFT = alt fire, F = use/open doors, 1-7 = weapons, ESC = quit")

episodes = [
    "E1M1", "E1M2", "E1M3", "E1M4", "E1M5", "E1M6", "E1M7", "E1M8", "E1M9",
    "E2M1", "E2M2", "E2M3", "E2M4", "E2M5", "E2M6", "E2M7", "E2M8", "E2M9",
    "E3M1", "E3M2", "E3M3", "E3M4", "E3M5", "E3M6", "E3M7", "E3M8", "E3M9",
    "E4M1", "E4M2", "E4M3", "E4M4", "E4M5", "E4M6", "E4M7", "E4M8", "E4M9",
]

# -----------------------------
# Main loop
# -----------------------------

running = True
for doom_map in episodes:
    if not running:
        break

    game.set_doom_map(doom_map)
    game.new_episode()

    while not game.is_episode_finished() and running:

        state = game.get_state()

        if state and state.screen_buffer is not None:
            # VizDoom outputs (C, H, W). OpenCV needs (H, W, C)
            img = state.screen_buffer.transpose(1, 2, 0)  # (H, W, C)

            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            h, s, v = cv2.split(hsv)

            v = cv2.multiply(v, 2.5) 
            v = np.clip(v, 0, 255).astype(np.uint8)

            bright_hsv = cv2.merge([h, s, v])
            img_bgr = cv2.cvtColor(bright_hsv, cv2.COLOR_HSV2BGR)

            #img_bgr = cv2.cvtColor(img_bgr, cv2.COLOR_RGB2BGR)

            framePath = collage.createCollageForWebServer(img_bgr, RESOLUTION, LUT, cachedImages, path)
            frame = cv2.imread(framePath)
            cv2.imshow("DOOM", frame)
            cv2.waitKey(1) 

        action = [0] * game.get_available_buttons_size()

        for key in pressed_keys:
            if key in button_map:
                action[button_map[key]] = 1

        if keyboard.Key.esc in pressed_keys:  # ESC to quit
            running = False

        game.make_action(action)
        os.remove(framePath)


# -----------------------------
# Cleanup
# -----------------------------
listener.stop()
game.close()
