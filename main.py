import pygame
from pygame.locals import *
import random

pygame.init()

clock = pygame.time.Clock()                                                     #to track game updates
fps = 50                                                                        #frames updated per sec

screen_width = 800
screen_height = 400

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Flappy Player')

# ----------------------------------------------------------
# REQUIRED FUNCTION DEFINITIONS
# ----------------------------------------------------------

def load_high_score():                                                          #read highscore from local file
    """Read highscore from file"""
    try:
        with open("highscore.txt", "r") as f:
            return int(f.read())
    except:
        return 0

def save_high_score(high_score):                                                #save highscore locally
    """save highscore in file"""
    with open("highscore.txt", "w") as f:
        f.write(str(high_score))

def hex_to_rgb(hex_code):                                                       #convert hex-> rgb for pygame colors
    """convert hex to rgb"""
    hex_code = hex_code.lstrip('#')
    return tuple(int(hex_code[i:i+2], 16) for i in (0, 2, 4))                   #R= 16h1+h2, G= 16h3+h4, B= 16h5+h6

def draw_text(text, font, text_col, x, y, outline_col=(0, 0, 0)):
    """Render text with outline (boundary)"""
    text_surface = font.render(text, True, text_col)                       #create a surface by turning text into drawable img with smooth edges
    
    outline_surface = font.render(text, True, outline_col)                 #create another surface with same text but with outline color

    screen.blit(outline_surface, (x - 2, y))                               #draw outline text in all 4 directions as boundaries
    screen.blit(outline_surface, (x + 2, y))
    screen.blit(outline_surface, (x, y - 2))
    screen.blit(outline_surface, (x, y + 2))

    screen.blit(text_surface, (x, y))                                      #draw main text on top


# ----------------------------------------------------------
# GAME VARIABLES
# ----------------------------------------------------------

font = pygame.font.SysFont('Bauhaus 93', 60)                                #required font and its size
font2 = pygame.font.SysFont('Bauhaus 93', 30)

white = hex_to_rgb("#3FF445")                                             #color conversion
high=hex_to_rgb("#b4d7f9")

ground_scroll = 0                                                           #tracking ground img horizontal movement
scroll_speed = 3                                                            #Controls how fast the ground and pipes move to the left.

flying = False                                                              #track if player is flying
game_over = False                                                           #track if game over

pipe_gap = 230                                                              # vertical distance between pipes (increase for easier gameplay)
pipe_frequency = 2000                                                       # time between new pipes: new pipes appear every 2 seconds
last_pipe = pygame.time.get_ticks() - pipe_frequency                        # show pipe when game starts instead of waiting for 2 seconds

score = 0                                                                   #user score track
pass_pipe = False                                                           #track if user passed a pipe for score to increase

high_score = load_high_score()                                              #load highscore locally

# ----------------------------------------------------------
# LOAD IMAGES
# ----------------------------------------------------------

bg = pygame.image.load('img/bg3.jpg')                                        #load image using pygame
bg = pygame.transform.scale(bg, (800, 400))                                  #scale accordingly for (w,h)

ground_img = pygame.image.load('img/ground4.jpg')
ground_img = pygame.transform.scale(ground_img, (1000, 400))

button_img = pygame.image.load('img/reset.png')
button_img = pygame.transform.scale(button_img, (100, 50))

# ----------------------------------------------------------
# GAME HELPER FUNCTIONS
# ----------------------------------------------------------

def reset_game():
    """Reset game variables after game over"""
    global flying, pass_pipe                                                  #function will modify variables globally
    pipe_group.empty()                                                        #clear all pipes
    flappy.rect.x = 100                                                       #reset player in initial position
    flappy.rect.y = 200
    flying=False                                                              #reset flying state: so player doesn’t start moving automatically
    pass_pipe=False                                                           #reset pipes passed
    score = 0                                                                 #reset score
    return score

# ----------------------------------------------------------
# PLAYER CLASS AS BIRD
# ----------------------------------------------------------

class Bird(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)                   #inherits from pygame.sprite.Sprite — making it part of Pygame’s sprite system
        self.images = []                                      #list to store all image frames                
        self.index = 0                                        #track cur img
        self.counter = 0                                      #control animation speed to switch frames

        # Load flapping animation frames
        for num in range(1, 9):
            img = pygame.image.load(f'img/luffy{num}.png')
            img = pygame.transform.scale(img, (70, 70))
            self.images.append(img)                             #add all images to list

        self.image = self.images[self.index]                    #cur img
        self.rect = self.image.get_rect()                       #create a rectangle around this img
        self.rect.center = [x, y]                               #set position for img

        self.vel = 0                                            #vertical velocity track for gravity and jumps

    def update(self):
        global flying, game_over

        # Apply gravity only when flying
        if flying:
            self.vel += 0.5                                     # gradually increase velocity to pull bird downward for gravity while flying
            if self.vel > 8:                                    #limit to max fall speed: prevents the bird from falling too fast
                self.vel = 8
            if self.rect.bottom < 350:
                self.rect.y += int(self.vel)                    #stop before going below ground
            else:
                self.rect.bottom = 350                          # prevent falling through ground

        # Animate bird
        if not game_over:
            self.counter += 1                                   #count for frame change interval
            flap_cooldown = 8                                   #controls how fast the frames flap (every 4 frames)

            #When counter passes cooldown, advance to the next frame.
            if self.counter > flap_cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images):
                    self.index = 0                              #loop back to first frame when all are shown

            # Tilt based on velocity
            self.image = self.images[self.index]
            self.image = pygame.transform.rotate(self.image, -self.vel * 2)
                                                                #Rotates the player slightly upward when going up, and downward when falling
        else:
            self.image = pygame.transform.rotate(self.images[self.index], -90)
                                                                #when game is over, rotate to get a fall effect

# ----------------------------------------------------------
# PIPE CLASS
# ----------------------------------------------------------

class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, y, position):
        pygame.sprite.Sprite.__init__(self)
        pipe_img = pygame.image.load('img/pipe.png')
        pipe_img = pygame.transform.scale(pipe_img, (40, 100))
        self.image = pipe_img
        self.rect = self.image.get_rect()

        # position 1 = top pipe, -1 = bottom pipe
        if position == 1:
            self.image = pygame.transform.flip(self.image, False, True)         #For top pipes, flip the image vertically
            self.rect.bottomleft = [x, y - int(pipe_gap / 2)]                   #position it above the gap
        if position == -1:
            self.rect.topleft = [x, y + int(pipe_gap / 2)]                      #position it below the gap

    def update(self):
        self.rect.x -= scroll_speed                                             # move pipes leftwards
        if self.rect.right < 0:
            self.kill()                                                         #Deletes the pipe when it moves off-screen

# ----------------------------------------------------------
# BUTTON CLASS
# ----------------------------------------------------------

class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)                              #rect defines clickable area

    def draw(self):
        """Draw button and return True if clicked"""
        action = False                                          #track button press action 
        pos = pygame.mouse.get_pos()                            #cur mouse position of user
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1:
                action = True                                    #if mouse is over the button and left click is pressed the set action for reset
        screen.blit(self.image, (self.rect.x, self.rect.y))      #draw button on screen
        return action

# ----------------------------------------------------------
# SPRITE GROUPS: helps manage and update multiple game objects
#   helps to Draw all sprites at once, 
#            Update all sprites together using .update(), 
#            Detect collisions between groups using built-in functions.
# ----------------------------------------------------------

bird_group = pygame.sprite.Group()
pipe_group = pygame.sprite.Group()

flappy = Bird(100, int(screen_height / 2))
bird_group.add(flappy)                                       #create user instance and keep it in group at start itself

button = Button(screen_width // 2 - 50, screen_height // 2 - 100, button_img)

# ----------------------------------------------------------
# MAIN GAME LOOP
# ----------------------------------------------------------

run = True                                                   #keep game screen running
while run:
    clock.tick(fps)                                         #control frame rate
    screen.blit(bg, (0, 0))                                 #draw bg

    # Draw sprites
    bird_group.draw(screen)                                 #draw user
    bird_group.update()                                     #draw all user animations
    pipe_group.draw(screen)                                 #draw cur active pipes
    screen.blit(ground_img, (ground_scroll, 350))           #draw ground

    # ------------------------------------------------------
    # SCORE CALCULATION 
    # ------------------------------------------------------
    if len(pipe_group) > 0:                                 #run logic only if pipe exists on screen
        bottom_pipe=None
        for pipe in pipe_group:
            if pipe.rect.bottom>screen_height/2:
                bottom_pipe=pipe                            #find bottom pipe to increment score acc to pair
                break

        if bottom_pipe:
            if not pass_pipe and flappy.rect.left > bottom_pipe.rect.left and flappy.rect.right<bottom_pipe.rect.right+50:
                pass_pipe=True                              #check if user entered area between pipes

            if pass_pipe and flappy.rect.left > bottom_pipe.rect.right:
                score+=10
                pass_pipe=False                             #after passing pipe pair increment score and reset the pair

            if score > high_score:
                high_score = score


    #-----------------------------------------
    # The for loop finds that pipe.

    # The bird crosses its right edge → triggers score += 10.

    # The next frame, the same pipe pair’s top pipe is ignored (since you only check bottom pipes).

    # The next bottom pipe appears and will again increment the score — even if the player hasn’t passed a complete pair visually yet.

    # So visually it feels like the score increments “too early” — after the bird crosses only one pipe — but in your logic, that one bottom pipe represents a full pair.
    #---------------------------------------------


    draw_text(str(score), font, white, int(screen_width / 2), 20)

    draw_text(f"High: {high_score}", font2, high, screen_width - 175, 10)

    # ------------------------------------------------------
    # COLLISION DETECTION
    # ------------------------------------------------------
    if pygame.sprite.groupcollide(bird_group, pipe_group, False, False):#Checks if the bird collides with any pipe
        game_over = True

    if flappy.rect.top<0:
        flappy.rect.top=0
        flappy.vel=0
                                            #Prevents the bird from flying above the top edge. Resets vertical velocity when that happens.

    if flappy.rect.bottom > 350:
        flying = False
        game_over=True
                                            #game over if user touches ground

    # ------------------------------------------------------
    # PIPE GENERATION AND MOVEMENT
    # ------------------------------------------------------
    if not game_over and flying:
        time_now = pygame.time.get_ticks()
        if time_now - last_pipe > pipe_frequency:           #Checks if it’s time to spawn a new pair of pipes (based on elapsed time).
            pipe_height = random.randint(-100, 100)
            bottom_pipe = Pipe(screen_width, int(screen_height / 2) + pipe_height, -1)
            top_pipe = Pipe(screen_width, int(screen_height / 2) + pipe_height, 1)
                                                            #Generates new top and bottom pipes with random vertical offsets.
            pipe_group.add(bottom_pipe)
            pipe_group.add(top_pipe)
            last_pipe = time_now
                                                            #Adds new pipes to the pipe_group and updates the timestamp for the last pipe spawn.

        ground_scroll -= scroll_speed                       #Moves the ground image leftward to simulate forward motion.
        if abs(ground_scroll) > 200:
            ground_scroll = 0

        pipe_group.update()                                 #Moves all pipes leftward, Removes pipes that go off-screen.

    # ------------------------------------------------------
    # GAME OVER / RESET
    # ------------------------------------------------------
    if game_over:
        if button.draw():
            game_over = False
            score = reset_game()

    # ------------------------------------------------------
    # EVENT HANDLING
    # ------------------------------------------------------
    for event in pygame.event.get():
        if event.type == pygame.QUIT:                       #If the player closes the game window, stop the main loop.
            run = False

        # SPACE key controls
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if not flying and not game_over:
                    flying = True
                    flappy.vel = -10                        # start game and jump
                elif not game_over:
                    flappy.vel = -10                        # jump mid-game each time spacebar is pressed.

    pygame.display.update()

save_high_score(high_score)
pygame.quit()
