import pygame
import json
import os
from pygame.locals import *
from tkinter import filedialog, messagebox
import tkinter as tk
import subprocess

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 30
FONT_COLOR = (255, 255, 255)
FONT_SIZE = 24
BACKGROUND_COLOR = (0, 0, 0)

def find_font():
    # Get the directory of the script
    ktb_font_directory = os.path.dirname(os.path.abspath(__file__))
    ktb_font_path = os.path.join(ktb_font_directory, "ktb", "meiryob.ttc")

    # Check if the file exists
    if not os.path.exists(ktb_font_path):
        messagebox.showerror("Error", f"File {ktb_font_path} does not exist.")
        return None  # Return None if file is not found
    
    return ktb_font_path  # Return the correct path if found

ktb_font = find_font()

# Initialize pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("KotoBoss")
clock = pygame.time.Clock()
font = pygame.font.Font(ktb_font, FONT_SIZE)

# Game variables
data = {}
keys = []
values = []
current_frame_index = 0
score = 0
player_health = 3
boss_health = 100
input_text = ""

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class Boss:
    def __init__(self, x, y):
        """Initialize the boss with different animations."""
        self.animations = {
            "idle": self.load_sprites("IDLE.png", 4, (300, 300)),
            "attack": self.load_sprites("ATTACK.png", 8, (300, 300)),
            "got_hit": self.load_sprites("HURT.png", 4, (300, 300)),
            "dead": self.load_sprites("DEATH.png", 6, (300, 300))
        }
        self.current_animation = "idle"
        self.frame_index = 0
        self.image = self.animations[self.current_animation][self.frame_index]
        self.x = (SCREEN_WIDTH - self.image.get_width()) // 2  # Centered
        self.y = (SCREEN_HEIGHT - self.image.get_height()) // 2 - 50  # Adjusted up
        self.last_update = pygame.time.get_ticks()
        self.frame_delay = 100  # Milliseconds between frames

    def load_sprites(self, filename, num_frames, scale_size):
        """Load frames from a sprite sheet using absolute paths."""
        path = os.path.join(BASE_DIR, "ktb", "with_outline", filename)  # Ensure the correct path
        if not os.path.exists(path):
            print(f"Error: {path} NOT FOUND!")  # Debugging message
            return []
        
        print(f"Loading {path}...")  # Confirm it's loading
        sprite_sheet = pygame.image.load(path).convert_alpha()
        width = sprite_sheet.get_width() // num_frames
        height = sprite_sheet.get_height()
        frames = [
            pygame.transform.scale(sprite_sheet.subsurface((i * width, 0, width, height)), scale_size)
            for i in range(num_frames)
        ]
        return frames

    def set_animation(self, name):
        """Change the boss's animation."""
        if name in self.animations and self.current_animation != name:
            self.current_animation = name
            self.frame_index = 0

    def update(self):
        """Update the boss animation."""
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_delay:
            self.last_update = now
            self.frame_index += 1
            if self.frame_index >= len(self.animations[self.current_animation]):
                if self.current_animation == "got_hit":
                    self.set_animation("idle")  # Return to idle after hit animation
                elif self.current_animation == "attack":
                    self.set_animation("idle")
                elif self.current_animation == "dead":
                    self.frame_index = len(self.animations["dead"]) - 1  # Stay on last frame
                else:
                    self.frame_index = 0
            self.image = self.animations[self.current_animation][self.frame_index]

    def draw(self):
        """Draw the boss sprite."""
        screen.blit(self.image, (self.x, self.y))


# Create boss instance
boss = Boss(SCREEN_WIDTH // 2 - 100, 100)


def render_text(text, x, y):
    """Render text on the screen."""
    label = font.render(text, True, FONT_COLOR)
    screen.blit(label, (x, y))


def update_health_bars():
    """Update and render health bars."""
    pygame.draw.rect(screen, (255, 0, 0), (50, 50, 200, 20))  # Player HP bar
    pygame.draw.rect(screen, (0, 255, 0), (50, 50, player_health * 66.67, 20))
    
    pygame.draw.rect(screen, (255, 0, 0), (550, 50, 200, 20))  # Boss HP bar
    pygame.draw.rect(screen, (0, 255, 0), (550, 50, boss_health * 2, 20))
    
    render_text(f"Player HP: {player_health}/3", 50, 20)
    render_text(f"Boss HP: {boss_health}%", 550, 20)


def game_loop():
    global current_frame_index, player_health, boss_health, score, input_text, boss  

    # Reset variables every time game starts
    current_frame_index = 0
    player_health = 3
    boss_health = 100
    score = 0
    input_text = ""

    boss = Boss(SCREEN_WIDTH // 2 - 100, 100)  # Recreate the boss instance
    game_over = False

    input_box = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 100, 200, 40)

    # Timer Variables
    time_limit = 5000  # 10 seconds per question (in milliseconds)
    start_time = pygame.time.get_ticks()  # Track time when question starts

    running = True
    while running:
        screen.fill(BACKGROUND_COLOR)
        if game_over:
            render_text(f"Final Score: {score}", SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50)
            render_text(f"Boss HP Left : {boss_health}", SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2)
            render_text("Back To Menu (Press E)", SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 50)

            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    return
                elif event.type == KEYDOWN:
                    if event.key == K_e:
                        return  

        else:
            update_health_bars()
            boss.update()
            boss.draw()

            if current_frame_index < len(keys):
                question = keys[current_frame_index]
                render_text(question, input_box.x + 10, input_box.y - 40)
                pygame.draw.rect(screen, (255, 255, 255), input_box, 2)
                render_text(input_text, input_box.x + 5, input_box.y + 5)

                # Timer Logic
                elapsed_time = pygame.time.get_ticks() - start_time
                time_left = max(time_limit - elapsed_time, 0)  # Ensure it doesn't go below 0
                
                # Draw Time Bar
                time_bar_width = (time_left / time_limit) * 400  # Scale bar
                pygame.draw.rect(screen, (255, 0, 0), (SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT - 50, time_bar_width, 20))

                # If time runs out
                if time_left == 0:
                    player_health -= 1
                    boss.set_animation("attack")
                    current_frame_index += 1  # Move to next question
                    start_time = pygame.time.get_ticks()  # Reset timer

                    # Check if game over
                    if player_health <= 0:
                        game_over = True

                for event in pygame.event.get():
                    if event.type == QUIT:
                        pygame.quit()
                        return
                    elif event.type == KEYDOWN:
                        if event.key == K_RETURN:
                            correct_value = values[current_frame_index]
                            if input_text.strip().lower() == correct_value.lower():
                                score += 1
                                boss_health -= 10
                                boss.set_animation("got_hit")
                                
                                if boss_health <= 0:  # If boss HP reaches 0, game over
                                    boss.set_animation("dead")
                                    pygame.time.delay(1500)
                                    game_over = True
                                    
                                current_frame_index += 1
                                if current_frame_index >= len(keys):
                                    game_over = True
                            else:
                                player_health -= 1
                                boss.set_animation("attack")

                                if player_health <= 0:  # If player HP reaches 0, game over
                                    game_over = True
                                else:
                                    current_frame_index += 1  # Increment only if player is still alive

                                if current_frame_index >= len(keys):  # Ensure the last question counts
                                    game_over = True
                            input_text = ""
                            start_time = pygame.time.get_ticks()  # Reset timer
                        elif event.key == K_BACKSPACE:
                            input_text = input_text[:-1]
                        else:
                            input_text += event.unicode

        pygame.display.flip()
        clock.tick(FPS)



def load_from_file():
    global data, keys, values
    root = tk.Tk()
    root.withdraw()
    filename = filedialog.askopenfilename(filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
    if filename:
        with open(filename, 'r') as file:
            data = json.load(file)
        keys = list(data.keys())
        values = list(data.values())
        game_loop()
        
def find_listmgr():
    # Get the directory of the script
    ktb_directory = os.path.dirname(os.path.abspath(__file__))
    ktb_filename = os.path.join(ktb_directory, "ktb", "KB_listmgr.py")

    # Check if the file exists
    if not os.path.exists(ktb_filename):
        messagebox.showerror("Error", f"File {ktb_filename} does not exist.")
        return None  # Return None if file is not found
    
    return ktb_filename  # Return the correct path if found

def created_list():
    ktb_filename = find_listmgr()  # Call function to get the correct path
    if ktb_filename:  # Only proceed if the file is found
        subprocess.Popen(["python", ktb_filename])

def start_screen():
    while True:
        screen.fill(BACKGROUND_COLOR)
        render_text("言ボス", SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 100)
        render_text("Press ENTER to Start", SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2)
        render_text("Press E to LIST", SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 50)

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                return
            elif event.type == KEYDOWN:
                if event.key == K_RETURN:
                    load_from_file()
                elif event.key == K_e:  # Added event handling for 'E' key
                    created_list()

        pygame.display.flip()
        clock.tick(FPS)


start_screen()
