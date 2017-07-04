'''
    main.py
    
    last edit on: 02/07/2017

    intructions to run:
    -execute on terminal
    sudo pip install pyopengl numpy Enum

'''

from __future__ import division
from __future__ import print_function

import sys

import OpenGL.GL as gl
import OpenGL.GLU as glu
import OpenGL.GLUT as glut

from ballsOfFury import BallsOfFury


def init():
    gl.glClearColor(1, 1, 1, 1.0)
    gl.glShadeModel(gl.GL_FLAT)


def idle():
    global state

    #if state == State.running:
    glut.glutPostRedisplay()


def keyboard(key, x, y):
    global cameraX, cameraY, cameraZ
    global forca, angulo
    global state


    if key == 's':
        # Diminui forca
        forca -= 1

    elif key == 'w':
        # Aumenta forca
        forca += 1

    elif key == 'd':
        # Incrementa mira p direita
        angulo += 1

    elif key == 'a':
        # Incrementa mira p esquerda
        angulo -= 1

    elif key == 'q':
        # Rotaciona para esquerda
        cameraZ = (cameraZ + 5) % 360


    elif key == 'e':
        # Rotaciona para direita
        cameraZ = (cameraZ - 5) % 360


    elif key == 'm':
        state = (state+1)%2

    else:
        return


    glut.glutPostRedisplay()

def reshape(w, h):
    gl.glViewport(0, 0, w, h)
    gl.glMatrixMode(gl.GL_PROJECTION)
    gl.glLoadIdentity()
    glu.gluPerspective(60.0, w / h, 1.0, 20.0)
    gl.glMatrixMode(gl.GL_MODELVIEW)
    gl.glLoadIdentity()
    glu.gluLookAt(0.0, 0.0, 5.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0)

def display():
    global game

    gl.glClear(gl.GL_COLOR_BUFFER_BIT)

    game.render()

    glut.glutSwapBuffers()

def main():
    global game
    game = BallsOfFury()

    _ = glut.glutInit(sys.argv)
    glut.glutInitDisplayMode(glut.GLUT_DOUBLE | glut.GLUT_RGB)

    glut.glutInitWindowSize(700, 700)
    glut.glutInitWindowPosition(0, 0)
    _ = glut.glutCreateWindow("BALLS OF FURY!!!")

    init()


    _ = glut.glutDisplayFunc(display)
    _ = glut.glutReshapeFunc(reshape)
    _ = glut.glutKeyboardFunc(keyboard)
    _ = glut.glutIdleFunc(idle)

    glut.glutMainLoop()

if __name__ == "__main__":
    main()