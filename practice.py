import pygame
import random
import sys

#initialising pygame
pygame.init()

#to get the screen dimension
info = pygame.display.Info()
screen_width = info.current_w // 2  
screen_height = info.current_h // 2  

#for display
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Brick Breaker 2.0")

#background
BG = pygame.image.load('background.png')
BG = pygame.transform.scale(BG, (screen_width, screen_height))  

#was trying to add another picture but stuck with the bg one
congrats_bg = pygame.image.load('background.png')
congrats_bg = pygame.transform.scale(congrats_bg, (screen_width, screen_height))  #to match screen size

#all the music used in the game
pygame.mixer.music.load('/home/shria-nair/Documents/amfoss2/background.mp3')  
pygame.mixer.music.play(-1)  #to loop bg music
hit_sound = pygame.mixer.Sound('/home/shria-nair/Documents/amfoss2/bowling-ball-90863.mp3')  #paddle hit sound
brick_break_sound = pygame.mixer.Sound('brick_break_sound.mp3')  # brickbreak sound
game_over_sound = pygame.mixer.Sound('/home/shria-nair/Documents/amfoss2/nevergonna.MP3')  #gameoversound
win_sound =pygame.mixer.Sound('/home/shria-nair/Documents/amfoss2/goodresult-82807.mp3') #victory sound
menu_sound = pygame.mixer.Sound('/home/shria-nair/Documents/amfoss2/menu.mp3') #menu sound

#font
font = pygame.font.SysFont('comicsans', 100)

#button class for menu
class Button():
    def __init__(self, image, pos, text_input, font, base_color, hovering_color):
        self.image = image
        self.x_pos = pos[0]
        self.y_pos = pos[1]
        self.font = font
        self.base_color, self.hovering_color = base_color, hovering_color
        self.text_input = text_input
        self.text = self.font.render(self.text_input, True, self.base_color)
        if self.image is None:
            self.image = self.text
        self.rect = self.image.get_rect(center=(self.x_pos, self.y_pos))
        self.text_rect = self.text.get_rect(center=(self.x_pos, self.y_pos))

    def update(self, screen):
        if self.image is not None:
            screen.blit(self.image, self.rect)
        screen.blit(self.text, self.text_rect)

    def checkForInput(self, position):
        return self.rect.collidepoint(position)

    def changeColor(self, position):  # color change when hovered on play
        if self.rect.collidepoint(position):
            self.text = self.font.render(self.text_input, True, self.hovering_color)
        else:
            self.text = self.font.render(self.text_input, True, self.base_color)

# paddle class
class Paddle:
    def __init__(self, x, y, color=(255, 255, 0)):
        self.rect = pygame.Rect(x, y, 120, 15)
        self.color = color

    def draw(self, screen):
        #gradient effect
        for i in range(self.rect.height):
            shade = max(0, self.color[0] - i * 8)  #3D effect
            gradient_color = (shade, shade, shade)
            pygame.draw.line(screen, gradient_color, 
                             (self.rect.left, self.rect.top + i), 
                             (self.rect.right, self.rect.top + i))
        border_color =  (255,255,255)
        pygame.draw.rect(screen, border_color, self.rect, 2)  

    def move(self, speed=23):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.move_ip(-speed, 0)
        if keys[pygame.K_RIGHT] and self.rect.right < screen_width:
            self.rect.move_ip(speed, 0)

# brick class
class Brick:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
#random color
        self.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        top_rect = pygame.Rect(self.rect.x, self.rect.y, self.rect.width, 5)
        top_color = (min(self.color[0] + 60, 255), min(self.color[1] + 60, 255), min(self.color[2] + 60, 255))
        pygame.draw.rect(screen, top_color, top_rect)
        side_rect = pygame.Rect(self.rect.right - 5, self.rect.y, 5, self.rect.height)
        side_color = (max(self.color[0] - 60, 0), max(self.color[1] - 60, 0), max(self.color[2] - 60, 0))
        pygame.draw.rect(screen, side_color, side_rect)

# ball class
class Ball:
    def __init__(self, x, y, radius=10, color=(255, 255, 0)):
        self.start_x = x
        self.start_y = y
        self.radius = radius
        self.rect = pygame.Rect(x - radius, y - radius, radius * 2, radius * 2)
        self.dx, self.dy = 4, -4 # initial ball speed
        self.speed_increment = 1.02  # increase after each collision

        self.ready = True  #if the ball is ready to start moving

    def reset(self, paddle_x, paddle_y):
        self.rect.x = paddle_x + 60 - self.radius
        self.rect.y = paddle_y - self.radius * 2
        self.dx, self.dy = 0, 0
        self.ready = True  # ball is on the paddle and ready for launch
    def draw(self, screen):
        for i in range(self.radius, 0, -1):
            shade = int(255 - (i / self.radius) * 100)  
            pygame.draw.circle(screen, (shade, shade, shade), self.rect.center, i)

    def move(self):
        if not self.ready:
            self.rect.move_ip(self.dx, self.dy)

    def bounce(self, paddle, bricks):
        
        if self.rect.left <= 0 or self.rect.right >= screen_width:
            self.dx *= -1  #reverse horizontal direction
        if self.rect.top <= 0:
            self.dy *= -1  #reverse vertical direction
        if self.rect.colliderect(paddle.rect) and self.dy > 0:
            self.dy *= -1
            hit_sound.play() #hitting sound plays
    
            self.dx *= self.speed_increment
            self.dy *= self.speed_increment
        hit_brick = self.rect.collidelist(bricks)
        if hit_brick != -1:
            self.dy *= -1
            brick_break_sound.play()
            # Gradually increase the speed after hitting a brick
            self.dx *= self.speed_increment
            self.dy *= self.speed_increment
            return hit_brick
        return None

# game class
class BreakoutGame:
    def __init__(self, width=800, height=600):
        self._font = pygame.font.Font(None, 36)
        self._score = 0
        self.level = 1
        self.game_over = False
        self.game_started = False

        self._width = width
        self._height = height
        self._screen = pygame.display.set_mode((width, height))
        self._clock = pygame.time.Clock()
        self._paddle = Paddle(width / 2 - 60, height - 20)
        self._ball = Ball(width / 2, height / 2, radius=15)
        self._lives = 3
        self._reset_bricks()
        self.reset_game() 

    def display_level_complete_message(self):  # to display victory message
        while True:
            self._screen.blit(congrats_bg, (0, 0))  # Clear the screen
            level_complete_text = self._font.render(
                "CONGRATS! YOU BRICKED UP THEM BRICKS HAHA LETS GO", True, (255, 255, 255))
            press_key_text = self._font.render(
                "Press any key to move your keys again ;)" + str(self.level + 1), True, (255, 255, 255))

            self._screen.blit(level_complete_text, 
                              (self._width // 2 - level_complete_text.get_width() // 2, self._height // 2 - 20))
            self._screen.blit(press_key_text, 
                              (self._width // 2 - press_key_text.get_width() // 2, self._height // 2 + 20))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    self._ball.reset(self._paddle.rect.x, self._paddle.rect.y)
                    
                    self._reset_bricks()

                    return  

            pygame.display.flip()
            self._clock.tick(60)

    def _reset_bricks(self):
        self._bricks = []
        brick_width = screen_width // 8
        brick_height = screen_height // 17
        rows = 5
        gap = 8
        for i in range(rows):
            for j in range(8):
                x = j * (brick_width + gap)
                y = i * (brick_height + gap)
                self._bricks.append(Brick(x, y, brick_width, brick_height))

    def _draw_text(self, text, pos):
        surface = self._font.render(text, True, (255, 255, 255))
        rect = surface.get_rect(center=pos)
        self._screen.blit(surface, rect)

    def run_game(self): #main loop
        pygame.mixer.music.play(-1)  #for bg music
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if self.game_over:
                        # Reset the game when game is over and any key is pressed
                        self.reset_game()
                        pygame.mixer.music.play(-1)
                        game_over_sound.stop()
                    elif not self.game_started:
                        
                        # Start the game if it's not started yet
                        self.game_started = True
                        self._ball.dx, self._ball.dy = 5, -5  
                        self._ball.ready = False
                        menu_sound.stop()
                       
                    elif self._ball.ready:
                        # Launch the ball when it's ready
                        self._ball.dx, self._ball.dy = 5, -5
                        self._ball.ready = False

            self._paddle.move()

            if self.game_started and not self.game_over:
                if not self._bricks:
                    pygame.mixer.music.stop()
                    win_sound.play()
                    self.display_level_complete_message()
                    self.reset_game() 
                     
                    self.level += 1
                    self._ball.dx *= 1.2  # Increase ball speed on level up
                    self._ball.dy *= 1.2  # Increase ball speed on level up
                    self._reset_bricks()
                    self._ball.reset(self._paddle.rect.x, self._paddle.rect.y)

                self._ball.move()
                hit_brick = self._ball.bounce(self._paddle, self._bricks)
                if hit_brick is not None:
                    del self._bricks[hit_brick]
                    self._score += 5
                if self._ball.rect.top > self._height:
                    self._lives -= 1
                    self._ball.reset(self._paddle.rect.x, self._paddle.rect.y)
                    if self._lives == 0:
                        self.game_over = True

            self._screen.blit(BG, (0, 0))
            self._paddle.draw(self._screen)
            self._ball.draw(self._screen)
            for brick in self._bricks:
                brick.draw(self._screen)

            if self.game_over:
                pygame.mixer.music.stop() #bg music stops
                game_over_sound.play() #game over music starts
                self._draw_text("Womp Womp! CRY ABOUT IT. Game Over!", (self._width // 2, self._height // 2 - 20))
                self._draw_text("Score: " + str(self._score), (self._width // 2, self._height // 2 + 20))
                self._draw_text("Press any key to RESTART and be good at it :)", (self._width // 2, self._height // 2 + 60))
            
            self._draw_text("Lives: " + str(self._lives), (self._width - 70, 500))
            self._draw_text("Score: " + str(self._score), (70, 500))
            
            pygame.display.flip()
            self._clock.tick(60)

    def reset_game(self):
        self._lives = 3
        self.level = 1
        self._score = 0
        
        self._bricks.clear()
        self._reset_bricks()
        self.game_over = False
        self.game_started = False
        self._ball.reset(self._paddle.rect.x, self._paddle.rect.y)
        pygame.mixer.music.play(-1)
        
def main_menu(): #menu that comes in the beginning
    instruction_font = pygame.font.Font(None, 30)  # small size for instructions

    while True:
        menu_sound.play()
        screen.blit(BG, (0, 0))
        menu_text = font.render("BATTLE OF THE BRICKS", True, "WHITE")
        menu_rect = menu_text.get_rect(center=(screen_width // 2, screen_height // 4))

        screen.blit(menu_text, menu_rect)
        instruction_text = instruction_font.render("Press the button below to start playing!", True, "WHITE")
        instruction_rect = instruction_text.get_rect(center=(screen_width // 2, screen_height // 2.5))
        screen.blit(instruction_text, instruction_rect)



        play_button = Button(image=None, pos=(screen_width // 2, screen_height // 1.5), text_input="PLAY",
                             font=font, base_color="white", hovering_color="yellow")
        play_button.update(screen)

        menu_mouse_pos = pygame.mouse.get_pos()
        play_button.changeColor(menu_mouse_pos)
        play_button.update(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                menu_sound.stop()
                if play_button.checkForInput(menu_mouse_pos):
                    game = BreakoutGame(screen_width, screen_height)
                    game.run_game()
                   

        pygame.display.flip()

if __name__ == "__main__":
    main_menu() 

   
