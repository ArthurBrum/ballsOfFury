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
        self.player = []                        # Indica player dono da bolinha
        self.pos = np.empty([0,2])              # Array Numpy de posicoes
        self.vel = np.empty([0,2])              # Array Numpy de velocidades
        self.color = []                         # Lista de cores - tupla (R,G,B)

        # Matriz auxiliar no tratamento de colisoes
        self.stillColliding = np.zeros([self.size, self.size])
        
    def add_polygon(self, player, posX, posY, velX=0, velY=0, color='#000000'):

        self.player.append(player)
        self.pos = np.vstack((self.pos, [posX, posY]))
        self.vel = np.vstack((self.vel, [velX, velY]))
        self.color.append(colors.hex2color(color))

        self.size += 1
        # Redimensiona matriz auxiliar
        self.stillColliding = np.zeros([self.size, self.size])