import pygame
import threading
import os
import sys
import mysql.connector as mysql

pygame.init()
clock = pygame.time.Clock()

screen = pygame.display.set_mode((1280, 720), pygame.FULLSCREEN | pygame.SCALED)
pygame.display.set_caption("CS Project 2026-27")

def resource_path(relative_path):
	try:
		base_path = sys._MEIPASS
	except:
		base_path = os.path.abspath(".")
	return os.path.join(base_path, relative_path)

try:
    db = mysql  .connect(
        host = "mysql-1c132f4a-cs-project-2026-27.a.aivencloud.com",
        database = "cs_project_2026_27",
        port = 26033,
        user = "avnadmin",
        password = "")
except Exception as e:
    connected = False
    print(e)
else:
    connected = True

def draw_loading_screen(percent):
    screen.fill((0, 0, 0))
    loading_text = font.render(f"System Initialising: {percent}%", True, (0, 255, 255))
    screen.blit(loading_text, (640 - loading_text.get_width() // 2, 300))
    bar_width = 400
    bar_height = 30
    fill = (percent / 100) * bar_width
    outline_rect = pygame.FRect(640 - bar_width // 2, 360, bar_width, bar_height)
    fill_rect = pygame.FRect(640 - bar_width // 2, 360, fill, bar_height)
    pygame.draw.rect(screen, (0, 255, 255), outline_rect, 2)
    pygame.draw.rect(screen, (10, 50, 60), fill_rect)
    pygame.display.flip()
    if not connected:
        no_internet_text = font.render("No Internet", True, (255,255, 255))
        screen.blit(no_internet_text, (640 - no_internet_text.get_width(), 400))

load_count = 0
total_assets = 10

def smart_load(file_name, scale_size=None):
    global load_count
    load_count += 1
    path = resource_path(file_name)
    if file_name.endswith((".png", ".jpg")):
        asset = pygame.image.load(path).convert_alpha()
        if scale_size:
            asset = pygame.transform.scale(asset, scale_size)
    else:
        asset = pygame.mixer.Sound(path)
    percent = int((load_count / total_assets) * 100)
    draw_loading_screen(percent)
    return asset

main_font = pygame.font.Font(resource_path("Assets/Fonts/Germania.ttf"), 52)
sub_font = pygame.font.Font(resource_path("Assets/Fonts/Lexend.ttf"), 26)
settings_texts = (main_font.render("Game Settings", True, (255, 255, 255)), sub_font.render("FPS Indicator", True, (255, 255, 255)), sub_font.render("Sound FX", True, (255, 255, 255)), sub_font.render("Particle FX", True, (255, 255, 255)))
game_state = "SETTINGS"
settings_buttons = (pygame.FRect(853.9, 104.3, 231.4, 59.8), pygame.FRect(855.2, 330.1, 231.4, 59.8), pygame.FRect(852.6, 618.1, 231.4, 59.8))
if connected:
    print("Connected")
    while True:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        if game_state == "TITLE":
            pass
        elif game_state == "SETTINGS":
            screen.blit(settings_texts[0], (165.4, 318.4))
            screen.blit(settings_texts[1], (852.6, 42.1))
            screen.blit(settings_texts[2], (888.6, 268))
            screen.blit(settings_texts[3], (875.8, 555.9))
            pygame.draw.rect(screen, (255, 255, 255), settings_buttons[0])
            pygame.draw.rect(screen, (255, 255, 255), settings_buttons[1])
            pygame.draw.rect(screen, (255, 255, 255), settings_buttons[2])
        elif game_state == "LEADERBOARDS":
            pass
        elif game_state == "SHOP":
            pass
        elif game_state == "PLAYING":
            pass

        pygame.display.flip()
        clock.tick(60)
