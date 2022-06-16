import pygame
import Load_Resources
from Utils.States import AnimatedState, StaticState

#define Entity de manera global
class GameEntity(pygame.sprite.Sprite):
    def __init__(self, display):
        super().__init__()

        self.display = display
        self.states_dict = {}
        self.current_state = None
        self.dx = 0
        self.dy = 0
        self.image = None
        self.jumping = False

    def set_current_state(self, key):
        self.current_state = self.states_dict[key]

    def impulse(self, dx, dy):
        self.dx = dx
        self.dy = dy

    def update(self, dt):
        raise NotImplementedError("El metodo update debe ser llamado en toda clase hija")

#Define jugador
class Player(GameEntity):
    def __init__(self, display, px, py):
        super(Player, self).__init__(display)

        self.speed = 3

        self.walking_images = pygame.image.load(Load_Resources.PlayerSprArchv)
        self.number_of_sprites = 3

        self.FontTxt = pygame.font.Font(None, 20)

        self.walking_right_state = AnimatedState(self.walking_images.subsurface(0, 32, self.walking_images.get_width(), 
                                                self.walking_images.get_height()/4), self.number_of_sprites, 300, "walking_right")
        self.walking_left_state = AnimatedState(self.walking_images.subsurface(0, 96, self.walking_images.get_width(), 
                                                self.walking_images.get_height()/4), self.number_of_sprites, 300, "walking_left")
        self.resting_right_state = StaticState(self.walking_images.subsurface(48, 32, self.walking_images.get_width()/3, self.walking_images.get_height()/4), "static_right")   
        self.resting_left_state = StaticState(self.walking_images.subsurface(0, 96, self.walking_images.get_width()/3, self.walking_images.get_height()/4), "static_left")         

        self.states_dict[self.walking_right_state.get_name()] = self.walking_right_state
        self.states_dict[self.walking_left_state.get_name()] = self.walking_left_state
        self.states_dict[self.resting_right_state.get_name()] = self.resting_right_state
        self.states_dict[self.resting_left_state.get_name()] = self.resting_left_state

        #Estado por defecto. Se define el Rect asociado al jugador y las coordenadas x e y
        self.set_current_state(self.resting_left_state.get_name())
        self.image = self.current_state.get_spr()
        self.rect = self.image.get_rect()
        self.rect.x = px
        self.rect.y = py
        self.rect.width = 16
        self.rect.move(4, 0)

    def calculate_gravity(self):
        self.dy = self.dy + 0.2

    def jump(self, jump_force):
        self.impulse(self.dx, -jump_force)

    #Eventos del teclado para el jugador
    def key_down(self, key):
        if key == pygame.K_UP:
            if not self.jumping:
                self.jump(6)
                self.jumping = True

        if key == pygame.K_RIGHT:
            self.dx = self.speed
            self.set_current_state(self.walking_right_state.get_name())

        if key == pygame.K_LEFT:
            self.dx = -self.speed
            self.set_current_state(self.walking_left_state.get_name())
        
        if key == pygame.K_LSHIFT:
            self.speed = 6

    def key_up(self, key):
        if key == pygame.K_UP:
           pass
        
        if key == pygame.K_RIGHT:
            if self.dx > 0:
                self.dx = 0
                self.set_current_state(self.resting_right_state.get_name())
        
        if key == pygame.K_LEFT:
            if self.dx < 0:
                self.dx = 0
                self.set_current_state(self.resting_left_state.get_name())
        
        if key == pygame.K_LSHIFT:
            self.speed = 3
    
    #Chequea colision con otro objeto y reacciona según sea el caso
    def check_collision(self, otherRect, type="solid"):
        IsCheck = False
        if self.rect.colliderect(otherRect) and type == "portal":
            print("collision with portal")
            IsCheck = True
        elif self.rect.colliderect(otherRect) and type == "damage":
            print("collision with spike")
            IsCheck = True
        elif self.rect.colliderect(otherRect) and type == "collectable":
            print("take coin")
            IsCheck = True
        elif self.rect.colliderect(otherRect) and type == "solid":           
            if self.rect.y > otherRect.y + (otherRect.height/2):
               self.rect.y = otherRect.y + (otherRect.height+1)
               self.jump(-1)                   
            elif self.rect.y + self.rect.height < otherRect.y + otherRect.height:
               self.rect.y = otherRect.y - (self.rect.height-1)
               self.jumping = False
               self.dy = 0            
            elif self.rect.x + self.rect.width < otherRect.x + (otherRect.width/2):
                self.rect.x = otherRect.x - (self.rect.width-1)
            elif self.rect.x + self.rect.width > otherRect.x + (otherRect.width/2):
                self.rect.x = otherRect.x + (otherRect.width+1)
            IsCheck = True
        elif self.rect.y + self.rect.height < self.display.get_height():
            self.jumping = True 
            IsCheck = False 
        else:
            IsCheck = False

        return IsCheck

    #Actualizacion frame a frame del jugador
    def update(self, dt):
        self.calculate_gravity()

        self.rect.x = self.rect.x + self.dx
        self.rect.y = self.rect.y + self.dy

        if self.rect.x + self.rect.width > self.display.get_width():
            self.rect.x = self.display.get_width()-self.rect.width
        if self.rect.x < 0:
            self.rect.x = 0
        if self.rect.y + self.rect.height > self.display.get_height():
            self.rect.y = self.display.get_height() - self.rect.height
            self.jumping = False
            self.dy = 0
        if self.rect.y < 0:
            self.rect.y = 0
            self.dy = 0
        
        self.current_state.update(dt)
        self.image = self.current_state.get_spr()
    
    #debug methods
    def draw_test(self):
        self.display.blit(self.image, (400, 300))

    def draw_pos(self):
        self.display.blit(self.FontTxt.render("Player Pos: " + str(self.rect.x) + " , " + str(self.rect.y) + "  "+ "Jumping: " + str(self.jumping), 
                                                0, pygame.Color("black")), (2,2))
    
    def checkColisionDebug(self, otherRect_debug):
        if self.rect.colliderect(otherRect_debug):
            self.display.blit(self.FontTxt.render("OtherObjectPos: " + str(otherRect_debug.x) + " , "+ str(otherRect_debug.y), 0, pygame.Color("black")), (2,25))
        else:
            self.display.blit(self.FontTxt.render("OtherObjectPos: None", 0, pygame.Color("black")), (2,25))

class SolidObjectSimple(pygame.sprite.Sprite):
    def __init__(self, color, x, y, width, height):
        super().__init__()

        self.typeObj = "solid"

        self.image = pygame.Surface((width, height))
        self.image.fill(color)

        self.rect = self.image.get_rect()

        self.rect.x = x
        self.rect.y = y

class Portal(GameEntity):
    def __init__(self, display, x, y):
        super(Portal, self).__init__(display)

        self.typeObj = "portal"

        self.AllImages = pygame.image.load(Load_Resources.PortalSpriteArchv)
        self.number_of_images = 3

        self.IdleState = AnimatedState(self.AllImages, self.number_of_images, 300, "Idle")
        self.states_dict[self.IdleState.get_name] = self.IdleState
        self.set_current_state(self.IdleState.get_name)

        self.image = self.current_state.get_spr()
        self.rect = self.image.get_rect()

        self.rect.x = x
        self.rect.y = y

    def update(self, dt):
        self.current_state.update(dt)
        self.image = self.current_state.get_spr()

class Spike(pygame.sprite.Sprite):
    def __init__(self, x, y, rotation=0):
        super().__init__()

        self.typeObj = "damage"

        self.image = pygame.image.load(Load_Resources.SpikeSpr)
        self.image = pygame.transform.rotate(self.image, rotation)

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y          
        if rotation == 0:
            self.rect.width = 12
            self.rect.height = 26
            self.rect.move(10, 4)
        elif rotation == 90:
            self.rect.width = 26
            self.rect.height = 12
            self.rect.move(4, 10)
        elif rotation == 180:
            self.rect.width = 12
            self.rect.height = 26
            self.rect.move(10, 0)
        elif rotation == 270:
            self.rect.width = 26
            self.rect.height = 12
            self.rect.move(0, 10)