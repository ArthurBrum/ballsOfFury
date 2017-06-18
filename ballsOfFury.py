'''
	ballsOfFury.py

	Created on: 31/05/2017
		Author: Arthur Brum (RA: 157701)

	Simples plot e movimentacao de poligonos com base em tempo

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

from polygonsHandler import PolygonsHandler

def init():
    gl.glClearColor(0.0, 0.0, 0.0, 1.0)
    gl.glShadeModel(gl.GL_FLAT)


def display():
    global cameraX, cameraY, cameraZ
    global p
    global oldTimeSinceStart
    radius = 0.1


    gl.glClear(gl.GL_COLOR_BUFFER_BIT)

    timeSinceStart = glut.glutGet(glut.GLUT_ELAPSED_TIME)
    deltaTime = timeSinceStart - oldTimeSinceStart
    oldTimeSinceStart = timeSinceStart

    gl.glPushMatrix()

    # Configura posicao da camera
    gl.glRotatef(cameraX, 1.0, 0.0, 0.0)
    gl.glRotatef(cameraY, 0.0, 1.0, 0.0)
    gl.glRotatef(cameraZ, 0.0, 0.0, 1.0)


    #### Movement

    #Operations to change position of all polygons (time based movement)
    p.pos += p.vel/10000 * deltaTime
    # TO-DO:
    #p.vel += p.acel/10000 * deltaTime


    # TO-DO: Chamar funcao detectCollision
    #### Collision
    # TO-DO: Otimiza verificando se existe algum par com colisao
    #d = spd.pdist(p.pos)
    #if d.min() <= 2*radius:
    #   call collision handler (conteudo abaixo)

    distMatrix = spd.squareform(spd.pdist(p.pos))

    # Percorre todas bolinhas
    for i in range(p.size):
        # Comparando com todas as outras
        for j in range(i):

            # TO-DO: generalizar para raios diferentes
            if (i != j and distMatrix[i][j] <= 2*radius):
                # Colisao :: Ver referencias.txt -> ref 3.2
                # TO-DO: tratar massas diferentes
                temp = p.vel[i].copy()
                p.vel[i] = p.vel[j].copy()
                p.vel[j] = temp.copy()


    for i in range(p.size):
        gl.glPushMatrix()

        gl.glTranslatef(p.pos[i][0], p.pos[i][1], 0)
        gl.glColor3f(p.color[i][0], p.color[i][1], p.color[i][2])
        drawCircle(radius)

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

def generateCirclePoints():
    global nPoints, points, alreadyGenerated

    for val in np.linspace(0, 2*math.pi, num=nPoints, endpoint = False):
        points.append([math.cos(val), math.sin(val)])

    alreadyGenerated = nPoints

def drawCircle(radius):
    global nPoints, points, alreadyGenerated

    if alreadyGenerated != nPoints:
        generateCirclePoints()

    gl.glBegin(gl.GL_POLYGON)
    for i in range(nPoints):
        gl.glVertex3f(points[i][0]*radius, points[i][1]*radius, 0.0)
    gl.glEnd()


def main():
    _ = glut.glutInit(sys.argv)
    glut.glutInitDisplayMode(glut.GLUT_DOUBLE | glut.GLUT_RGB)

    glut.glutInitWindowSize(700, 700)
    glut.glutInitWindowPosition(100, 100)
    _ = glut.glutCreateWindow(sys.argv[0])

    init()

    global cameraX, cameraY, cameraZ
    cameraX = 0
    cameraY = 0
    cameraZ = 0

    _ = glut.glutDisplayFunc(display)
    _ = glut.glutReshapeFunc(reshape)
    _ = glut.glutKeyboardFunc(keyboard)
    _ = glut.glutIdleFunc(display)

    global p
    p = PolygonsHandler()
    p.add_polygon(-1,0,1.9,0.85, '#00aa00', 'c1')
    p.add_polygon(1,1,-1,-0.5, '#aa0000', 'c2')
    p.add_polygon(1,-1,0,0, '#0099FF', 'c3')


    global nPoints, points, alreadyGenerated, oldTimeSinceStart
    alreadyGenerated = 0
    nPoints = 12
    points = []

    oldTimeSinceStart = 0

    glut.glutMainLoop()


if __name__ == "__main__":
    main()
