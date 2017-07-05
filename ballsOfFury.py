'''
	ballsOfFury.py

	Created on: 31/05/2017



'''
from __future__ import division
from __future__ import print_function

import math
import matplotlib.colors as colors
import numpy as np
import scipy.spatial.distance as spd

import OpenGL.GL as gl
import OpenGL.GLU as glu
import OpenGL.GLUT as glut

from enum import Enum
from polygonsHandler import PolygonsHandler


# Definindo enums para estados de execucao do jogo
class State(Enum):
    aiming, running  = range(2)

# Constantes

LOWEST_VEL = 0.05
COLORS = ['#4fc4ff', '#a6dd4d']
N_POINTS = 12
RADIUS = 0.12
LIMIT1_RADIUS = RADIUS *4
LIMIT2_RADIUS = RADIUS *12

MAP_CENTER_X = 0
MAP_CENTER_Y = 0.8
INITIAL_X = 0
INITIAL_Y = -2.2

BAR_HEIGHT = 0.8
BAR_Y_BOTTOM = INITIAL_Y
BAR_Y_TOP = BAR_Y_BOTTOM + BAR_HEIGHT
BAR_X_L = 2.55
BAR_X_R = BAR_X_L + 0.1



class BallsOfFury:
    def __init__(self):

        # Valores Iniciais
        self.cameraZ = 0
        self.angle = 0
        self.strength = 0.7
        self.incrementSignal = 1
        self.alreadyGenerated = 0
        self.points = []
        self.oldTimeSinceStart = 0
        self.deltaTime = 0
        self.state = State.aiming
        self.currentPlayer = 0
        self.score = [0,0]

        self.p = PolygonsHandler()
        # Adicionando bolinhas ao ambiente


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
        self.renderText(-2.2, 2, ("Player1: " + str(self.score[0])), tamanho=0.001)
        self.renderText(+0.9, 2, ("Player2: " + str(self.score[1])), tamanho=0.001)
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
        self.drawCircle(LIMIT1_RADIUS, filled=0)

        # Limite 2
        gl.glColor3f(0.8, 0.1, 0.1)
        self.drawCircle(LIMIT2_RADIUS, filled=0)

        gl.glLineWidth(1)
        gl.glPopMatrix()


    # Desenha bolinha a ser arremessada junto com mira
    def drawPlayingBall(self):

        # Mudando angulo da mira
        gl.glPushMatrix()

        gl.glTranslatef(INITIAL_X, INITIAL_Y, 0)
        gl.glRotatef((self.angle), 0.0, 0.0, 1.0)
        gl.glTranslatef(INITIAL_X, -INITIAL_Y, 0)


        # Desenha reta da mira
        gl.glLineWidth(2)
        gl.glColor3f(0.2,0.2,0.2)

        gl.glBegin(gl.GL_LINES)
        gl.glVertex3f(INITIAL_X, INITIAL_Y, 0)
        gl.glVertex3f(INITIAL_X, (INITIAL_Y+0.8), 0)
        gl.glEnd()


        # Desenha ponta da mira
        gl.glBegin(gl.GL_POLYGON)
        gl.glVertex3f(INITIAL_X, (INITIAL_Y+ 0.8), 0)
        gl.glVertex3f((INITIAL_X+0.05), (INITIAL_Y+ 0.7), 0)
        gl.glVertex3f((INITIAL_X-0.05), (INITIAL_Y+ 0.7), 0)
        gl.glEnd()

        gl.glLineWidth(1)
        gl.glPopMatrix()

        # Desenha a bolinha na posicao inicial
        gl.glPushMatrix()

        currentColor = colors.hex2color(COLORS[self.currentPlayer])
        gl.glTranslatef(INITIAL_X, INITIAL_Y, 0)
        gl.glColor3f(currentColor[0], currentColor[1], currentColor[2])
        self.drawCircle(RADIUS)

        gl.glPopMatrix()


    def throw(self):
        # Muda estado do jogo para aguardar termino da jogada
        self.state = State.running

        # Faz deslocamento de 90 graus e converte valor do angulo para radianos
        anguloReal = math.pi/2 + self.angle*(math.pi/180)

        # Faz a bolinha entrar de fato no jogo
        self.p.add_polygon(self.currentPlayer, INITIAL_X, INITIAL_Y,
                           velX=math.cos(anguloReal) * (self.strength*25 + 8),
                           velY=math.sin(anguloReal) * (self.strength*25 + 8),
                           color=COLORS[self.currentPlayer])

        # Muda proximo player a jogar
        self.currentPlayer = (self.currentPlayer + 1) % 2


    # Desenhas as bolinhas que ja estao em campo
    def drawBalls(self):

        # Rotacionando camera para ponto de vista desejado
        gl.glPushMatrix()

        gl.glTranslatef(MAP_CENTER_X, MAP_CENTER_Y, 0)
        gl.glRotatef(self.cameraZ, 0.0, 0.0, 1.0)
        gl.glTranslatef(MAP_CENTER_X, -MAP_CENTER_Y, 0)

        self.score = [0,0]
        # Plotting balls
        for i in range(self.p.size):


            # Contagem de pontos
            dist = spd.euclidean(self.p.pos[i], [MAP_CENTER_X, MAP_CENTER_Y])
            if dist <= LIMIT2_RADIUS:
                self.score[self.p.player[i]] +=1
                if dist <= LIMIT1_RADIUS:
                    self.score[self.p.player[i]] += 1

            # Actual plotting
            gl.glPushMatrix()

            gl.glTranslatef(self.p.pos[i][0], self.p.pos[i][1], 0)
            gl.glColor3f(self.p.color[i][0], self.p.color[i][1], self.p.color[i][2])
            self.drawCircle(RADIUS)

            gl.glPopMatrix()

        gl.glPopMatrix()


    def drawStrengthBar(self):

        if (self.state == State.aiming):

            # Controla variacao da forca com o tempo
            increment = 0.4 * self.deltaTime/1000
            print(str(self.strength) +"--"+ str(increment))

            if self.strength >= 1:
                self.incrementSignal = -1
            if self.strength <= 0.1:
                self.incrementSignal = 1

            self.strength += increment*self.incrementSignal


        height = self.strength * BAR_HEIGHT

        # Desenha quadrado interno colorido
        gl.glBegin(gl.GL_QUADS)

        gl.glColor3f(2*self.strength, 1/(2*self.strength), 0)
        gl.glVertex3f(BAR_X_L, BAR_Y_BOTTOM +height, 0)
        gl.glVertex3f(BAR_X_R, BAR_Y_BOTTOM +height, 0)
        gl.glVertex3f(BAR_X_R, BAR_Y_BOTTOM, 0)
        gl.glVertex3f(BAR_X_L, BAR_Y_BOTTOM, 0)

        gl.glEnd()


        # Desenha borda
        gl.glLineWidth(2)
        gl.glBegin(gl.GL_LINE_LOOP)

        gl.glColor3f(0.2, 0.2, 0.2)
        gl.glVertex3f(BAR_X_L, BAR_Y_TOP, 0)
        gl.glVertex3f(BAR_X_R, BAR_Y_TOP, 0)
        gl.glVertex3f(BAR_X_R, BAR_Y_BOTTOM, 0)
        gl.glVertex3f(BAR_X_L, BAR_Y_BOTTOM, 0)
        gl.glEnd()
        gl.glLineWidth(1)


    # Atualiza posicoes e velocidades para bolinhas em campo
    def computeMovement(self):
        # Operacao para alterar posicao de todos poligonos (baseado no tempo)
        self.p.pos += self.p.vel * self.deltaTime / 10000

        # Operacao para desacelerar bolinhas
        self.p.vel -= (self.p.vel*0.6)*self.deltaTime/1000

        # Zerando os valores muito proximos de zero
        self.p.vel[np.absolute(self.p.vel) < LOWEST_VEL] = 0


    # Detecta e trata colisoes
    def collisionsHandling(self):

        # Evita calculos se nao houver bolinhas para colidir
        if self.p.size <= 1:
            return

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
                    self.p.stillColliding[i][j] = 1

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
                    if (self.p.stillColliding[i][j]):
                        self.p.stillColliding[i][j] = 0
                        


    def render(self):

        # Calcula passagem de tempo
        timeSinceStart = glut.glutGet(glut.GLUT_ELAPSED_TIME)
        self.deltaTime = timeSinceStart - self.oldTimeSinceStart
        self.oldTimeSinceStart = timeSinceStart

        # Cenario de fundo do jogo
        self.drawScoreLimits()


        if self.state == State.aiming:
            # Desenha bolinha a ser jogada
            self.drawPlayingBall()


        elif self.state == State.running:

            # Quando todas bolinhas ja tiverem parado volta ao estado aiming
            if not (self.p.vel[self.p.vel!=0].any()):
                self.state = State.aiming


        # Movimentacao das bolinhas em campo
        self.computeMovement()

        # Detectando e tratanto colisoes
        self.collisionsHandling()

        # Desenhas as bolinhas ja em campo
        self.drawBalls()

        # Informacoes textuais (pontos, angulo)
        self.drawTexts()

        # Informacoes de forca
        self.drawStrengthBar()



