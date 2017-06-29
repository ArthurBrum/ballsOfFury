'''
	ballsOfFury.py

	Created on: 31/05/2017
		Author: Arthur Brum (RA: 157701)

	Simples plot e movimentacao de poligonos com base em tempo

    intructions to run:
    -execute on terminal
    sudo pip install pyopengl numpy Enum

'''

from __future__ import division
from __future__ import print_function

import sys
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

def renderizarTexto(x, y, text, z=1, tamanho=0.002, color={'r': 1, 'g': 1, 'b': 1}):
    gl.glPushMatrix()
    gl.glMaterialfv(gl.GL_FRONT, gl.GL_AMBIENT, [color['r'], color['g'], color['b'], 1.0])
    gl.glMaterialfv(gl.GL_FRONT, gl.GL_DIFFUSE, [color['r'], color['g'], color['b'], 1.0])
    gl.glMaterialfv(gl.GL_FRONT, gl.GL_SPECULAR, [color['r'], color['g'], color['b'], 1.0])
    gl.glMaterialfv(gl.GL_FRONT, gl.GL_SHININESS, 100.0)
    gl.glTranslatef(x, y, z)
    gl.glScalef(tamanho, tamanho, tamanho)
    for ch in text:
        glut.glutStrokeCharacter(glut.GLUT_STROKE_MONO_ROMAN, glut.ctypes.c_int(ord(ch)))
    gl.glPopMatrix()

def init():
    gl.glClearColor(1, 1, 1, 1.0)
    gl.glShadeModel(gl.GL_FLAT)

def idle():
    global state

    if state == State.running:
        glut.glutPostRedisplay()

    if state == State.waiting:
        pass


def display():

    global cameraX, cameraY, cameraZ
    global p, stillColliding
    global oldTimeSinceStart
    radius = 0.1

    gl.glClear(gl.GL_COLOR_BUFFER_BIT)

    timeSinceStart = glut.glutGet(glut.GLUT_ELAPSED_TIME)
    deltaTime = timeSinceStart - oldTimeSinceStart
    oldTimeSinceStart = timeSinceStart

    gl.glPushMatrix()



    #Desenhando limites de pontuacao---------------------------------------------
    gl.glPushMatrix()

    gl.glLineWidth(20);
    gl.glTranslatef(0,0.7,0)

    # Limite 1
    gl.glColor3f(0.2,0.2,0.2)
    drawCircle(radius*4, nPoints*3, vazio=1)

    # Limite 2
    gl.glColor3f(0.8,0.1,0.1)
    drawCircle(radius*12, nPoints*3, vazio=1)


    gl.glLineWidth(1);

    gl.glColor3f(0.6,0.2,0.3)
    gl.glPopMatrix()
    #-----------------------------------------------------------------------------


    # Configura posicao da camera
    gl.glTranslatef(0,0.7,0)
    gl.glRotatef(cameraX, 1.0, 0.0, 0.0)
    gl.glRotatef(cameraY, 0.0, 1.0, 0.0)
    gl.glRotatef(cameraZ, 0.0, 0.0, 1.0)
    gl.glTranslatef(0,-0.7,0)


    #### Movement------------------------------------------------------------------

    # Operacao para alterar posicao de todos poligonos (baseado no tempo)
    p.pos += p.vel * deltaTime/10000

    # Operacao para desacelerar bolinha
    p.vel -= (p.vel*0.7)*deltaTime/1000

    ''' Tentar desaceleracao exponencial depois
    a = (p.vel[1])**0.8
    if not(math.isnan(a[1])):
        print(a)
    '''

    gl.glLineWidth(2);
    renderizarTexto(-2.2,2, ("Player1:"+"12"), tamanho=0.0012)
    renderizarTexto(+0.9,2, ("Player1:"+"08"), tamanho=0.0012)


    # TO-DO: Chamar funcao detectCollision
    # Collision ------------------------------------------------------------------

    # TO-DO: Otimiza verificando se existe algum par com colisao
    #d = spd.pdist(p.pos)
    #if d.min() <= 2*radius:
    #   call collision handler (conteudo abaixo)
    ##### Handling collision #########

    distMatrix = spd.squareform(spd.pdist(p.pos))

    # Percorre todas bolinhas
    for i in range(p.size):
        # Comparando com todas as outras
        for j in range(i):

            # TO-DO: generalizar para raios diferentes
            if (i != j and distMatrix[i][j] <= 2*radius):
                # Colisao :: Ver referencias.txt -> ref 3.2
                # TO-DO: tratar massas diferentes

                # Marca que collisao esta ocorrendo - evita mais de um tratamento por colisao
                stillColliding[i][j] = 1

                # Talvez para maior numero de colisoes seja melhor otimizar - ref 3.2.1

                n = p.pos[i] - p.pos[j]         # Calcula vetor normal
                un = n / np.sqrt(n.dot(n))      # Vetor unitario normal
                ut = np.array([-un[1], un[0]])  # Vetor unitario tangente

                vIn = un.dot(p.vel[i]) # Projecao da velocidade na direcao normal
                vJn = un.dot(p.vel[j])

                vIt = ut.dot(p.vel[i])
                vJt = ut.dot(p.vel[j])

                p.vel[i] = un * vJn + vJt
                p.vel[j] = un * vIn + vIt
            else:
                if (stillColliding[i][j]):
                    stillColliding[i][j] = 0

    # Plotting
    for i in range(p.size):
        gl.glPushMatrix()

        ## WALL DETECTION (shouldnt be here)
        # TO-DO: fix for resizing windows and place code elsewhere
        if not(-2.8 < p.pos[i][1] < 2.8):
            p.vel[i][1] = -p.vel[i][1]

        if not(-2.8 < p.pos[i][0] < 2.8):
            p.vel[i][0] = -p.vel[i][0]

        # Actual plotting
        gl.glTranslatef(p.pos[i][0], p.pos[i][1], 0)
        gl.glColor3f(p.color[i][0], p.color[i][1], p.color[i][2])
        drawCircle(radius,nPoints)

        gl.glPopMatrix()


    gl.glPopMatrix()

    glut.glutSwapBuffers()


def reshape(w, h):
    gl.glViewport(0, 0, w, h)
    gl.glMatrixMode(gl.GL_PROJECTION)
    gl.glLoadIdentity()
    glu.gluPerspective(60.0, w / h, 1.0, 20.0)
    gl.glMatrixMode(gl.GL_MODELVIEW)
    gl.glLoadIdentity()
    glu.gluLookAt(0.0, 0.0, 5.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0)

def keyboard(key, x, y):
    global cameraX, cameraY, cameraZ

    # Alteracoes na camera
    if key == 's':
        cameraX = (cameraX + 5) % 360
    elif key == 'w':
        cameraX = (cameraX - 5) % 360
    elif key == 'd':
        cameraY = (cameraY + 5) % 360
    elif key == 'a':
        cameraY = (cameraY - 5) % 360
    elif key == 'q':
        cameraZ = (cameraZ + 5) % 360
    elif key == 'e':
        cameraZ = (cameraZ - 5) % 360

    else:
        return

    glut.glutPostRedisplay()

def generateCirclePoints(nPoints):
    global points, alreadyGenerated

    points = []
    for val in np.linspace(0, 2*math.pi, num=nPoints, endpoint = False):
        points.append([math.cos(val), math.sin(val)])

    alreadyGenerated = nPoints


def drawCircle(radius, nPoints, vazio=0):
    global points, alreadyGenerated

    if alreadyGenerated != nPoints:
        generateCirclePoints(nPoints)

    if vazio:
        gl.glBegin(gl.GL_LINE_LOOP)
    else:
        gl.glBegin(gl.GL_POLYGON)

    for i in range(nPoints):
        gl.glVertex3f(points[i][0]*radius, points[i][1]*radius, 0.0)
    gl.glEnd()


def main():
    _ = glut.glutInit(sys.argv)
    glut.glutInitDisplayMode(glut.GLUT_DOUBLE | glut.GLUT_RGB)

    glut.glutInitWindowSize(700, 700)
    glut.glutInitWindowPosition(0, 0)
    _ = glut.glutCreateWindow(sys.argv[0])

    init()

    # Valores Iniciais
    global cameraX, cameraY, cameraZ
    cameraX = 0
    cameraY = 0
    cameraZ = 0

    global p
    p = PolygonsHandler()
    p.add_polygon(-1, 0, 0, 0, '#00aa00', 'c1')
    p.add_polygon(1, 1, 0, 0, '#aa0000', 'c2')
    p.add_polygon(1, -1.1, 0, 0, '#0099FF', 'c3')
    p.add_polygon(-1, -0.95, 0, 8, '#2211AA', 'c4')

    global stillColliding
    stillColliding = np.zeros([p.size, p.size])

    global nPoints, points, alreadyGenerated, oldTimeSinceStart
    alreadyGenerated = 0
    nPoints = 12
    points = []
    oldTimeSinceStart = 0

    global state
    state = State.running


    _ = glut.glutDisplayFunc(display)
    _ = glut.glutReshapeFunc(reshape)
    _ = glut.glutKeyboardFunc(keyboard)
    _ = glut.glutIdleFunc(idle)

    glut.glutMainLoop()


if __name__ == "__main__":
    main()
