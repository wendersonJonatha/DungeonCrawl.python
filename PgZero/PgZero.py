

import math
import random
from pygame import Rect
    
import pgzrun 
import sys 
import pygame 


TITLE = "Dungeon Crawl"
WIDTH = 800
HEIGHT = 600
TILE = 64
COLS = WIDTH // TILE
ROWS = HEIGHT // TILE

ANIM_INTERVAL = 0.16         
MOVE_SPEED = 300.0           
INVULNERABLE_TIME = 0.5      
ENEMY_CHASE_RANGE = 100
ENEMY_PATROL_SPEED = (0.3, 0.6) 

MUSIC_NAME = "fundo" 
HIT_SOUND = "hit"


def clamp(v, a, b):
    return max(a, min(b, v))


class AnimatedSprite:
    def __init__(self, x, y, idle_frames, walk_frames):
        self.x = x
        self.y = y
        self.target_x = x
        self.target_y = y
        self.rect = Rect(int(x - TILE/2), int(y - TILE/2), TILE, TILE) 

        self.idle_frames = idle_frames
        self.walk_frames = walk_frames
        self.frame = 0
        self.timer = 0.0
        self.is_moving = False
        self.current_image = idle_frames[0] if idle_frames else None 

    def update_animation(self, dt):
        self.timer += dt
        if self.timer >= ANIM_INTERVAL:
            self.timer = 0.0
            self.frame += 1
            
            if self.is_moving and self.walk_frames:
                self.frame %= len(self.walk_frames)
                self.current_image = self.walk_frames[self.frame]
            elif (not self.is_moving) and self.idle_frames:
                self.frame %= len(self.idle_frames)
                self.current_image = self.idle_frames[self.frame]

    def move_towards(self, dt):
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        dist = math.hypot(dx, dy)
        
        if dist < 1e-3:
            self.x = self.target_x
            self.y = self.target_y
            self.is_moving = False
            return

        self.is_moving = True
        step = MOVE_SPEED * dt
        
        if step >= dist:
            self.x = self.target_x
            self.y = self.target_y
            self.is_moving = False
        else:
            self.x += dx / dist * step
            self.y += dy / dist * step
            
        self.rect.topleft = (int(self.x - TILE/2), int(self.y - TILE/2))

    def update(self, dt):
        self.move_towards(dt)
        self.update_animation(dt)

    def draw(self):
        if self.current_image:
             screen.blit(self.current_image, (self.x, self.y)) 

class Hero(AnimatedSprite):
    def __init__(self, gx, gy):
        px = gx * TILE + TILE/2
        py = gy * TILE + TILE/2
        idle = [f"hero_idle_{i}" for i in (1,2,3,4)]
        walk = [f"hero_walk_{i}" for i in (1,2,3,4)]
        super().__init__(px, py, idle, walk)
        self.gx = gx 
        self.gy = gy 
        self.health = 5 
        self.invulnerable_timer = 0.0 
        self.invulnerable_duration = INVULNERABLE_TIME

    def try_move(self, dx, dy):
        if self.is_moving:
            return
        
        if dx != 0 and dy != 0:
            return 

        nx = clamp(self.gx + dx, 0, COLS - 1)
        ny = clamp(self.gy + dy, 0, ROWS - 1)
        
        if nx != self.gx or ny != self.gy:
            self.gx, self.gy = nx, ny
            self.target_x = nx * TILE + TILE/2
            self.target_y = ny * TILE + TILE/2

    def update(self, dt):
        super().update(dt)
        
        
        if self.invulnerable_timer > 0:
            self.invulnerable_timer -= dt
            
        if self.invulnerable_timer > 0:
            is_visible = (int(self.invulnerable_timer * 10) % 2 == 0)
            if is_visible:
                 frames = self.walk_frames if self.is_moving else self.idle_frames
                 self.current_image = frames[self.frame % len(frames)]
            else:
                 self.current_image = None
        elif self.current_image is None and (self.idle_frames or self.walk_frames):
             frames = self.walk_frames if self.is_moving else self.idle_frames
             self.current_image = frames[self.frame % len(frames)]


class Enemy(AnimatedSprite):
    def __init__(self, cx, cy, radius=2):
        px = cx * TILE + TILE/2
        py = cy * TILE + TILE/2
        idle = [f"enemy_idle_{i}" for i in (1,2,3,4)]
        walk = [f"enemy_walk_{i}" for i in (1,2,3,4)]
        super().__init__(px, py, idle, walk)
        self.cx = cx 
        self.cy = cy 
        self.radius = radius
        self.angle = random.uniform(0, 2*math.pi)
        self.speed_factor = random.uniform(*ENEMY_PATROL_SPEED)
        self.chase_target = None
        self.damage = 1

    def consider(self, hero, radius_px=ENEMY_CHASE_RANGE):
        dx = hero.x - self.x
        dy = hero.y - self.y
        self.chase_target = hero if math.hypot(dx, dy) <= radius_px else None

    def update(self, dt):
        if self.chase_target:
            self.target_x = self.chase_target.x
            self.target_y = self.chase_target.y
        else:
            self.angle += dt * self.speed_factor
            
            ox = math.cos(self.angle) * self.radius * TILE * 0.5 
            oy = math.sin(self.angle) * self.radius * TILE * 0.5
            
            self.target_x = self.cx * TILE + TILE/2 + ox
            self.target_y = self.cy * TILE + TILE/2 + oy
            
        super().update(dt) 


class Button:
    def __init__(self, rect, text, action, color=(30,30,30)):
        self.rect = rect
        self.text = text
        self.action = action
        self.color = color

    def draw(self):
        screen.draw.filled_rect(self.rect, self.color)
        screen.draw.rect(self.rect, (180,180,180))
        screen.draw.text(self.text, center=self.rect.center, fontsize=24, color="white")


class Game:
    def __init__(self):
        self.in_menu = True
        self.music_on = True
        self.hero = None
        self.enemies = []
        
        
        self.btn_start = Button(Rect(300, 200, 200, 56), "Start Game", lambda: self.start())
        self.btn_music = Button(Rect(300, 268, 200, 56), "Music: On", lambda: self.toggle_music())
        self.btn_exit = Button(Rect(300, 336, 200, 56), "Exit", lambda: sys.exit(), color=(50,30,30))
        
        
        self.return_to_menu_scheduled = False

        self.play_music() 

    def play_music(self):
        if self.music_on:
            try:
                music.play(MUSIC_NAME, -1)
            except Exception:
                try: 
                    pygame.mixer.init()
                    pygame.mixer.music.load(f"sounds/{MUSIC_NAME}.mp3") 
                    pygame.mixer.music.play(-1)
                except Exception:
                    pass

    def stop_music(self):
        try: 
            music.stop()
        except Exception: 
            pass
            
    
    def reset_game_state(self):
         self.in_menu = True
         self.return_to_menu_scheduled = False

    def start(self):
        
        
        if self.return_to_menu_scheduled:
            clock.unschedule(self.reset_game_state)
            self.return_to_menu_scheduled = False

        self.in_menu = False
        self.hero = Hero(COLS//2, ROWS//2) 
        self.enemies = []
        
        for i in range(4): 
            cx = random.randint(1, COLS-2)
            cy = random.randint(1, ROWS-2)
            e = Enemy(cx, cy, radius=random.randint(1,3)) 
            self.enemies.append(e)
            
        self.play_music()

    def toggle_music(self):
        self.music_on = not self.music_on
        if self.music_on:
            self.play_music()
            self.btn_music.text = "Music: On"
        else:
            self.stop_music()
            self.btn_music.text = "Music: Off"
            


game = Game()


def on_key_down(key):
    
    if game.in_menu or not game.hero or game.hero.is_moving or game.hero.health <= 0:
        return
        
    dx, dy = 0, 0
    
    if key == keys.UP or key == keys.W:
        dy = -1
    elif key == keys.DOWN or key == keys.S:
        dy = 1
    elif key == keys.LEFT or key == keys.A:
        dx = -1
    elif key == keys.RIGHT or key == keys.D:
        dx = 1

    if dx != 0 or dy != 0:
        game.hero.try_move(dx, dy)

def on_mouse_down(pos):
    if game.in_menu:
        if game.btn_start.rect.collidepoint(pos):
            game.btn_start.action()
        elif game.btn_music.rect.collidepoint(pos):
            game.btn_music.action()
        elif game.btn_exit.rect.collidepoint(pos):
            game.btn_exit.action()
    
    elif game.hero and not game.hero.is_moving and game.hero.health > 0:
        gx = pos[0] // TILE
        gy = pos[1] // TILE
        
        dx = clamp(gx - game.hero.gx, -1, 1)
        dy = clamp(gy - game.hero.gy, -1, 1)
        
        if abs(dx) + abs(dy) <= 2 and (dx != 0 or dy != 0): 
            game.hero.try_move(dx, dy)
        


def update(dt):
    if game.in_menu:
        return
    
    hero = game.hero
    
    
    if hero and hero.health <= 0:
        hero.update(dt) 
        return 
        
    if hero:
        hero.update(dt) 
        
    for e in game.enemies:
        e.consider(hero) 
        e.update(dt)
        
        
        if e.rect.colliderect(hero.rect):
            
            if hero.invulnerable_timer <= 0: 
                
                if not hero.is_moving:
                    
                    if game.music_on:
                         try:
                            sounds[HIT_SOUND].play()
                         except Exception:
                            pass
                    
                    hero.health -= e.damage 
                    hero.health = max(0, hero.health) 
                    
                    hero.invulnerable_timer = hero.invulnerable_duration 
                    
                    
                    dx = hero.x - e.x
                    dy = hero.y - e.y
                    if abs(dx) > abs(dy):
                        hero.try_move(1 if dx > 0 else -1, 0)
                    else:
                        hero.try_move(0, 1 if dy > 0 else -1)
                    
                    if hero.health <= 0:
                        game.stop_music()
                        
                        
                        clock.schedule_unique(game.reset_game_state, 3.0) 
                        game.return_to_menu_scheduled = True 
                        
                        return


def draw_grid():
    screen.fill((20, 20, 20)) 
    for c in range(COLS):
        for r in range(ROWS):
            x = c * TILE
            y = r * TILE
            screen.draw.filled_rect(Rect(x + 1, y + 1, TILE - 2, TILE - 2), (40,40,50)) 

def draw_menu():
    screen.clear()
    screen.draw.text(TITLE, center=(WIDTH//2, 120), fontsize=48, color="#DDDDDD")
    game.btn_start.draw()
    game.btn_music.text = f"Music: {'On' if game.music_on else 'Off'}"
    game.btn_music.draw()
    game.btn_exit.draw()
    screen.draw.text("Use ASWD ou Setas para mover.", center=(WIDTH//2, 440), fontsize=18, color=(150,150,150))
    screen.draw.text("O dano ocorre ao colidir.", center=(WIDTH//2, 465), fontsize=18, color=(150,150,150))

def draw():
    if game.in_menu:
        draw_menu()
        return
        
    draw_grid()
    
    for e in game.enemies:
        e.draw()
        
    if game.hero:
        game.hero.draw()
        health_display = max(0, game.hero.health) 
        screen.draw.text(f"Health: {health_display}", (8,8), fontsize=26, color=(255,100,100))
    
    
    if game.hero and game.hero.health <= 0:
        screen.draw.text("GAME OVER", center=(WIDTH//2, HEIGHT//2), fontsize=80, color=(255, 0, 0))


pgzrun.go()