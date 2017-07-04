'''
	polygonsHandler.py

	Created on: 31/05/2017
		Author: Arthur Brum (RA: 157701)

    Classe para controle de todos os poligonos e realizacao de operacoes

'''

import numpy as np
import matplotlib.colors as colors


class PolygonsHandler():

    def __init__(self):
        self.size = 0
        self.id = {}                            # Dictionary de ids  {string:int}
        self.pos = np.empty([0,2])              # Array Numpy de posicoes
        self.vel = np.empty([0,2])              # Array Numpy de velocidades
        self.color = []                         # Lista de cores - tupla (R,G,B)
        #radius
        #typeOfPolygon
        
    def add_polygon(self, posX, posY, velX=0, velY=0, color='#ffffff', id=None):

        self.pos = np.vstack((self.pos, [posX, posY]))
        self.vel = np.vstack((self.vel, [velX, velY]))
        self.color.append(colors.hex2color(color))
        #radius
        #typeOfPolygon

        if(id == None):
            self.id[str(self.size)] = self.size
        else:
            self.id[str(id)] = self.size

        self.size += 1