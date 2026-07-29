#===IMPORTS===

import pygame
import threading
import os
import sys
import json
import base64
import mysql.connector as mysql

#===PYGAME-INITIALISATION===

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

#===MYSQL-SERVER-CONNECTION===

try:
    db = mysql.connect(
        host = "mysql-1c132f4a-cs-project-2026-27.a.aivencloud.com",
        database = "MechGame",
        port = 26033,
        user = "avnadmin",
        password = "")
except Exception as e:
    print(e)
    connected = False
else:
    connected = True
    cursor = db.cursor()

query_list = ()

connected = True
#===LOADING-SCREEN-AND-ASSETS===

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
data_not_found = None

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

#===FILE-HANDLING-AND-GAME-DATA===

SAVE_FILE = "game_data.json"
def load_data():
    global data_not_found, SAVE_FILE
    default_data = {"userid": ""}
    if not os.path.exists(SAVE_FILE):
        data_not_found = True
        return default_data
    try:
        f = open(SAVE_FILE, "r")
        scrambled_bytes = f.read()
        raw_bytes = base64.b64decode(scrambled_bytes)
        json_string = raw_bytes.decode("utf-8")
        return json.loads(json_string)
        f.close()
    except:
        data_not_found = True
        return default_data

game_data = load_data()
if data_not_found:
    cursor.execute("SELECT UserID FROM Player ORDER BY UserID DESC LIMIT 1")
    result = cursor.fetchone()
    if result is None:
        user_data = 0
    else:
        user_data = result[0]
    cursor.execute(f"INSERT INTO Player VALUES ({user_data + 1}, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1)")
    db.commit()
    game_data["userid"] = user_data + 1
    json_string = json.dumps(game_data)
    raw_bytes = json_string.encode("utf-8")
    scrambled_bytes = base64.b64encode(raw_bytes)
    f = open(SAVE_FILE, "wb")
    f.write(scrambled_bytes)
    f.close()

#===GAME-INITIALISATION===

game_state = "TITLE"

fade_status = "IDLE"
fade_action = None
fade_speed = 600.0
fade_alpha = 0.0
fade_surface = pygame.Surface((1280, 720))
fade_surface.fill((0, 0, 0))

show_fps = False
particle_fx = True
sound_fx = True

def fps_display():
    current_fps = int(clock.get_fps())
    cached_fps_text = sub_font.render(f"FPS: {current_fps}", True, (255, 255, 255))
    screen.blit(cached_fps_text, (1180, 0))

#===OBJECT-INITIALISATION===

main_font = pygame.font.Font(resource_path("Assets/Fonts/Asimovian.ttf"), 52)
sub_font = pygame.font.Font(resource_path("Assets/Fonts/KellySlab.ttf"), 26)

settings_texts = (main_font.render("Game Settings", True, (255, 255, 255)), sub_font.render("FPS Indicator", True, (255, 255, 255)), sub_font.render("Sound FX", True, (255, 255, 255)), sub_font.render("Particle FX", True, (255, 255, 255)))
settings_buttons = (pygame.FRect(800, 100, 100, 50), pygame.FRect(800, 300, 100, 50), pygame.FRect(800, 600, 100, 50))
states = ("ON", "OFF")

title_texts = (main_font.render("Mechamania", True, (255, 255, 255)), sub_font.render("Play", True, (255, 255, 255)), sub_font.render("Settings", True, (255, 255, 255)), sub_font.render("Leaderboards", True, (255, 255, 255)), sub_font.render("Shop", True, (255, 255, 255)))
title_buttons = (
    title_texts[0].get_rect(center=(1280 // 2, 100 + title_texts[0].get_height() // 2)),
    title_texts[1].get_rect(center=(1280 // 2, 320 + title_texts[1].get_height() // 2)),
    title_texts[2].get_rect(center=((   1280 // 2) - 300, 450 + title_texts[2].get_height() // 2)),
    title_texts[3].get_rect(center=(1280 // 2, 450 + title_texts[3].get_height() // 2)),
    title_texts[4].get_rect(center=((1280 // 2) + 300, 450 + title_texts[4].get_height() // 2))
)
title_rects = tuple(pygame.FRect(r).inflate(30, 30) for r in title_buttons)

if connected:
    print("Connected")
    while True:
        dt = clock.tick(60) / 1000.0
        events = pygame.event.get()

        #===EVENT-HANDLING===

        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if fade_status == "IDLE":
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    pos = event.pos
                    if game_state == "TITLE":
                        if title_buttons[2].collidepoint(pos):
                            fade_action = "GOTOSETTINGS"
                            fade_status = "FADE_OUT"
                        if title_buttons[3].collidepoint(pos):
                            fade_action = "GOTOLEADERBOARDS"
                            fade_status = "FADE_OUT"
                        if title_buttons[4].collidepoint(pos):
                            fade_action = "GOTOSHOP"
                            fade_status = "FADEOUT"
                    if game_state == "SETTINGS":
                        if settings_buttons[0].collidepoint(pos):
                            show_fps = not(show_fps)
                        if settings_buttons[1].collidepoint(pos):
                            sound_fx = not(sound_fx)
                        if settings_buttons[2].collidepoint(pos):
                            particle_fx = not(particle_fx)
                    if game_state == "SHOP":
                        pass
                    if game_state == "LEADERBOARDS":
                        pass
                    if game_state == "PLAYING":
                        if not connected_game:
                            screen.blit
        screen.fill((0, 0, 0))

        #===FADE-EFFECTS===

        if fade_status == "FADE_OUT":
            fade_alpha += fade_speed*dt
            if fade_alpha >= 255:
                fade_alpha = 255
                fade_status = "FADE_IN"
                if fade_action == "GOTOSETTINGS":
                    game_state = "SETTINGS"
                elif fade_action == "GOTOSHOP":
                    game_state = "SHOP"
                elif fade_action == "GOTOLEADERBOARDS":
                    game_state = "LEADERBOARDS"
                elif fade_action == "GOTOPLAY":
                    game_state = "PLAYING"
        elif fade_status == "FADE_IN":
            fade_alpha -= fade_speed * dt
            if fade_alpha <= 0:
                fade_alpha = 0
                fade_status = "IDLE"

        #===GAME-STATES===

        if game_state == "TITLE":
            for btn_rect in title_rects[1:]:
                pygame.draw.rect(screen, (200, 200, 200), btn_rect, border_radius=5)
            screen.blit(title_texts[0], title_buttons[0])
            screen.blit(title_texts[1], title_buttons[1])
            screen.blit(title_texts[2], title_buttons[2])
            screen.blit(title_texts[3], title_buttons[3])
            screen.blit(title_texts[4], title_buttons[4])

        elif game_state == "SETTINGS":
            screen.blit(settings_texts[0], (165.4, 318.4))
            screen.blit(settings_texts[1], (850 - settings_texts[1].get_width()//2, 50))
            screen.blit(settings_texts[2], (850- settings_texts[2].get_width()//2, 250))
            screen.blit(settings_texts[3], (850- settings_texts[3].get_width()//2, 550))
            pygame.draw.rect(screen, (255, 255, 255), settings_buttons[0], border_radius=5)
            pygame.draw.rect(screen, (255, 255, 255), settings_buttons[1], border_radius=5)
            pygame.draw.rect(screen, (255, 255, 255), settings_buttons[2], border_radius=5)

        elif game_state == "LEADERBOARDS":
            pass

        elif game_state == "SHOP":
            pass

        elif game_state == "PLAYING":
            pass

        #===FINAL===

        if fade_status != "IDLE":
            fade_surface.set_alpha(int(fade_alpha))
            screen.blit(fade_surface, (0, 0))

        if show_fps:
            fps_display()

        pygame.display.flip()
