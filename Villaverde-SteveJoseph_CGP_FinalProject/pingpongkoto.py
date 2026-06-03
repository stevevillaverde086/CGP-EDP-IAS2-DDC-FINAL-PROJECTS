import pygame
import random
import math
from tkinter import *
from enum import Enum

# =====================================================
# AUDIO INIT (simple built-in synth sounds)
# =====================================================

pygame.mixer.pre_init(44100, -16, 1, 512)
pygame.init()

def beep(freq=440, duration=80, volume=0.3):
    # simple procedural sound (no external files)
    sample_rate = 44100
    n_samples = int(sample_rate * duration / 1000)

    buf = bytearray()

    for x in range(n_samples):
        t = x / sample_rate
        wave = int(32767 * math.sin(2 * math.pi * freq * t))
        buf += int(wave).to_bytes(2, byteorder='little', signed=True)

    sound = pygame.mixer.Sound(buffer=bytes(buf))
    sound.set_volume(volume)
    sound.play()

# =====================================================
# MENU
# =====================================================

mode = "PVP"

def create_menu():
    root = Tk()
    root.title("Cosmic Pong Omega")
    root.geometry("600x600")
    root.config(bg="black")

    def pvp():
        global mode
        mode = "PVP"
        root.destroy()

    def ai():
        global mode
        mode = "AI"
        root.destroy()

    def show_guide():
        clear_menu()
        
        Label(root,
              text="GAME GUIDE",
              font=("Arial", 24, "bold"),
              fg="cyan", bg="black").pack(pady=20)
        
        guide_text = """
POWER-UPS (Collectible during gameplay):
• YELLOW SPEED - Paddle moves 20% faster for 5 seconds
• GREEN SHIELD - Blocks one hit from damage
• PURPLE GROW - Paddle becomes 60% larger for 6 seconds
• CYAN FREEZE - Temporarily freezes opponent's ball for 3 seconds
• ORANGE SLOWBALL - Reduces ball speed temporarily

GAMEPLAY MECHANICS:
• Score 12 points to WIN the game
• COMBO SYSTEM - Hit the ball consecutively for score multipliers
• BALL SPLIT - At combo 15, ball splits into 2 for chaos mode
• GRAVITY WAVES - Ball gets pulled in random directions
• SCREEN SHAKE - Intense feedback when hitting the ball
• CORE (Middle) - Spinning lines that bounce the ball away

CONTROLS:
• Player 1: W/S to move, A to dash
• Player 2: UP/DOWN to move, LEFT to dash

POWER CHAIN:
• Collect the same power-up 3 times to unlock MEGA POWER!

TIPS:
• The core helps keep the ball in play
• Use dash to make quick escapes
• Power-ups spawn randomly - grab them when you can!
"""
        
        Label(root,
              text=guide_text,
              font=("Arial", 9),
              fg="lime", bg="black",
              justify=LEFT,
              wraplength=550).pack(pady=10)
        
        Button(root,
               text="BACK TO MENU",
               font=("Arial", 12, "bold"),
               bg="cyan",
               fg="black",
               width=20,
               command=back_to_menu).pack(pady=10)

    def back_to_menu():
        for widget in root.winfo_children():
            widget.destroy()
        show_main_menu()

    def clear_menu():
        for widget in root.winfo_children():
            widget.destroy()

    def show_main_menu():
        Label(root,
              text="COSMIC PONG OMEGA",
              font=("Arial", 26, "bold"),
              fg="cyan", bg="black").pack(pady=30)

        Button(root,
               text="PVP",
               font=("Arial", 14, "bold"),
               bg="cyan",
               fg="black",
               width=20,
               command=pvp).pack(pady=10)

        Button(root,
               text="VS AI",
               font=("Arial", 14, "bold"),
               bg="magenta",
               fg="white",
               width=20,
               command=ai).pack(pady=10)

        Button(root,
               text="GAME GUIDE",
               font=("Arial", 14, "bold"),
               bg="lime",
               fg="black",
               width=20,
               command=show_guide).pack(pady=10)

        Label(root,
              text="Master the combos, dodge the chaos!",
              fg="#00FF00",
              bg="black").pack(pady=30)

    show_main_menu()
    root.mainloop()

create_menu()

# =====================================================
# GAME INIT
# =====================================================

W, H = 1300, 750
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Cosmic Pong Omega - Enhanced")

clock = pygame.time.Clock()

WHITE = (255,255,255)
CYAN = (0,255,255)
PINK = (255,0,180)
PURPLE = (180,0,255)
BLACK = (8,8,20)
GREEN = (0,255,0)
YELLOW = (255,255,0)
RED = (255,0,0)
ORANGE = (255,165,0)

font = pygame.font.SysFont("consolas", 26)
big = pygame.font.SysFont("consolas", 60)
small = pygame.font.SysFont("consolas", 16)

# =====================================================
# STARFIELD
# =====================================================

stars = [[random.randint(0,W), random.randint(0,H), random.randint(1,4), random.uniform(0.5,2)] for _ in range(160)]

# =====================================================
# PARTICLES
# =====================================================

particles = []

def burst(x,y,c,count=20):
    for i in range(count):
        particles.append([
            x,y,
            random.uniform(-5,5),
            random.uniform(-5,5),
            random.randint(3,6),
            c
        ])

def draw_particles():
    for p in particles[:]:
        p[0]+=p[2]
        p[1]+=p[3]
        p[4]-=0.12

        pygame.draw.circle(screen,p[5],
            (int(p[0]),int(p[1])),max(1,int(p[4])))

        if p[4]<=0:
            particles.remove(p)

# =====================================================
# POWER-UPS
# =====================================================

class PowerUp:
    def __init__(self, x, y, power_type):
        self.x = x
        self.y = y
        self.r = 15
        self.power_type = power_type  # "speed", "shield", "grow", "freeze"
        self.angle = 0
        self.duration = 300  # frames
        
        self.color_map = {
            "speed": YELLOW,
            "shield": GREEN,
            "grow": PURPLE,
            "freeze": CYAN,
            "slowball": ORANGE
        }

    def update(self):
        self.angle += 5

    def draw(self):
        # Multiple pulsing rings for glow effect
        for ring in range(3, 0, -1):
            ring_r = self.r + ring * 8 + math.sin(self.angle * 0.1) * 4
            alpha = max(50, 150 - ring * 40)
            color = self.color_map[self.power_type]
            pygame.draw.circle(screen, color, (int(self.x), int(self.y)), int(ring_r), 2)
        
        # Main circle
        pygame.draw.circle(screen, self.color_map[self.power_type], (int(self.x), int(self.y)), self.r)
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.r, 2)

    def get_rect(self):
        return pygame.Rect(self.x - self.r, self.y - self.r, self.r * 2, self.r * 2)

power_ups = []

def spawn_powerup():
    if random.random() < 0.008 and len(power_ups) < 2:  # 0.8% chance per frame, max 2 at once
        x = random.randint(200, W - 200)
        y = random.randint(100, H - 100)
        power_type = random.choice(["speed", "shield", "grow", "freeze", "slowball"])
        power_ups.append(PowerUp(x, y, power_type))



# =====================================================
# PADDLE (NOW HAS DASH ABILITY + POWER-UPS)
# =====================================================

class Paddle:
    def __init__(self,x,y,c):
        self.base_width = 22
        self.base_height = 110
        self.x = x
        self.y = y
        self.c = c
        self.speed = 8
        self.power = 0
        self.dash_cd = 0
        
        # Power-up effects
        self.shield = False
        self.shield_timer = 0
        self.speed_boost = 1.0
        self.speed_timer = 0
        self.size_boost = 1.0
        self.size_timer = 0

    @property
    def rect(self):
        width = int(self.base_width * self.size_boost)
        height = int(self.base_height * self.size_boost)
        return pygame.Rect(self.x, self.y, width, height)

    def update(self):
        if self.shield_timer > 0:
            self.shield_timer -= 1
        else:
            self.shield = False
            
        if self.speed_timer > 0:
            self.speed_timer -= 1
        else:
            self.speed_boost = 1.0
            
        if self.size_timer > 0:
            self.size_timer -= 1
        else:
            self.size_boost = 1.0

    def move(self, up, down):
        speed = self.speed * self.speed_boost
        if up and self.y > 0:
            self.y -= speed
        if down and self.y + int(self.base_height * self.size_boost) < H:
            self.y += speed

        if self.dash_cd > 0:
            self.dash_cd -= 1

    def dash(self):
        if self.dash_cd == 0:
            self.y += random.choice([-60, 60])
            height = int(self.base_height * self.size_boost)
            self.y = max(0, min(H - height, self.y))
            self.dash_cd = 120
            beep(600, 60)
            burst(self.rect.centerx, self.rect.centery, self.c, 15)

    def apply_powerup(self, power_type):
        self.power_type = power_type  # Track for power chains
        if power_type == "speed":
            self.speed_boost = 1.2  # Reduced from 1.4 to 1.2
            self.speed_timer = 300
            beep(800, 100)
            burst(self.rect.centerx, self.rect.centery, YELLOW, 20)
        elif power_type == "shield":
            self.shield = True
            self.shield_timer = 500
            beep(700, 150)
            burst(self.rect.centerx, self.rect.centery, GREEN, 25)
        elif power_type == "grow":
            self.size_boost = 1.6
            self.size_timer = 400
            beep(600, 100)
            burst(self.rect.centerx, self.rect.centery, PURPLE, 20)
        elif power_type == "slowball":
            # Slow ball effect applied globally (easier to track)
            beep(750, 100)
            burst(self.rect.centerx, self.rect.centery, ORANGE, 20)

    def draw(self):
        rect = self.rect
        pygame.draw.rect(screen, self.c, rect, border_radius=8)
        
        if self.shield:
            pygame.draw.rect(screen, GREEN, rect, 4, border_radius=8)

# =====================================================
# BALL (MORE PHYSICS FEEL + FREEZE)
# =====================================================

class Ball:
    def __init__(self):
        self.reset()
        self.frozen = False
        self.frozen_timer = 0
        self.core_immunity = 0  # Immunity to core bounces when leaving

    def reset(self):
        self.x=W//2
        self.y=H//2
        self.r=12
        self.vx=random.choice([-7,7])
        self.vy=random.choice([-5,5])
        self.frozen = False
        self.frozen_timer = 0
        self.core_immunity = 0
        self.paddle_collision_cd = 0  # Cooldown to prevent spam hits

    def update(self):
        if self.frozen_timer > 0:
            self.frozen_timer -= 1
            self.frozen = True
        else:
            self.frozen = False
        
        if self.core_immunity > 0:
            self.core_immunity -= 1
        
        if self.paddle_collision_cd > 0:
            self.paddle_collision_cd -= 1

    def move(self):
        if self.frozen:
            return
        
        # Cap ball velocity to prevent it from being too fast
        max_speed = 12
        speed = math.hypot(self.vx, self.vy)
        if speed > max_speed:
            scale = max_speed / speed
            self.vx *= scale
            self.vy *= scale
            
        self.x+=self.vx
        self.y+=self.vy

        # wall bounce
        if self.y-self.r<=0:
            self.y=self.r
            self.vy*=-1
            beep(300,40)

        if self.y+self.r>=H:
            self.y=H-self.r
            self.vy*=-1
            beep(300,40)

    def draw(self):
        color = (100, 100, 255) if not self.frozen else (100, 200, 255)
        
        for i in range(6):
            pygame.draw.circle(screen, color,
                (int(self.x-self.vx*i*0.8),
                 int(self.y-self.vy*i*0.8)),
                self.r-i)

        pygame.draw.circle(screen,WHITE,(int(self.x),int(self.y)),self.r)
        
        if self.frozen:
            pygame.draw.circle(screen, CYAN, (int(self.x), int(self.y)), self.r, 3)

# =====================================================
# SPINNING CORE (NOW BOUNCES BALL)
# =====================================================

class Core:
    def __init__(self):
        self.x = W // 2
        self.y = H // 2
        self.angle = 0
        self.radius = 30
        self.line_length = 100

    def update(self):
        self.angle += 3

    def affect_ball(self, ball):
        if ball.frozen or ball.core_immunity > 0:
            return
            
        dx = self.x - ball.x
        dy = self.y - ball.y
        dist = math.hypot(dx, dy)

        # Check if ball hits the core area
        if dist < self.radius + ball.r:
            # Bounce the ball away from core
            if dist > 0:
                angle = math.atan2(dy, dx)
                ball.vx = math.cos(angle) * 8
                ball.vy = math.sin(angle) * 8
                # Grant temporary immunity so ball can escape
                ball.core_immunity = 30
            burst(ball.x, ball.y, PURPLE, 20)
            beep(450, 60)

    def draw(self):
        # Pulsing outer ring
        pulse = 5 + math.sin(self.angle * 0.05) * 3
        pygame.draw.circle(screen, PURPLE, (self.x, self.y), int(self.radius + pulse), 3)
        pygame.draw.circle(screen, PURPLE, (self.x, self.y), self.radius)
        pygame.draw.circle(screen, CYAN, (self.x, self.y), 12)

        # Draw rotating lines that can bounce the ball
        for i in range(6):
            a = math.radians(self.angle + i * 60)
            x2 = self.x + math.cos(a) * self.line_length
            y2 = self.y + math.sin(a) * self.line_length

            # Pulsing line thickness
            thickness = 6 + int(math.sin(self.angle * 0.1 + i) * 2)
            pygame.draw.line(screen, PINK, (self.x, self.y), (x2, y2), thickness)

# =====================================================
# COMBO SYSTEM
# =====================================================

class ComboSystem:
    def __init__(self):
        self.combo = 0
        self.combo_timer = 0
        self.combo_freeze = 120  # frames before combo resets
        self.power_chain = ""
        self.chain_count = 0
        self.mega_power_active = False
        self.ball_split_ready = False
    
    def hit(self):
        self.combo += 1
        self.combo_timer = self.combo_freeze
        beep(400 + self.combo * 20, 50)
        
        # Trigger ball split at combo 15
        if self.combo >= 15:
            self.ball_split_ready = True
    
    def update(self):
        if self.combo_timer > 0:
            self.combo_timer -= 1
        else:
            self.combo = 0
        
        if self.mega_power_active:
            self.mega_power_active = False
    
    def get_multiplier(self):
        return 1 + (self.combo * 0.1)
    
    def add_power_chain(self, power_type):
        if power_type == self.power_chain:
            self.chain_count += 1
            if self.chain_count >= 3:
                self.mega_power_active = True
                self.chain_count = 0
                self.power_chain = ""
                beep(1000, 300)
        else:
            self.power_chain = power_type
            self.chain_count = 1

# =====================================================
# OBJECTS
# =====================================================

p1=Paddle(15,H//2-55,CYAN)  # Left edge, centered vertically with base height 110
p2=Paddle(W-37,H//2-55,PINK)  # Right edge, centered vertically (15 + 22 width = 37 from right)
ball=Ball()
core=Core()
combo = ComboSystem()

score1=0
score2=0
combo_score1 = 0
combo_score2 = 0

# =====================================================
# LOOP
# =====================================================

run=True
difficulty = 1.0

# Screen shake effect
screen_shake = 0
shake_intensity = 0

# Gravity waves
gravity_angle = 0
gravity_strength = 0
gravity_change_timer = 0

# Multiple balls for split mechanic
balls = [ball]

while run:
    clock.tick(60)

    for e in pygame.event.get():
        if e.type==pygame.QUIT:
            run=False

    keys=pygame.key.get_pressed()

    # movement
    p1.move(keys[pygame.K_w],keys[pygame.K_s])
    p1.update()

    if mode=="PVP":
        p2.move(keys[pygame.K_UP],keys[pygame.K_DOWN])
    else:
        # smarter AI with power-up awareness
        target = ball.y
        if p2.rect.centery < target - 30:
            p2.move(False,True)
        elif p2.rect.centery > target + 30:
            p2.move(True,False)

    p2.update()

    # DASH (interaction mechanic)
    if keys[pygame.K_a]:
        p1.dash()

    if mode=="PVP" and keys[pygame.K_LEFT]:
        p2.dash()

    # Gravity waves - change every 5 seconds
    gravity_change_timer -= 1
    if gravity_change_timer <= 0:
        gravity_angle = random.uniform(0, 2 * math.pi)
        gravity_strength = random.uniform(0.1, 0.4)
        gravity_change_timer = 300
    
    # Update core spinning
    core.update()
    
    # Handle multiple balls
    for ball in balls[:]:
        # Apply gravity waves with reduced strength
        grav_x = math.cos(gravity_angle) * gravity_strength * 0.3  # Reduced to 30% strength
        grav_y = math.sin(gravity_angle) * gravity_strength * 0.3
        ball.vx += grav_x
        ball.vy += grav_y
        
        ball.move()
        ball.update()
        
        # core influence
        core.affect_ball(ball)
    
    # Ball split at high combo
    if combo.ball_split_ready and len(balls) == 1:
        original_ball = balls[0]
        ball1 = Ball()
        ball1.x = original_ball.x
        ball1.y = original_ball.y
        ball1.vx = original_ball.vx * 0.7 + random.uniform(-3, 3)
        ball1.vy = original_ball.vy * 0.7 + random.uniform(-3, 3)
        
        ball2 = Ball()
        ball2.x = original_ball.x
        ball2.y = original_ball.y
        ball2.vx = original_ball.vx * 0.7 + random.uniform(-3, 3)
        ball2.vy = original_ball.vy * 0.7 + random.uniform(-3, 3)
        
        balls = [ball1, ball2]
        combo.ball_split_ready = False
        combo.combo = 0
        beep(800, 200)
        beep(600, 200)
        burst(original_ball.x, original_ball.y, CYAN, 50)
    
    # Merge balls if they get too close
    if len(balls) > 1:
        for i in range(len(balls)):
            for j in range(i+1, len(balls)):
                if math.hypot(balls[i].x - balls[j].x, balls[i].y - balls[j].y) < 30:
                    avg_x = (balls[i].x + balls[j].x) / 2
                    avg_y = (balls[i].y + balls[j].y) / 2
                    avg_vx = (balls[i].vx + balls[j].vx) / 2
                    avg_vy = (balls[i].vy + balls[j].vy) / 2
                    
                    new_ball = Ball()
                    new_ball.x = avg_x
                    new_ball.y = avg_y
                    new_ball.vx = avg_vx
                    new_ball.vy = avg_vy
                    
                    balls = [b for b in balls if b != balls[i] and b != balls[j]]
                    balls.append(new_ball)
                    burst(avg_x, avg_y, PURPLE, 30)
                    beep(700, 100)

    # Power-ups
    spawn_powerup()
    for pu in power_ups[:]:
        pu.update()
        pu_rect = pu.get_rect()
        
        # Check ball collision (catches yellow and other powerups)
        for ball in balls:
            ball_rect = pygame.Rect(ball.x - ball.r, ball.y - ball.r, ball.r * 2, ball.r * 2)
            if pu_rect.colliderect(ball_rect):
                if pu.power_type == "freeze":
                    ball.frozen_timer = 180
                    beep(500, 200)
                else:
                    # Apply to nearest paddle
                    dist_p1 = math.hypot(pu.x - p1.rect.centerx, pu.y - p1.rect.centery)
                    dist_p2 = math.hypot(pu.x - p2.rect.centerx, pu.y - p2.rect.centery)
                    if dist_p1 < dist_p2:
                        p1.apply_powerup(pu.power_type)
                        combo.add_power_chain(pu.power_type)
                    else:
                        p2.apply_powerup(pu.power_type)
                        combo.add_power_chain(pu.power_type)
                burst(pu.x, pu.y, pu.color_map[pu.power_type], 25)
                if pu in power_ups:
                    power_ups.remove(pu)
                break
        
        # Check paddle collisions (secondary)
        if pu_rect.colliderect(p1.rect):
            if pu.power_type == "freeze":
                for ball in balls:
                    ball.frozen_timer = 180
                beep(500, 200)
                burst(pu.x, pu.y, CYAN, 25)
            else:
                p1.apply_powerup(pu.power_type)
                combo.add_power_chain(pu.power_type)
            if pu in power_ups:
                power_ups.remove(pu)
            continue
              
        if pu_rect.colliderect(p2.rect):
            if pu.power_type == "freeze":
                for ball in balls:
                    ball.frozen_timer = 180
                beep(500, 200)
                burst(pu.x, pu.y, CYAN, 25)
            else:
                p2.apply_powerup(pu.power_type)
                combo.add_power_chain(pu.power_type)
            if pu in power_ups:
                power_ups.remove(pu)

    # paddle hit - check all balls
    for ball in balls[:]:
        br = pygame.Rect(ball.x - ball.r, ball.y - ball.r, ball.r * 2, ball.r * 2)
        
        # Only hit if cooldown is 0 to prevent spam
        if br.colliderect(p1.rect) and ball.paddle_collision_cd == 0:
            if not ball.frozen:
                ball.vx *= -1
                ball.vy += (ball.y - p1.rect.centery) * 0.05
                ball.paddle_collision_cd = 10  # 10 frames cooldown to prevent spam
                combo.hit()
                combo.add_power_chain(p1.power_type if hasattr(p1, 'power_type') else "normal")
                multiplier = combo.get_multiplier()
                
                # Screen shake on hit
                screen_shake = 8
                shake_intensity = 3
                
                burst(ball.x, ball.y, CYAN, 25)
                beep(500, 50)
            
            if p1.shield:
                p1.shield = False
                burst(p1.rect.centerx, p1.rect.centery, GREEN, 30)
        
        if br.colliderect(p2.rect) and ball.paddle_collision_cd == 0:
            if not ball.frozen:
                ball.vx *= -1
                ball.vy += (ball.y - p2.rect.centery) * 0.05
                ball.paddle_collision_cd = 10  # 10 frames cooldown to prevent spam
                combo.hit()
                combo.add_power_chain(p2.power_type if hasattr(p2, 'power_type') else "normal")
                multiplier = combo.get_multiplier()
                
                # Screen shake on hit
                screen_shake = 8
                shake_intensity = 3
                
                burst(ball.x, ball.y, PINK, 25)
                beep(500, 50)
            
            if p2.shield:
                p2.shield = False
                burst(p2.rect.centerx, p2.rect.centery, GREEN, 30)

    # difficulty scaling
    total_score = score1 + score2
    difficulty = 1.0 + (total_score / 100) * 0.2

    # scoring (capped at 12) - handle all balls
    for ball in balls[:]:
        if ball.x < 0:
            score2 = min(12, score2 + int(1 * combo.get_multiplier()))
            if score2 == 12:
                beep(800, 500)  # victory sound
                run = False  # Game over when score hits 12
            else:
                beep(200, 120)
            balls.remove(ball)
            if run:  # Only add new ball if game continues
                ball_new = Ball()
                balls.append(ball_new)
            combo.combo = 0
        
        if ball.x > W:
            score1 = min(12, score1 + int(1 * combo.get_multiplier()))
            if score1 == 12:
                beep(800, 500)  # victory sound
                run = False  # Game over when score hits 12
            else:
                beep(200, 120)
            balls.remove(ball)
            if run:  # Only add new ball if game continues
                ball_new = Ball()
                balls.append(ball_new)
            combo.combo = 0

    combo.update()

    # Screen shake effect
    shake_offset_x = 0
    shake_offset_y = 0
    if screen_shake > 0:
        screen_shake -= 1
        shake_offset_x = random.randint(-shake_intensity, shake_intensity)
        shake_offset_y = random.randint(-shake_intensity, shake_intensity)
    
    # draw
    screen.fill(BLACK)
    
    # Apply screen shake to drawing
    if shake_offset_x != 0 or shake_offset_y != 0:
        screen.scroll(shake_offset_x, shake_offset_y)
    
    # stars
    for s in stars:
        s[0]-=s[3]
        if s[0]<0:s[0]=W
        pygame.draw.circle(screen,(150,150,200),(int(s[0]),int(s[1])),s[2])

    # objects
    core.draw()
    p1.draw()
    p2.draw()
    
    # Draw all balls
    for ball in balls:
        ball.draw()
    
    draw_particles()
    
    # Power-ups
    for pu in power_ups:
        pu.draw()
    
    # UI
    screen.blit(big.render(f"{score1} : {score2}",True,WHITE),(W//2-70,20))
    
    # Combo display
    if combo.combo > 1:
        combo_text = f"COMBO x{combo.combo}!"
        combo_color = (255, int(100 + 155 * (combo.combo / 10)), 0)
        screen.blit(font.render(combo_text, True, combo_color), (W//2 - 80, 100))
    
    # Mega Power indicator
    if combo.mega_power_active:
        mega_text = "MEGA POWER!"
        screen.blit(big.render(mega_text, True, (255, 215, 0)), (W//2 - 150, 150))
    
    # Ball count display
    ball_text = f"Balls: {len(balls)}"
    screen.blit(small.render(ball_text, True, PURPLE), (W - 150, 10))
    
    # Gravity wave indicator
    grav_text = f"Gravity: {gravity_strength:.1f}"
    screen.blit(small.render(grav_text, True, ORANGE), (W - 150, 30))
    
    # Difficulty indicator
    diff_text = f"Difficulty: {difficulty:.1f}x"
    screen.blit(small.render(diff_text, True, CYAN), (10, 10))
    
    # Active effects display
    effects = []
    if p1.shield:
        effects.append("SHIELD")
    if p1.speed_boost > 1.0:
        effects.append("SPEED")
    if p1.size_boost > 1.0:
        effects.append("GROW")
    
    if effects:
        effect_text = " | ".join(effects)
        screen.blit(small.render(f"P1: {effect_text}", True, GREEN), (10, 35))
    
    effects = []
    if p2.shield:
        effects.append("SHIELD")
    if p2.speed_boost > 1.0:
        effects.append("SPEED")
    if p2.size_boost > 1.0:
        effects.append("GROW")
    
    if effects:
        effect_text = " | ".join(effects)
        screen.blit(small.render(f"P2: {effect_text}", True, YELLOW), (W - 250, 35))
    
    # Game over screen - wait for user input to return to menu
    if score1 == 12 or score2 == 12:
        game_over = True
        while game_over:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game_over = False
                    run = False
                if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    game_over = False
            
            screen.fill(BLACK)
            
            # Draw semi-transparent overlay
            overlay = pygame.Surface((W, H))
            overlay.set_alpha(200)
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (0, 0))
            
            # Game over text
            winner = "PLAYER 1" if score1 == 12 else "PLAYER 2"
            screen.blit(big.render("GAME OVER", True, (255, 215, 0)), (W//2 - 200, H//2 - 100))
            screen.blit(font.render(f"{winner} WINS!", True, (255, 215, 0)), (W//2 - 150, H//2 - 20))
            
            # Instructions
            screen.blit(small.render("Press any key to return to menu", True, CYAN), (W//2 - 150, H//2 + 80))
            
            pygame.display.update()
            clock.tick(60)
        
        run = False

    pygame.display.update()

pygame.quit()

# Return to menu after game ends
create_menu()