# -*- coding: utf-8 -*-

from __future__ import division

import math
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from Box2D import *

#CONSTANTES

ANCHO_VENTANA = 600
ALTO_VENTANA = 400

LINHA_BORRADO_Y = -100

TEMPO_ESPERA_MOUSE = 0

#MEDIDA OPENGL

ANCHO_GL = 100
ALTO_GL = ANCHO_GL*ALTO_VENTANA/ANCHO_VENTANA

COLOR_FONDO = 0

#VARIABLES

pos_camara = [0,0]

descanso_mouse = 0

lista_caixas = []
lista_caixas_shape = []
lista_suelo = []

#BOX2D

FRICCION = 0.2

mundo = b2World(gravity=(0, -50))


def crear_mundo():
	global lista_suelo
	lista_suelo.append(mundo.CreateStaticBody(position=(0, 0), shapes=b2PolygonShape(box=(12,2))))
	lista_suelo.append(mundo.CreateStaticBody(position=(30, 10), shapes=b2PolygonShape(box=(10,2))))
	lista_suelo.append(mundo.CreateStaticBody(position=(60, 20), shapes=b2PolygonShape(box=(10,2))))
	lista_suelo.append(mundo.CreateStaticBody(position=(90, 30), shapes=b2PolygonShape(box=(10,2))))
	lista_suelo.append(mundo.CreateStaticBody(position=(120, 25), shapes=b2PolygonShape(box=(5,2))))
	lista_suelo.append(mundo.CreateStaticBody(position=(130, 20), shapes=b2PolygonShape(box=(5,2))))
	lista_suelo.append(mundo.CreateStaticBody(position=(140, 15), shapes=b2PolygonShape(box=(5,2))))
	
crear_mundo()

personaje = mundo.CreateDynamicBody(position=(0,3), shapes=b2CircleShape(box=(1,2), density=10, friction=5, radius=1.5))

#MAIN

def main():

	global ANCHO_GL
	global ALTO_GL
	global pos_camara
	global descanso_mouse
	global lista_caixas
	global lista_caixas_shape
	global lista_suelo
	global mundo
	global personaje
	
	pygame.init()
	ventana = pygame.display.set_mode((ANCHO_VENTANA, ALTO_VENTANA), DOUBLEBUF|OPENGL)
	
	init_gl()
	
	fps = 60
	vel_iters = 10
	pos_iters = 10

	while True:
	
		reloj = pygame.time.Clock()
		
		mundo.Step(1 / fps, vel_iters, pos_iters)
		
		#LIMPIAR VENTANA ######
		
		limpiar_ventana()
		
		######################################
		#DEBUXAR #############################
		######################################
		
		glColor3f(1.0, 1.0, 1.0)
		
		for i in range(len(lista_caixas)):
			debuxar_rect(lista_caixas[i].position, list(lista_caixas_shape[i].shape), lista_caixas[i].angle)
		
		glColor3f(0.0, 0.5, 1.0)
		
		for i in lista_suelo:
			debuxar_rect(i.position, list(i.fixtures[0].shape))
			
		glColor3f(0.1, 0.9, 0.1)
		
		debuxar_circulo(personaje.position, 1.5)
				
		debuxar_linea_borrado()
		
		#BORRADO DE CAIXAS
		
		for i in range(len(lista_caixas)):
			if lista_caixas[i].position[1] < LINHA_BORRADO_Y:
				lista_caixas.remove(lista_caixas[i])
				lista_caixas_shape.remove(lista_caixas_shape[i])
				break
				
		#COLISIONS
		
		#############################################################
		#EVENTOS ####################################################
		#############################################################
		
		#MOUSE ######
		
		if descanso_mouse > 0:
			descanso_mouse -= 1
		
		if descanso_mouse == 0:
			pos_mouse = pygame.mouse.get_pos()
		
		if descanso_mouse == 0:
			teclas_mouse_pulsadas = pygame.mouse.get_pressed()
		
		if descanso_mouse == 0 and (teclas_mouse_pulsadas[0] or teclas_mouse_pulsadas[2]):
			if teclas_mouse_pulsadas[0]:
				lista_caixas.append(mundo.CreateDynamicBody
					(position=(pos_mouse[0]*ANCHO_GL/ANCHO_VENTANA-ANCHO_GL/2-pos_camara[0],ALTO_GL-(pos_mouse[1]*ALTO_GL/ALTO_VENTANA)-pos_camara[1])))
				lista_caixas_shape.append(lista_caixas[-1].CreatePolygonFixture(box=(1,1), density=0.5, friction=0.1))
			#if teclas_mouse_pulsadas[2]:
			#	lista_suelo.append(mundo.CreateStaticBody
			#	(position=(pos_mouse[0]*ANCHO_GL/ANCHO_VENTANA-ANCHO_GL/2-pos_camara[0],ALTO_GL-(pos_mouse[1]*ALTO_GL/ALTO_VENTANA)-pos_camara[1]),
			#	shapes=b2PolygonShape(box=(1,1))))
			descanso_mouse = TEMPO_ESPERA_MOUSE
		
		#TECLAS ######
		
		tecla_pulsada = pygame.key.get_pressed()
		
		if (tecla_pulsada[K_UP] or tecla_pulsada[K_w]): 
			if (list(personaje.linearVelocity)[1] < 0.1 and list(personaje.linearVelocity)[1] > -0.1 and 
					personaje.fixtures[0].body.contacts and not personaje.fixtures[0].body.contacts[0].contact.manifold.localNormal[1] < 0):
				personaje.ApplyForceToCenter(b2Vec2(0,10), personaje.position)
				personaje.ApplyLinearImpulse(b2Vec2(0,30), personaje.position, 0)
			personaje.ApplyForceToCenter(b2Vec2(0,15), personaje.position)
			
		
		if tecla_pulsada[K_DOWN] or tecla_pulsada[K_s]:
			personaje.ApplyForceToCenter(b2Vec2(0,-50), personaje.position)
		
		if tecla_pulsada[K_LEFT] or tecla_pulsada[K_a]:
			if personaje.fixtures[0].body.contacts:
				if (list(personaje.linearVelocity)[0]) > -1:
					personaje.ApplyLinearImpulse(b2Vec2(-2,0), personaje.position, 0)
				personaje.ApplyForceToCenter(b2Vec2(-30,0), personaje.position)
			else:
				personaje.ApplyForceToCenter(b2Vec2(-20,0), personaje.position)
				personaje.linearVelocity = b2Vec2(max(-25,list(personaje.linearVelocity)[0]),list(personaje.linearVelocity)[1])
			
		elif tecla_pulsada[K_RIGHT] or tecla_pulsada[K_d]:
			if personaje.fixtures[0].body.contacts:
				if (list(personaje.linearVelocity)[0]) < 1:
					personaje.ApplyLinearImpulse(b2Vec2(2,0), personaje.position, 0)
				personaje.ApplyForceToCenter(b2Vec2(30,0), personaje.position)
			else:
				personaje.ApplyForceToCenter(b2Vec2(20,0), personaje.position)
				personaje.linearVelocity = b2Vec2(min(25,list(personaje.linearVelocity)[0]),list(personaje.linearVelocity)[1])
			
		else:
			if personaje.fixtures[0].body.contacts:
				personaje.ApplyLinearImpulse(b2Vec2(-(list(personaje.linearVelocity)[0])/5,0), personaje.position, 0)
			else:
				personaje.ApplyForceToCenter(b2Vec2(-(list(personaje.linearVelocity)[0])/20,0), personaje.position)
				
		personaje.linearVelocity = b2Vec2(max(-35,list(personaje.linearVelocity)[0]),list(personaje.linearVelocity)[1])
		personaje.linearVelocity = b2Vec2(min(35,list(personaje.linearVelocity)[0]),list(personaje.linearVelocity)[1])
			
			
		#personaje.linearVelocity = (20,personaje.linearVelocity[1])
		#personaje.ApplyLinearImpulse(b2Vec2(100,0), personaje.position, 0)
		
		for event in pygame.event.get():
		
			if event.type == pygame.MOUSEBUTTONDOWN:
				if event.button == 4:
					ANCHO_GL -= 5
				if event.button == 5:
					ANCHO_GL += 5
				ANCHO_GL = max(50,ANCHO_GL)
				ANCHO_GL = min(300,ANCHO_GL)
				ALTO_GL = ANCHO_GL*ALTO_VENTANA/ANCHO_VENTANA

			if event.type == pygame.KEYDOWN:
			
				if event.key == pygame.K_DELETE:
					lista_caixas = []
					lista_caixas_shape = []
					lista_suelo = []
					mundo = b2World(gravity=(0, -50))
					crear_mundo()
					personaje = mundo.CreateDynamicBody(position=(0,3), shapes=b2CircleShape(box=(1,2), density=10, friction=5, radius=1.5))
			
				if event.key == pygame.K_SPACE:
					for i in lista_caixas:
						i.ApplyLinearImpulse(b2Vec2(0,50), personaje.position, 0)
					
			if event.type == pygame.QUIT:
				pygame.quit()
				return
                
		#ACTUALIZAR VENTANA ######
		
		pygame.display.set_caption("caixas: "+str(len(lista_caixas)))
		
		pygame.display.flip()
		
		#AXUSTAR CAMARA
		
		pos_camara = [-personaje.position[0], -personaje.position[1]+ALTO_GL/2]
		
		reloj.tick(fps)

##############################################################
#OPENGL    ######################################################
##############################################################

def init_gl():
	glViewport(0, 0, ANCHO_VENTANA, ALTO_VENTANA)
	glClearColor(COLOR_FONDO, COLOR_FONDO, COLOR_FONDO, 1)
	glEnable(GL_BLEND);
	glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
	
def limpiar_ventana():
	glClear(GL_COLOR_BUFFER_BIT)
	glMatrixMode(GL_PROJECTION)
	glLoadIdentity()
	gluOrtho2D(-ANCHO_GL/2, ANCHO_GL/2, 0, ALTO_GL)
	glTranslatef(0 + pos_camara[0],0 + pos_camara[1], 0)
	glMatrixMode(GL_MODELVIEW)

def debuxar_rect(pos, vertices, angulo=False):
	glLoadIdentity()
	glTranslatef(pos[0], pos[1], 0)
	if angulo:
		glRotatef(math.degrees(angulo), 0, 0, 1)
	glBegin(GL_QUADS)
	glVertex2i(int(vertices[0][0]), int(vertices[0][1]))
	glVertex2i(int(vertices[1][0]), int(vertices[1][1]))
	glVertex2i(int(vertices[2][0]), int(vertices[2][1]))
	glVertex2i(int(vertices[3][0]), int(vertices[3][1]))
	glEnd()
	
def debuxar_circulo(pos, radio):
	glLoadIdentity()
	glEnable(GL_POLYGON_SMOOTH)
	glBegin(GL_POLYGON)
	for i in range(250):
		angulo = 2 * math.pi * i /250
		px = radio * math.cos(angulo)
		py = radio * math.sin(angulo)
		glVertex2f((px+pos[0]),(py+pos[1]))
	glEnd()
	
def debuxar_linea_borrado():
	glLoadIdentity()
	glColor4f(1, 0, 0, 0.8)
	glBegin(GL_LINES)
	glVertex2f(-ANCHO_GL+personaje.position[0], LINHA_BORRADO_Y)
	glVertex2f(ANCHO_GL+personaje.position[0], LINHA_BORRADO_Y)
	glEnd()
	
if __name__ == '__main__':
	main()