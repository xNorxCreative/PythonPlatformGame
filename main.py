import pygame
import Load_Resources
import Entities.UI_entities as ui
from Maps.Map import Map
from pygame.locals import *

#Inicialize parameters
pygame.init() 
pygame.mixer.init()
ScreemLentgh = (800, 600)
window = pygame.display.set_mode(ScreemLentgh)
pygame.display.set_caption("Platform Game")

#Constantes y variables globales
MAX_LEVEL = len(Load_Resources.MapsDirectory)
SCENES = {"Menu":-1, "Levels":0, "GameOver":1, "Finish":2}
Lives = 3
Score = 0

#Define clase principal
class Main(object):
    #Parametros iniciales (setup)
    def __init__(self, *globals):
        self.Clock = pygame.time.Clock()
        self.running = True
        self.SpriteList = pygame.sprite.Group()

        #Variables globales pasados como parámetro en el constructor
        self.Lives = globals[0]
        self.Score = globals[1]

        self.GameFont = pygame.font.Font(None, 20) #Font del juego

        #Sonidos
        self.CoinSFX = pygame.mixer.Sound(Load_Resources.CoinTake)
        self.PortalSFX = pygame.mixer.Sound(Load_Resources.PortalEnter)
        self.DmgSFX = pygame.mixer.Sound(Load_Resources.DmgTake)

        #Definimos elementos para interface gráfica
        # - Menú UI
        self.MenuBG = ui.Image(pygame.image.load(Load_Resources.MenuBG), 0, 0, ScreemLentgh[0], ScreemLentgh[1])
        self.button1 = ui.Button(pygame.image.load(Load_Resources.Button1[0]), ScreemLentgh[0]/2-50, ScreemLentgh[1]/2)
        self.cursor = ui.Cursor()
        # - Levels UI
        self.PlayerImage = ui.Image(pygame.image.load(Load_Resources.PlayerSprArchv).subsurface(24, 64, 24, 32), 32, 32)
        self.CoinUI = ui.Image(pygame.image.load(Load_Resources.CoinSpr), 34, 70, 24, 26)
        self.UiLives = ui.TextBox(68, 44, self.GameFont, "", Color("white"))
        self.Coincount = ui.TextBox(68, 80, self.GameFont, "", Color("white"))
        # - GameOver UI/Finish UI
        self.backgroundGameOver = ui.Image(pygame.image.load(Load_Resources.GameOverBG), 0, 0, ScreemLentgh[0], ScreemLentgh[1])
        self.FinishBG = ui.Image(pygame.image.load(Load_Resources.FinishBG), 0, 0, ScreemLentgh[0], ScreemLentgh[1])
        self.CoinUI2 = ui.Image(pygame.image.load(Load_Resources.CoinSpr), ScreemLentgh[0]/2-70, ScreemLentgh[1]/2+100, 72, 78)
        self.CoincountLast = ui.TextBox(ScreemLentgh[0]/2-70+78, ScreemLentgh[1]/2+134, pygame.font.Font(None, 35), "Total: ", Color("black"))

        self.ListMaps = [] #Almacena todos los niveles que contendrá el juego
        self.Actuallvl = -1 #El nivel actual del juego. Por defecto es -1 (ningún nivel cargado)
        self.ActualScene = SCENES["Menu"] # id de la escena actual, por defecto es -1 (referente al menú inicial)

        for map_id in range(MAX_LEVEL):
            self.ListMaps.append(Map((32,30), Load_Resources.MapsDirectory[map_id]))
            
        #Entidades especiales y lista de entidades 
        self.AllEntities = None 
        self.player = None
        self.portal = None 
        
    #Ejecucion del juego
    def Play(self):
        #Variables para control de flujo
        Blockcolision = False #para colision con bloques
        Damage = False #para colision con pinchos
        take = False #Para collectables
        LoadedEntities = False #Para evaluar carga de los recursos para la escena
        LastScore = self.Score #Para resetear el score al ultimo obtenido desde el nivel anterior

        #Ciclo principal
        while self.running:
            #Si la escena es Levels (un nivel del juego)
            if self.ActualScene == SCENES["Levels"]:

                if not LoadedEntities:
                    self.map = self.ListMaps[self.Actuallvl]

                    self.AllEntities = self.map.GenerateEntities(window)
                    self.player = self.AllEntities["Player"]
                    self.portal = self.AllEntities["Portal"]

                    for block in self.AllEntities["BlockSimple"]:
                        self.SpriteList.add(block)
                    for spike in self.AllEntities["Spike"]:
                        self.SpriteList.add(spike)
                    for coin in self.AllEntities["Coin"]:
                        self.SpriteList.add(coin)
            
                    self.SpriteList.add(self.player)
                    self.SpriteList.add(self.portal)

                    self.SpriteList.add(self.PlayerImage)
                    self.SpriteList.add(self.UiLives)
                    self.SpriteList.add(self.CoinUI)
                    self.SpriteList.add(self.Coincount)
                    
                    print("Sprite list content: " + str(self.SpriteList))#Debug content
                    LoadedEntities = True

                #Fondo del mapa
                window.fill(Color("grey20"))

                #check colision with player
                for checkBlock in self.AllEntities["BlockSimple"]:
                    Blockcolision = self.player.check_collision(checkBlock.rect, checkBlock.typeObj)
                    if Blockcolision:
                        break
            
                #Evaluacion de eventos
                for event in pygame.event.get():
                    if event.type == QUIT or event.type == KEYDOWN:
                        if event.key == pygame.K_ESCAPE or event.mod == pygame.KMOD_NONE:
                            self.running = False
                        self.player.key_down(event.key)
                    if event.type == KEYUP:
                        self.player.key_up(event.key)

                 #Tiempo que dura entre frame y frame del juego
                DeltaT = self.Clock.tick(60) 
                self.player.update(DeltaT)
                self.portal.update(DeltaT)

                #check collision with portal and other entities
                if self.player.check_collision(self.portal.rect, self.portal.typeObj):
                    self.Actuallvl += 1
                    self.PortalSFX.play()
                    if self.Actuallvl < MAX_LEVEL:
                        LoadedEntities = False
                        self.Lives = Lives #Reset Lives
                        LastScore = self.Score
                        self.SpriteList.empty()#Limpiamos la lista de sprites
                        print("cleared list: " + str(self.SpriteList))#Debug
                    else:
                        LoadedEntities = False
                        self.SpriteList.empty()
                        self.Actuallvl = -1
                        self.ActualScene = SCENES["Finish"]
                for checkCoin in self.AllEntities["Coin"]:
                    take = self.player.check_collision(checkCoin.rect, checkCoin.typeObj)
                    if not take:
                        continue
                    else:
                        self.Score += checkCoin.value
                        if checkCoin.value != 0:
                            self.CoinSFX.play()
                        checkCoin.took()
                        self.SpriteList.remove(checkCoin)
                        break
                for checkSpike in self.AllEntities["Spike"]:
                    Damage = self.player.check_collision(checkSpike.rect, checkSpike.typeObj)
                    if not Damage:
                        continue
                    else:
                        self.Lives -= 1
                        LoadedEntities = False
                        self.SpriteList.empty()
                        self.DmgSFX.play()
                        self.Score = LastScore
                        if self.Lives == 0:
                            self.Lives = Lives
                            self.Actuallvl = -1
                            self.ActualScene = SCENES["GameOver"]
                        break
                
                self.Coincount.updateText(str(self.Score))
                self.UiLives.updateText(str(self.Lives))
                self.SpriteList.draw(window)
    
            #Si la escena es Menu (por defecto)
            if self.ActualScene == SCENES["Menu"]:

                self.cursor.update() #Actualiza ubicacion del cursor en el display
                
                #Fondo del mapa
                window.fill(Color("gray"))

                #Cargar elementos a dibujar
                if not LoadedEntities:
                    pygame.mixer.music.load(Load_Resources.MusicBG1Archv) #Load BGM
                    pygame.mixer.music.play(-1) #Play music 
                    self.SpriteList.add(self.MenuBG)
                    self.SpriteList.add(self.button1)
                    print("Sprite list content: "+ str(self.SpriteList))#Debug content
                    LoadedEntities = True

                #Evaluacion de eventos
                for event in pygame.event.get():
                    if event.type == QUIT or event.type == KEYDOWN:
                        if event.key == pygame.K_ESCAPE or event.mod == pygame.KMOD_NONE:
                            self.running = False
                            
                    if event.type == pygame.MOUSEMOTION:
                        self.button1.CursorDetect(self.cursor, pygame.image.load(Load_Resources.Button1[1]), pygame.image.load(Load_Resources.Button1[0]))
                    
                    if event.type == pygame.MOUSEBUTTONDOWN and self.button1.OnClick(event.button):
                        LoadedEntities = False
                        self.SpriteList.empty()
                        self.Actuallvl += 1
                        self.ActualScene = SCENES["Levels"]

                self.SpriteList.draw(window)   

            #Si la escena es Finish
            if self.ActualScene == SCENES["Finish"]:

                #Fondo del mapa
                window.fill(Color("cornsilk3"))

                #Cargar elementos al dibujar
                if not LoadedEntities:
                    pygame.mixer.music.load(Load_Resources.FinishBGM) #Load BGM for Game over
                    pygame.mixer.music.play(-1) #Play music
                    self.SpriteList.add(self.FinishBG)
                    self.SpriteList.add(self.CoinUI2)
                    self.SpriteList.add(self.CoincountLast)
                    LoadedEntities = True

                #Evaluacion de eventos
                for event in pygame.event.get():
                    if event.type == QUIT or event.type == KEYDOWN:
                        if event.key == pygame.K_ESCAPE or event.mod == pygame.KMOD_NONE:
                            self.running = False      
                self.CoincountLast.updateText("Total: "+str(self.Score))
                self.SpriteList.draw(window)   
            
            #Si la escena es GameOver
            if self.ActualScene == SCENES["GameOver"]:

                #Fondo del mapa
                window.fill(Color("cornsilk3"))

                #Cargar elementos al dibujar
                if not LoadedEntities:
                    pygame.mixer.music.load(Load_Resources.MusicGameOver) #Load BGM for Game over
                    pygame.mixer.music.play(-1) #Play music
                    self.SpriteList.add(self.backgroundGameOver) 
                    self.SpriteList.add(self.CoinUI2)
                    self.SpriteList.add(self.CoincountLast)
                    LoadedEntities = True

                #Evaluacion de eventos
                for event in pygame.event.get():
                    if event.type == QUIT or event.type == KEYDOWN:
                        if event.key == pygame.K_ESCAPE or event.mod == pygame.KMOD_NONE:
                            self.running = False  
                        elif event.key == K_SPACE:
                            self.SpriteList.empty()
                            LoadedEntities = False
                            self.Score = Score #Reset score
                            self.ActualScene = SCENES["Menu"]

                self.CoincountLast.updateText("Total: "+str(self.Score))
                self.SpriteList.draw(window)   
            
            pygame.display.flip()
        pygame.quit()

if __name__ == "__main__":
    m = Main(Lives, Score)
    m.Play()