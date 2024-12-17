import pygame
import random
import sys
import math
import os

# Initialize Pygame
pygame.init()

# Get device screen size for mobile
if os.name == 'posix':  # For Android/iOS
    try:
        import android
        WINDOW_WIDTH = android.get_display_size()[0]
        WINDOW_HEIGHT = android.get_display_size()[1]
    except:
        WINDOW_WIDTH = 400
        WINDOW_HEIGHT = 600
else:  # Fallback dimensions
    WINDOW_WIDTH = 400
    WINDOW_HEIGHT = 600

# Set up the game window
WINDOW = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption('Jumping Person')

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
SKIN_COLOR = (255, 198, 140)

# Scale factors for mobile
SCALE_FACTOR = WINDOW_HEIGHT / 600  # Base scaling on screen height
PERSON_SCALE = SCALE_FACTOR * 1.2  # Make person slightly larger on mobile

# Game variables
GRAVITY = 0.25 * SCALE_FACTOR
PERSON_MOVEMENT = 0
GAME_ACTIVE = True
SCORE = 0
HIGH_SCORE = 0
ANIMATION_TIMER = 0
DIFFICULTY_LEVEL = 1
PIPE_SPEED = 5 * SCALE_FACTOR
PIPE_GAP = 200 * SCALE_FACTOR

def draw_person(surface, animation_time):
    # Clear the surface
    surface.fill((0, 0, 0, 0))
    
    # Scale positions for mobile
    base_size = 15 * PERSON_SCALE
    
    # Calculate animation offsets using sine waves
    arm_offset = math.sin(animation_time * 0.1) * (10 * PERSON_SCALE)
    leg_offset = math.sin(animation_time * 0.1) * (5 * PERSON_SCALE)
    
    # Draw head
    pygame.draw.circle(surface, SKIN_COLOR, (base_size, base_size*0.67), base_size*0.67)
    # Draw body
    pygame.draw.line(surface, SKIN_COLOR, (base_size, base_size*1.33), (base_size, base_size*2.33), int(2*PERSON_SCALE))
    # Draw arms with animation
    pygame.draw.line(surface, SKIN_COLOR, (base_size, base_size*1.67), (base_size*0.33 - arm_offset, base_size*1.67 + arm_offset), int(2*PERSON_SCALE))
    pygame.draw.line(surface, SKIN_COLOR, (base_size, base_size*1.67), (base_size*1.67 + arm_offset, base_size*1.67 + arm_offset), int(2*PERSON_SCALE))
    # Draw legs with animation
    pygame.draw.line(surface, SKIN_COLOR, (base_size, base_size*2.33), (base_size*0.53 - leg_offset, base_size*3 + leg_offset), int(2*PERSON_SCALE))
    pygame.draw.line(surface, SKIN_COLOR, (base_size, base_size*2.33), (base_size*1.47 + leg_offset, base_size*3 + leg_offset), int(2*PERSON_SCALE))

# Person settings
PERSON_SURFACE = pygame.Surface((int(30*PERSON_SCALE), int(50*PERSON_SCALE)), pygame.SRCALPHA)
draw_person(PERSON_SURFACE, 0)
PERSON_RECT = PERSON_SURFACE.get_rect(center=(WINDOW_WIDTH*0.25, WINDOW_HEIGHT/2))

# Pipe settings
PIPE_SURFACE = pygame.Surface((int(50*SCALE_FACTOR), int(400*SCALE_FACTOR)))
PIPE_SURFACE.fill(GREEN)
PIPE_LIST = []
SPAWN_PIPE = pygame.USEREVENT
pygame.time.set_timer(SPAWN_PIPE, 1200)
PIPE_HEIGHT = [int(h*SCALE_FACTOR) for h in [300, 400, 500]]

def update_difficulty():
    global PIPE_SPEED, PIPE_GAP, DIFFICULTY_LEVEL
    DIFFICULTY_LEVEL = (SCORE // 20) + 1
    PIPE_SPEED = (5 + (DIFFICULTY_LEVEL - 1)) * SCALE_FACTOR
    PIPE_GAP = max((200 - (DIFFICULTY_LEVEL - 1) * 10) * SCALE_FACTOR, 140 * SCALE_FACTOR)

def create_pipe():
    random_pipe_pos = random.choice(PIPE_HEIGHT)
    bottom_pipe = PIPE_SURFACE.get_rect(midtop=(WINDOW_WIDTH + 100*SCALE_FACTOR, random_pipe_pos))
    top_pipe = PIPE_SURFACE.get_rect(midbottom=(WINDOW_WIDTH + 100*SCALE_FACTOR, random_pipe_pos - PIPE_GAP))
    return bottom_pipe, top_pipe

def move_pipes(pipes):
    for pipe in pipes:
        pipe.centerx -= PIPE_SPEED
    return pipes

def draw_pipes(pipes):
    for pipe in pipes:
        if pipe.bottom >= WINDOW_HEIGHT:
            WINDOW.blit(PIPE_SURFACE, pipe)
        else:
            flip_pipe = pygame.transform.flip(PIPE_SURFACE, False, True)
            WINDOW.blit(flip_pipe, pipe)

def check_collision(pipes):
    for pipe in pipes:
        if PERSON_RECT.colliderect(pipe):
            return False
    if PERSON_RECT.top <= -100 or PERSON_RECT.bottom >= WINDOW_HEIGHT:
        return False
    return True

def update_score(score, high_score):
    if score > high_score:
        high_score = score
    return high_score

# Game loop
clock = pygame.time.Clock()
font = pygame.font.Font(None, int(36*SCALE_FACTOR))

# Handle touch events
def handle_touch():
    global PERSON_MOVEMENT, GAME_ACTIVE, PIPE_LIST, SCORE, DIFFICULTY_LEVEL, PIPE_SPEED, PIPE_GAP, ANIMATION_TIMER
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
            
        if event.type == pygame.FINGERDOWN or (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1):
            if GAME_ACTIVE:
                PERSON_MOVEMENT = -7 * SCALE_FACTOR
            else:
                GAME_ACTIVE = True
                PIPE_LIST.clear()
                PERSON_RECT.center = (WINDOW_WIDTH*0.25, WINDOW_HEIGHT/2)
                PERSON_MOVEMENT = 0
                SCORE = 0
                DIFFICULTY_LEVEL = 1
                PIPE_SPEED = 5 * SCALE_FACTOR
                PIPE_GAP = 200 * SCALE_FACTOR
                ANIMATION_TIMER = 0
                
        if event.type == SPAWN_PIPE and GAME_ACTIVE:
            PIPE_LIST.extend(create_pipe())

while True:
    handle_touch()
    
    WINDOW.fill(BLACK)
    
    if GAME_ACTIVE:
        update_difficulty()
        
        ANIMATION_TIMER += 1
        
        PERSON_SURFACE.fill((0, 0, 0, 0))
        draw_person(PERSON_SURFACE, ANIMATION_TIMER)
        
        PERSON_MOVEMENT += GRAVITY
        PERSON_RECT.centery += PERSON_MOVEMENT
        WINDOW.blit(PERSON_SURFACE, PERSON_RECT)
        
        PIPE_LIST = move_pipes(PIPE_LIST)
        draw_pipes(PIPE_LIST)
        
        GAME_ACTIVE = check_collision(PIPE_LIST)
        
        for pipe in PIPE_LIST:
            if pipe.centerx == WINDOW_WIDTH*0.24:
                SCORE += 0.5
        
        score_surface = font.render(f'Score: {int(SCORE)} (Level {DIFFICULTY_LEVEL})', True, WHITE)
        score_rect = score_surface.get_rect(center=(WINDOW_WIDTH/2, 50*SCALE_FACTOR))
        WINDOW.blit(score_surface, score_rect)
    else:
        HIGH_SCORE = update_score(int(SCORE), HIGH_SCORE)
        game_over_surface = font.render('Game Over! Tap to restart', True, WHITE)
        game_over_rect = game_over_surface.get_rect(center=(WINDOW_WIDTH/2, WINDOW_HEIGHT/2))
        high_score_surface = font.render(f'High Score: {HIGH_SCORE}', True, WHITE)
        high_score_rect = high_score_surface.get_rect(center=(WINDOW_WIDTH/2, WINDOW_HEIGHT/2 + 50*SCALE_FACTOR))
        
        WINDOW.blit(game_over_surface, game_over_rect)
        WINDOW.blit(high_score_surface, high_score_rect)
    
    pygame.display.update()
    clock.tick(60)
