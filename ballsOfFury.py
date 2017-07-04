'''
	ballsOfFury.py

	Created on: 31/05/2017

	Simples plot e movimentacao de poligonos com base em tempo

    intructions to run:
    -execute on terminal
    sudo pip install pyopengl numpy Enum

'''
from __future__ import division
from __future__ import print_function

import math
import numpy as np
import scipy.spatial.distance as spd

import OpenGL.GL as gl
import OpenGL.GLU as glu
import OpenGL.GLUT as glut

from enum import Enum
from polygonsHandler import PolygonsHandler


# Definindo enums para estados de execucao do jogo
class State(Enum):
    running, waiting  = range(2)

# Constantes

COLORS = ['#4fc4ff', '#a6dd4d']
N_POINTS = 12
RADIUS = 0.12
MAP_CENTER_X = 0
MAP_CENTER_Y = 0.7


class BallsOfFury:
    def __init__(self):

        # Valores Iniciais
        self.cameraZ = 0
        self.angulo = 0
        self.alreadyGenerated = 0
        self.points = []
        self.oldTimeSinceStart = 0
        self.deltaTime = 0
        self.state = State.waiting

        self.p = PolygonsHandler()
        # Adicionando bolinhas ao ambiente
        self.p.add_polygon(-0.35, 0, color=COLORS[0])
        self.p.add_polygon(0.7, 0.7, color=COLORS[1])
        self.p.add_polygon(1, -0.7, color=COLORS[0])
        self.p.add_polygon(-0.45, -0.95, velY=10, color=COLORS[1])

        self.stillColliding = np.zeros([self.p.size, self.p.size])


    # Renderiza um dado texto para uma dada posicao
    def renderText(self, x, y, text, z=1, tamanho=0.002, color={'r': 0, 'g': 0, 'b': 0}):
        gl.glPushMatrix()

        gl.glColor3f(color['r'], color['g'], color['b'])
        gl.glTranslatef(x, y, z)
        gl.glScalef(tamanho, tamanho, tamanho)
        for ch in text:
            glut.glutStrokeCharacter(glut.GLUT_STROKE_MONO_ROMAN, glut.ctypes.c_int(ord(ch)))

        gl.glPopMatrix()

    # Desenho de informacoes textuais na tela
    def drawTexts(self):
        # Textos de pontuacao
        gl.glColor3f(0.2, 0.2, 0.2)
        gl.glLineWidth(2)
        self.renderText(-2.2, 2, ("Player1:" + "12"), tamanho=0.0012)
        self.renderText(+0.9, 2, ("Player1:" + "08"), tamanho=0.0012)
        gl.glLineWidth(1)

    # Gera vetor de pontos auxiliar na criacao do circulo
    def generateCirclePoints(self, nPoints):

        self.points = []

        # Cria lista de nPontos - com raio 1 - separados por angulos iguais
        for val in np.linspace(0, 2 * math.pi, num=nPoints, endpoint=False):
            self.points.append([math.cos(val), math.sin(val)])

        self.alreadyGenerated = nPoints

    # Desenha circulo na posicao corrente
    def drawCircle(self, radius, filled=1):

        # Determina numero de pontos necessarios para plotar aceitavelmente um circulo
        nPoints = (int)(radius*100)

        if self.alreadyGenerated != nPoints:
            self.generateCirclePoints(nPoints)

        # Desenha um circulo preenchido ou vazio
        if filled:
            gl.glBegin(gl.GL_POLYGON)
        else:
            gl.glBegin(gl.GL_LINE_LOOP)

        for i in range(nPoints):
            gl.glVertex3f(self.points[i][0] * radius, self.points[i][1] * radius, 0.0)
        gl.glEnd()

    # Desenha os circulos limitantes de pontuacao
    def drawScoreLimits(self):
        gl.glPushMatrix()

        # Muda posicao de desenho e tambem espessura da linha
        gl.glLineWidth(6)
        gl.glTranslatef(MAP_CENTER_X, MAP_CENTER_Y, 0)

        # Limite 1
        gl.glColor3f(0.2, 0.2, 0.2)
        self.drawCircle(RADIUS * 4, filled=0)

        # Limite 2
        gl.glColor3f(0.8, 0.1, 0.1)
        self.drawCircle(RADIUS * 12, filled=0)

        gl.glLineWidth(1)
        gl.glPopMatrix()

    # Desenhas as bolinhas que ja estao em campo
    def drawBalls(self):
        # Plotting balls
        for i in range(self.p.size):
            gl.glPushMatrix()

            ## WALL DETECTION (shouldnt be here)
            # TO-DO: fix for resizing windows and place code elsewhere
            if not (-2.8 < self.p.pos[i][1] < 2.8):
                self.p.vel[i][1] = -self.p.vel[i][1]

            if not (-2.8 < self.p.pos[i][0] < 2.8):
                self.p.vel[i][0] = -self.p.vel[i][0]

            # Actual plotting
            gl.glTranslatef(self.p.pos[i][0], self.p.pos[i][1], 0)
            gl.glColor3f(self.p.color[i][0], self.p.color[i][1], self.p.color[i][2])
            self.drawCircle(RADIUS)

            gl.glPopMatrix()

    # Atualiza posicoes e velocidades para bolinhas em campo
    def computeMovement(self):
        # Operacao para alterar posicao de todos poligonos (baseado no tempo)
        self.p.pos += self.p.vel * self.deltaTime / 10000

        # Operacao para desacelerar bolinha
        self.p.vel -= (self.p.vel*0.6)*self.deltaTime/1000

    # Detecta e trata colisoes
    def collisionsHandling(self):

        # Calcula vetor de distancias e encerra rapidamente se nao existir colisoes
        d = spd.pdist(self.p.pos)
        if d.min() >= 2*RADIUS:
            return

        # Caso exista colisoes, transforma vetor de distancias em matriz quadrada
        distMatrix = spd.squareform(d)


        # Percorre todas bolinhas
        for i in range(self.p.size):
            # Comparando com todas as outras
            for j in range(i):

                # TO-DO: generalizar para raios diferentes
                if (i != j and distMatrix[i][j] <= 2 * RADIUS):
                    # Colisao :: Ver referencias.txt -> ref 3.2
                    # TO-DO: tratar massas diferentes

                    # Marca que collisao esta ocorrendo - evita mais de um tratamento por colisao
                    self.stillColliding[i][j] = 1

                    n = self.p.pos[i] - self.p.pos[j]           # Calcula vetor normal
                    un = n / np.sqrt(n.dot(n))                  # Vetor unitario normal
                    ut = np.array([-un[1], un[0]])              # Vetor unitario tangente

                    vIn = un.dot(self.p.vel[i])                 # Projecao da velocidade na direcao normal
                    vJn = un.dot(self.p.vel[j])

                    vJt = ut.dot(self.p.vel[i])                 # Projecao na direcao tangente
                    vIt = ut.dot(self.p.vel[j])

                    self.p.vel[i] = un * vJn + vJt              # Trazendo de volta para base canonica
                    self.p.vel[j] = un * vIn + vIt
                else:
                    if (self.stillColliding[i][j]):
                        self.stillColliding[i][j] = 0
                        


    def render(self):

        # Calcula passagem de tempo
        timeSinceStart = glut.glutGet(glut.GLUT_ELAPSED_TIME)
        self.deltaTime = timeSinceStart - self.oldTimeSinceStart
        self.oldTimeSinceStart = timeSinceStart

        # Cenario de fundo do jogo
        self.drawScoreLimits()


        # TO-DO: contagem de bolinhas restantes de cada jogador

        # TO-DO: Bolinha a ser jogada


        # Rotacao da camera
        gl.glTranslatef(MAP_CENTER_X, MAP_CENTER_Y, 0)
        gl.glRotatef(self.cameraZ, 0.0, 0.0, 1.0)
        gl.glTranslatef(MAP_CENTER_X, -MAP_CENTER_Y, 0)

        # Desenhas as bolinhas ja em campo
        self.drawBalls()

        # Movimentacao das bolinhas em campo
        self.computeMovement()

        # Detectando e tratanto colisoes
        self.collisionsHandling()

        # Informacoes textuais (pontos, forca)
        self.drawTexts()


