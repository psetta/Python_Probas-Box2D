# -*- coding: utf-8 -*-

from __future__ import division

import math
import pygame
import os
import sys
import ctypes

from constantes import *
from clases import *

from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from Box2D import *

if os.name == 'nt' and sys.getwindowsversion()[0] >= 6:
    ctypes.windll.user32.SetProcessDPIAware()

#CONTROLES

##########################################
#TECLAS DIRECCION E (W,A,S,D) -> MOVEMENTO DA BOLA
#Q e E -> ROTAN OS RECTANGULOS A CREAR
#BOTON ESQUERDO DO RATO -> CREAR RECTANGULOS
#BOTON DEREITO DO RATO -> ANULAR VERTICES DO RECTANGULO A CREAR
#RODA DO RATO -> ZOOM
#SUPR -> REINICIAR O XOGO
#F -> CAMBIAR TIPO DE RECTANGULO A CREAR
#G -> DEVOLVE DATOS DOS RECTANGULOS 'SUELO' CREADOS
#C -> MODO EDITOR(anula restriccions)
##########################################

#VARIABLES

pos_camara = [0,0]

descanso_mouse = 0

lista_caixas = []
lista_caixas_shape = []
lista_suelo = []

vertices_clicados = []
angulo_rectangulo_clicado = 0

tempo_inicio_nivel = 0

modo_debuxo = "caixa"

modo_editor = False

#BOX2D

FRICCION = 0.2

mundo = b2World(gravity=(0, -50))

def crear_mundo():
	global lista_suelo
	global lista_caixas
	global bola
	global bola_shape
	global rect_final
	
	lista_suelo.append(mundo.CreateStaticBody(position=(-90, 88), shapes=b2PolygonShape(box=(5,2))))
	lista_suelo.append(mundo.CreateStaticBody(position=(95, 27), shapes=b2PolygonShape(box=(2,4.5))))
	lista_suelo.append(mundo.CreateStaticBody(position=(-108.5, 95), angle=-0.4 ,shapes=b2PolygonShape(box=(12,2))))
	lista_suelo.append(mundo.CreateStaticBody(position=(-131.5, 110), angle=-0.7 ,shapes=b2PolygonShape(box=(12,2))))
	lista_suelo.append(mundo.CreateStaticBody(position=(-62, 90), angle=-0.5 ,shapes=b2PolygonShape(box=(2,7))))
	lista_suelo.append(mundo.CreateStaticBody(position=(-80, 80), angle=-0.5 ,shapes=b2PolygonShape(box=(3,2))))
	lista_suelo.append(mundo.CreateStaticBody(position=(-75, 70), angle=-0.5 ,shapes=b2PolygonShape(box=(3,2))))
	lista_suelo.append(mundo.CreateStaticBody(position=(-70, 60), angle=-0.5 ,shapes=b2PolygonShape(box=(3,2))))
	lista_suelo.append(mundo.CreateStaticBody(position=(5, 35), angle=0 ,shapes=b2PolygonShape(box=(4,4))))
	
	lista_caixas.append(mundo.CreateDynamicBody(position=(5,40)))
	lista_caixas_shape.append(lista_caixas[-1].CreatePolygonFixture(box=(70,3), density=2, friction=1))
	
	bola = mundo.CreateDynamicBody(position=(-90,110))
	bola_shape = bola.CreateCircleFixture(density=3, friction=0.5, radius=RADIO_BOLA, restitution=0.3)
	
	rect_final = (mundo.CreateStaticBody(position=(85, 20), shapes=b2PolygonShape(box=(8,2))))
	
	rect_final.fixtures[0].filterData.categoryBits = 0x0002
	rect_final.fixtures[0].filterData.maskBits = 0x0004
	
	bola_shape.filterData.categoryBits = 0x0004
	bola_shape.filterData.maskBits = 0xFFFF
	
crear_mundo()

lista_generador_caixas = [generador_caixas([55,120],0.5,0.5,10,0,1,0.6)]

rectangulo_a_crear = False
rectangulo_a_crear_shape = False

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
	global bola
	global bola_shape
	global vertices_clicados
	global cont_crear_caixa
	global angulo_rectangulo_clicado
	global modo_debuxo
	global tempo_inicio_nivel
	global rectangulo_a_crear
	global rectangulo_a_crear_shape
	global ANCHO_VENTANA
	global ALTO_VENTANA
	global ALTO_GL
	global tamanho_rectangulo_pintado
	global rect_final
	global modo_editor
	
	pygame.init()
	
	ventana = pygame.display.set_mode((ANCHO_VENTANA, ALTO_VENTANA), DOUBLEBUF|OPENGL|RESIZABLE )
	
	pygame.display.set_caption("")
	
	icono = pygame.image.load("img/icono.png").convert_alpha()
	
	pygame.display. set_icon (icono)
	
	init_gl()
	
	fps = 60
	vel_iters = 10
	pos_iters = 10
	
	#ESTABLECER VALOR DEFECTO AO RECTANGULO QUE PODEMOS PINTAR CO RATO
	tamanho_rectangulo_pintado = False
	
	#CANTIDADE AZUL RECTANGULO FINAL
	color_rojo_final = [0,0]
	
	####################################################################################
	### BUCLE XOGO
	####################################################################################

	while True:
	
		reloj = pygame.time.Clock()
		
		if not tempo_inicio_nivel:
			mundo.Step(1 / fps, vel_iters, pos_iters)
		else:
			tempo_inicio_nivel -= 1
		
		#LIMPIAR VENTANA ######
		
		limpiar_ventana()
		
		#CREAR CAIXAS
		
		if not tempo_inicio_nivel:
			for i in lista_generador_caixas:
				if not i.cont:
					if len(lista_caixas) < 350:
						lista_caixas.append(mundo.CreateDynamicBody
							(position=(i.pos[0],i.pos[1])))
						lista_caixas_shape.append(lista_caixas[-1].CreatePolygonFixture(box=(i.ancho,i.alto), density=i.densidad, friction=i.friccion))
					i.cont = i.cont0
				else:
					i.cont -= 1
		
		######################################
		#DEBUXAR #############################
		######################################
		
		for i in lista_caixas:
			debuxar_rect(i.position, list(i.fixtures[0].shape), i.angle, [1.0, 1.0, 1.0,1])
		
		for i in lista_suelo:
			debuxar_rect(i.position, list(i.fixtures[0].shape), i.angle, [0.0, 0.5, 1.0, 1])
			
		#O COLOR DA PLATAFORMA 'FINAL' VARIA CO TEMPO
			
		if color_rojo_final[1] < 0:
			color_rojo_final[0] = 1
		if color_rojo_final[1] > 1:
			color_rojo_final[0] = 0
			
		if color_rojo_final[0] == 1:
			color_rojo_final[1] += 0.02
		else:
			color_rojo_final[1] -= 0.02
			
		debuxar_rect(rect_final.position, list(rect_final.fixtures[0].shape), rect_final.angle, [color_rojo_final[1],1,0,1], True)
		
		if bola:
			debuxar_circulo(bola.position, RADIO_BOLA)
		
		for i in vertices_clicados:
			debuxar_punto(i)
			
		if len(vertices_clicados) >= 1:
			debuxar_rectangulo_a_pintar(vertices_clicados+[pos_mouse_gl],angulo_rectangulo_clicado)
				
		debuxar_linea_borrado()
		
		#BORRADO DE CAIXAS
		
		for i in range(len(lista_caixas)):
			if lista_caixas[i].position[1] < LINHA_BORRADO_Y:
				lista_caixas[i].DestroyFixture(lista_caixas_shape[i])
				lista_caixas.remove(lista_caixas[i])
				lista_caixas_shape.remove(lista_caixas_shape[i])
				break
			if bola and bola.position[1] < LINHA_BORRADO_Y:
				bola.DestroyFixture(bola_shape)
				bola_shape = False
				bola = False
				
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
			
		pos_mouse_gl = [pos_mouse[0]*ANCHO_GL/ANCHO_VENTANA-ANCHO_GL/2-pos_camara[0],ALTO_GL-(pos_mouse[1]*ALTO_GL/ALTO_VENTANA)-pos_camara[1]]
		
		if descanso_mouse == 0 and (teclas_mouse_pulsadas[0] or teclas_mouse_pulsadas[2]):
			if teclas_mouse_pulsadas[0] and len(vertices_clicados) <= 1:
				vertices_clicados.append(pos_mouse_gl)
				descanso_mouse = TEMPO_ESPERA_MOUSE
			if teclas_mouse_pulsadas[2]:
				vertices_clicados = []
				angulo_rectangulo_clicado = 0
		
		#TECLAS ######
		
		tecla_pulsada = pygame.key.get_pressed()
		
		if (tecla_pulsada[K_UP] or tecla_pulsada[K_w]): 
			pos_camara[1] -= 1
			
		elif tecla_pulsada[K_DOWN] or tecla_pulsada[K_s]:
			pos_camara[1] += 1
		
		if tecla_pulsada[K_LEFT] or tecla_pulsada[K_a]:
			pos_camara[0] += 1
			
		elif tecla_pulsada[K_RIGHT] or tecla_pulsada[K_d]:
			pos_camara[0] -= 1
		
		if tecla_pulsada[K_e] and len(vertices_clicados) >= 1:
			angulo_rectangulo_clicado -= 0.02
		elif tecla_pulsada[K_q] and len(vertices_clicados) >= 1:
			angulo_rectangulo_clicado += 0.02
		
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
					pos_camara = [0, 0]
					vertices_clicados = []
					
				if event.key == pygame.K_f:
					if modo_debuxo == "bloque":
						modo_debuxo = "caixa"
					else:
						modo_debuxo = "bloque"
						
				if event.key == pygame.K_g:
					for i in lista_suelo:
						print "posicion", i.position, i.fixtures[0].shape, "angulo", i.angle
						print "-" * 10
					print "#" * 50
					
				if event.key == pygame.K_c:
					if modo_editor:
						modo_editor = False
					else:
						modo_editor = True
			
				if event.key == pygame.K_SPACE:
				
					if len(vertices_clicados) <= 1 or not rectangulo_a_crear:
						vertices_clicados = []
						angulo_rectangulo_clicado = 0
						
					elif abs(vertices_clicados[0][0] - vertices_clicados[1][0]) and abs(vertices_clicados[0][1] - vertices_clicados[1][1]):
					
						vertices_clicados = sorted(vertices_clicados, key = lambda x: x[0])
					
						pos_rectangulo_debuxado = [(vertices_clicados[0][0]+vertices_clicados[1][0])/2,(vertices_clicados[0][1]+vertices_clicados[1][1])/2]
						tamanho_rectangulo_pintado = [(vertices_clicados[1][0]-vertices_clicados[0][0])/2, 
							(sorted(vertices_clicados, key = lambda x : x[1])[1][1]-sorted(vertices_clicados, key = lambda x : x[1])[0][1])/2]
							
						if modo_editor or ((tamanho_rectangulo_pintado[0] >= TAMANHO_MIN_RECT_ANCHO and 
							tamanho_rectangulo_pintado[1] >= TAMANHO_MIN_RECT_ALTO) and 
							tamanho_rectangulo_pintado[0] <= TAMANHO_MAX_RECT_ANCHO and 
							tamanho_rectangulo_pintado[1] <= TAMANHO_MAX_RECT_ALTO
							and ((not rectangulo_a_crear.contacts) or (rectangulo_a_crear.contacts and not rectangulo_a_crear.contacts[0].contact.touching))):
							
							if modo_debuxo == "bloque":
								lista_suelo.append(mundo.CreateStaticBody(
									position=(pos_rectangulo_debuxado[0],pos_rectangulo_debuxado[1]), 
									angle = angulo_rectangulo_clicado,
									shapes=b2PolygonShape(box=(
											tamanho_rectangulo_pintado[0],
											tamanho_rectangulo_pintado[1])
											)))
							else:
								lista_caixas.append(mundo.CreateDynamicBody(
									position=(pos_rectangulo_debuxado[0],pos_rectangulo_debuxado[1]),
									angle = angulo_rectangulo_clicado))

								lista_caixas_shape.append(lista_caixas[-1].CreatePolygonFixture(box=(
									tamanho_rectangulo_pintado[0], tamanho_rectangulo_pintado[1]),
									density=1, friction=0.5))
								
						vertices_clicados = []
						angulo_rectangulo_clicado = 0
						
					else:
						vertices_clicados = []
						angulo_rectangulo_clicado = 0
						
			if event.type == VIDEORESIZE:
				
				#REDIMENSIONAR
		
				ANCHO_VENTANA = event.dict['size'][0]
				ALTO_VENTANA = event.dict['size'][1]
				ventana = pygame.display.set_mode((ANCHO_VENTANA, ALTO_VENTANA), DOUBLEBUF|OPENGL|RESIZABLE )
				ALTO_GL = ANCHO_GL*ALTO_VENTANA/ANCHO_VENTANA
				init_gl()
				
			if event.type == pygame.QUIT:
				pygame.quit()
				return
				
		#RECTANGULO A CREAR
		
		if len(vertices_clicados) >= 1:
		
			if len(vertices_clicados) == 1:
				vertices_clicados_aux = vertices_clicados + [pos_mouse_gl]
			else:
				vertices_clicados_aux = vertices_clicados[:]

			if not vertices_clicados_aux[0][0] == vertices_clicados_aux[1][0] and not vertices_clicados_aux[0][1] == vertices_clicados_aux[1][1]:
					
				if rectangulo_a_crear:
					rectangulo_a_crear.DestroyFixture(rectangulo_a_crear.fixtures[0])
			
			
				vertices_clicados_aux = sorted(vertices_clicados_aux, key = lambda x: x[0])
				pos_rectangulo_debuxado = [(vertices_clicados_aux[0][0]+vertices_clicados_aux[1][0])/2,(vertices_clicados_aux[0][1]+vertices_clicados_aux[1][1])/2]
				tamanho_rectangulo_pintado = [(vertices_clicados_aux[1][0]-vertices_clicados_aux[0][0])/2, 
						(sorted(vertices_clicados_aux, key = lambda x : x[1])[1][1]-sorted(vertices_clicados_aux, key = lambda x : x[1])[0][1])/2]
		
				rectangulo_a_crear = (mundo.CreateDynamicBody(
								position=(pos_rectangulo_debuxado[0],pos_rectangulo_debuxado[1]), 
								angle = angulo_rectangulo_clicado))
								
				rectangulo_a_crear_shape = rectangulo_a_crear.CreatePolygonFixture(box=(
								tamanho_rectangulo_pintado[0], tamanho_rectangulo_pintado[1]),
								density=0.2, friction=0.6)
											
				rectangulo_a_crear.fixtures[0].sensor = True
											
		else:
			rectangulo_a_crear = False
			rectangulo_a_crear_shape = False
                
		#ACTUALIZAR VENTANA ######
		
		pygame.display.flip()

		
		reloj.tick(fps)
		
		
#################################################################
#OPENGL    ######################################################
#################################################################

def init_gl():
	glViewport(0, 0, ANCHO_VENTANA, ALTO_VENTANA)
	glClearColor(COLOR_FONDO, COLOR_FONDO, COLOR_FONDO, 1)
	glEnable(GL_BLEND);
	glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
	glEnable(GL_LINE_SMOOTH)
	glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
	
def limpiar_ventana():
	glClear(GL_COLOR_BUFFER_BIT)
	glMatrixMode(GL_PROJECTION)
	glLoadIdentity()
	gluOrtho2D(-ANCHO_GL/2, ANCHO_GL/2, 0, ALTO_GL)
	glTranslatef(0 + pos_camara[0],0 + pos_camara[1], 0)
	glMatrixMode(GL_MODELVIEW)

def debuxar_rect(pos, vertices, angulo, color, fill=False):
	glLoadIdentity()
	glColor4f(color[0], color[1], color[2], color[3])
	glTranslatef(pos[0], pos[1], 0)
	if angulo:
		glRotatef(math.degrees(angulo), 0, 0, 1)
	glBegin(GL_LINES)
	for i in range(len(vertices)):
		glVertex2f(vertices[i-1][0],vertices[i-1][1])
		glVertex2f(vertices[i][0],vertices[i][1])
	glEnd()
	if fill:
		glPolygonMode (GL_FRONT_AND_BACK, GL_FILL)
		glColor4f(color[0], color[1], color[2], 0.3)
		glBegin(GL_POLYGON)
		for i in range(len(vertices)):
			glVertex2f(vertices[i][0],vertices[i][1])
		glEnd()
	
def debuxar_circulo(pos, radio):
	glLoadIdentity()
	glColor4f(0.1, 0.9, 0.1,0.2)
	glPolygonMode (GL_FRONT_AND_BACK, GL_FILL)
	glBegin(GL_POLYGON)
	for i in range(50):
		angulo = 2 * math.pi * i /50
		px = radio * math.cos(angulo)
		py = radio * math.sin(angulo)
		glVertex2f((px+pos[0]),(py+pos[1]))
	glEnd()
	
	glColor3f(0.1, 0.9, 0.1)
	glPolygonMode (GL_FRONT_AND_BACK, GL_LINE)
	glBegin(GL_POLYGON)
	for i in range(50):
		angulo = 2 * math.pi * i /50
		px = radio * math.cos(angulo)
		py = radio * math.sin(angulo)
		glVertex2f((px+pos[0]),(py+pos[1]))
	glEnd()
	glPolygonMode (GL_FRONT_AND_BACK, GL_FILL)
	
def debuxar_linea_borrado():
	glLoadIdentity()
	glColor4f(1, 0, 0, 0.5)
	glBegin(GL_LINES)
	glVertex2f(-ANCHO_GL-pos_camara[0], LINHA_BORRADO_Y)
	glVertex2f(ANCHO_GL-pos_camara[0], LINHA_BORRADO_Y)
	glEnd()
	
def debuxar_punto(pos):
	glLoadIdentity()
	glPointSize(2)
	glColor4f(1, 0.5, 0.5, 0.5)
	glBegin(GL_POINTS)
	glVertex2f(pos[0], pos[1])
	glEnd()

def debuxar_rectangulo_a_pintar(vertices,angulo):
	ancho_cadro = vertices[1][0] - vertices[0][0]
	alto_cadro = vertices[0][1] - vertices[1][1]
	pos = [vertices[0][0]+ancho_cadro/2, vertices[1][1]+alto_cadro/2]
	glLoadIdentity()
	if (tamanho_rectangulo_pintado and ((tamanho_rectangulo_pintado[0] > TAMANHO_MAX_RECT_ANCHO or
									tamanho_rectangulo_pintado[1] > TAMANHO_MAX_RECT_ALTO)
									or (tamanho_rectangulo_pintado[0] < TAMANHO_MIN_RECT_ANCHO or
										tamanho_rectangulo_pintado[1] < TAMANHO_MIN_RECT_ALTO))):
		glColor4f(1, 0, 0, 0.1)
	elif modo_debuxo == "bloque":
		glColor4f(0.5, 0.5, 1, 0.2)
	else:
		glColor4f(0.8, 0.8, 0.8, 0.2)
	glTranslatef(pos[0], pos[1], 0)
	glRotatef(math.degrees(angulo),0, 0, 1)
	glRectf(vertices[0][0]-pos[0],vertices[0][1]-pos[1],vertices[1][0]-pos[0],vertices[1][1]-pos[1])
	glPolygonMode (GL_FRONT_AND_BACK, GL_LINE)
	if rectangulo_a_crear and rectangulo_a_crear.contacts and rectangulo_a_crear.contacts[0].contact.touching:
		glColor4f(1, 0, 0, 0.9)
	elif modo_debuxo == "bloque":
		glColor4f(0.0, 0.5, 1.0, 0.5)
	else:
		glColor4f(1, 1, 1, 0.5)
	glRectf(vertices[0][0]-pos[0],vertices[0][1]-pos[1],vertices[1][0]-pos[0],vertices[1][1]-pos[1])
	
def debuxar_texto():
	glLoadIdentity()
	glColor3f(1, 1, 1)
	
if __name__ == '__main__':
	main()