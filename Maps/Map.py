import pygame
from Entities.entities import *
from Colectables.Coin import coin

class Map:
    def __init__(self, cell_size, nameFileMap):
        self.nameMap = nameFileMap
        self.cellSize = cell_size 
        self.dataMap = None

        filemap = open(self.nameMap, "r")
        dataMap = filemap.readlines() #Es un arreglo de strings, contiene el siguiente formato:
                                      #      X = Bloques simples
                                      #      P = Player 
                                      #      F = Portal
                                      #      O = vacío
                                      #      1 = Spike up
                                      #      2 = Spike left
                                      #      3 = Spike Down
                                      #      4 = Spike Right
                                      #      C = Coin
                                      #      other = por definir
        dataMapFormat = []
        for i in dataMap:
            dataMapFormat.append(i[:-2]) #Se elimina el salto de línea al final de cada fila de string
        self.dataMap = dataMapFormat
        filemap.close()

        self.colorBlock = pygame.Color("black")
        self.EntitiesInMap_dict = {} #Contendrá las entidades que se ocuparan en el mapa segun self.dataMap
                                     #Keys: Player = Contiene la entidad jugador
                                     #      BlockSimple = Contiene una lista de los bloques simples a colocar
                                     #      Portal = Contiene el portal para finalizar el nivel
                                     #      Other = por definir
      
    #Asigna un color para los bloques simples. Por defecto es negro
    def DefineSolidSimpleBlocksColor(self, color):
        self.colorBlock = color
    
    #Genera las entidades necesarias segun la informacion dada por self.dataMap. Retorna un diccionario con todas las entidades
    def GenerateEntities(self, displaySource):
        #Establecemos las llaves del diccionario
        self.EntitiesInMap_dict["Player"] = None
        self.EntitiesInMap_dict["Portal"] = None
        self.EntitiesInMap_dict["BlockSimple"] = []
        self.EntitiesInMap_dict["Spike"] = []
        self.EntitiesInMap_dict["Coin"] = []
        
        #Control de flujo
        IncrementLenghtBlock = 0
        CatchPlayer = False
        CatchPortal = False
        incrementalFactor_x = 0
        incrementalFactor_y = 0
        TemporalOrigin = []

        for dataFragmentRow in self.dataMap:
            for dataUnit in dataFragmentRow:
                if dataUnit == "X":
                    if IncrementLenghtBlock == 0:
                        TemporalOrigin = [incrementalFactor_x*self.cellSize[0], incrementalFactor_y*self.cellSize[1]]
                        IncrementLenghtBlock = IncrementLenghtBlock + 1

                    elif IncrementLenghtBlock > 0:
                        IncrementLenghtBlock = IncrementLenghtBlock + 1
                elif dataUnit == "P":
                    if IncrementLenghtBlock > 0:
                        self.EntitiesInMap_dict["BlockSimple"].append(SolidObjectSimple(self.colorBlock, TemporalOrigin[0], TemporalOrigin[1], self.cellSize[0]*IncrementLenghtBlock, self.cellSize[1]))
                        IncrementLenghtBlock = 0
                    if not CatchPlayer:
                        self.EntitiesInMap_dict["Player"] = Player(displaySource, incrementalFactor_x * self.cellSize[0], incrementalFactor_y*self.cellSize[1])
                        CatchPlayer = True
                    else:
                        raise "before you catch the player. You can't have two or more in map"
                elif dataUnit == "F":
                    if IncrementLenghtBlock > 0:
                        self.EntitiesInMap_dict["BlockSimple"].append(SolidObjectSimple(self.colorBlock, TemporalOrigin[0], TemporalOrigin[1], self.cellSize[0]*IncrementLenghtBlock, self.cellSize[1]))
                        IncrementLenghtBlock = 0
                    if not CatchPortal:
                        self.EntitiesInMap_dict["Portal"] = Portal(displaySource, incrementalFactor_x * self.cellSize[0], incrementalFactor_y*self.cellSize[1])
                        CatchPortal = True
                    else:
                        raise "before you catch the portal. You can't have two or more in map"
                elif dataUnit in ("1","2","3","4"):
                    if IncrementLenghtBlock > 0:
                        self.EntitiesInMap_dict["BlockSimple"].append(SolidObjectSimple(self.colorBlock, TemporalOrigin[0], TemporalOrigin[1], self.cellSize[0]*IncrementLenghtBlock, self.cellSize[1]))
                    IncrementLenghtBlock = 0
                    self.EntitiesInMap_dict["Spike"].append(Spike(incrementalFactor_x * self.cellSize[0], incrementalFactor_y*self.cellSize[1], int(dataUnit)*90-90))
                elif dataUnit == "C":
                    if IncrementLenghtBlock > 0:
                        self.EntitiesInMap_dict["BlockSimple"].append(SolidObjectSimple(self.colorBlock, TemporalOrigin[0], TemporalOrigin[1], self.cellSize[0]*IncrementLenghtBlock, self.cellSize[1]))
                    IncrementLenghtBlock = 0
                    self.EntitiesInMap_dict["Coin"].append(coin(incrementalFactor_x * self.cellSize[0], incrementalFactor_y*self.cellSize[1]))
                else:
                    if IncrementLenghtBlock > 0:
                        self.EntitiesInMap_dict["BlockSimple"].append(SolidObjectSimple(self.colorBlock, TemporalOrigin[0], TemporalOrigin[1], self.cellSize[0]*IncrementLenghtBlock, self.cellSize[1]))
                        IncrementLenghtBlock = 0
                if IncrementLenghtBlock > 0:
                        self.EntitiesInMap_dict["BlockSimple"].append(SolidObjectSimple(self.colorBlock, TemporalOrigin[0], TemporalOrigin[1], self.cellSize[0]*IncrementLenghtBlock, self.cellSize[1]))
                        IncrementLenghtBlock = 0
                incrementalFactor_x = incrementalFactor_x + 1
            incrementalFactor_x = 0
            incrementalFactor_y = incrementalFactor_y + 1

        if CatchPlayer == False or CatchPortal == False:
            raise "The map is invalid. No have a portal and a player"   
        
        return self.EntitiesInMap_dict


    def debugDataMap(self):
        print(self.dataMap)
    
    def debugDataEntities(self, entitie_name = "Player"):
        if entitie_name == "Player":
            print(self.EntitiesInMap_dict[entitie_name].rect)
        elif entitie_name == "BlockSimple":
            for debugBlock in self.EntitiesInMap_dict[entitie_name]:
                print(str(debugBlock.rect) + "  ")
    
    def __str__(self):
        #para mostrar en un print
        return "Map Name -> " + self.nameMap + ". Map template -> " + str(self.dataMap)
