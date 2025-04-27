import pygame
import sys
import json
import random

# Inicializar pygame
pygame.init()

# Tamaño de la ventana
ANCHO, ALTO = 1024, 768
ventana = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Clue: Edición Los Simpson")

# Colores
NEGRO = (0, 0, 0)
BLANCO = (255, 255, 255)
GRIS = (100, 100, 100)
AZUL = (50, 50, 255)
ROJO = (200, 0, 0)
AMARILLO = (255, 255, 0)
DORADO = (255, 215, 0)
VERDE = (0, 255, 0)
deduciendo = False
investigacion = False
caso = ""
seleccionado = ""
seccion = ""
deduccion = {"sospechoso": None, "locacion": None, "arma": None}
resultado = []
intentos_restantes = 5  # Intentos disponibles para investigar
mensaje_temporal = ""
temporizador_mensaje = 0
investigado = False
# Fuentes
fuente_titulo = pygame.font.SysFont("Arial", 60, bold=True)
fuente_boton = pygame.font.SysFont("Arial", 35, bold=True)

# Cargar imagen de fondo
fondo = pygame.image.load("imagenes/fondo/fondo_menu.png")
fondo = pygame.transform.scale(fondo, (ANCHO, ALTO))

# Cargar y reproducir música
pygame.mixer.music.load('Soundtrack.mp3')
pygame.mixer.music.play(-1)
pygame.mixer.music.set_volume(0.3)
sonido_tecla = pygame.mixer.Sound('tecla.wav')
sonido_tecla.set_volume(0.1)

# Utilidad: dibujar botones
# Variable para controlar si el botón ya fue presionado
boton_presionado_global = False

def dibujar_boton(texto, x, y, w, h, color, color_texto, accion=None):
    global boton_presionado_global

    sombra_offset = 5
    pygame.draw.rect(ventana, (0, 0, 0), (x + sombra_offset, y + sombra_offset, w, h), 0)
    pygame.draw.rect(ventana, color, (x, y, w, h), border_radius=15)

    texto_render = fuente_boton.render(texto, True, color_texto)
    ventana.blit(texto_render, (x + (w - texto_render.get_width()) // 2, y + (h - texto_render.get_height()) // 2))

    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()

    # Si el mouse está sobre el botón
    if x < mouse[0] < x + w and y < mouse[1] < y + h:
        pygame.draw.rect(ventana, (200, 200, 0), (x, y, w, h), 5)

        # Detectar el "click" solo una vez
        if click[0] == 1 and not boton_presionado_global:
            boton_presionado_global = True  # evitar múltiples llamadas
            if accion is not None:
                accion()

    # Resetear cuando se suelta el botón del mouse
    if click[0] == 0:
        boton_presionado_global = False

def seleccionar_caso_aleatorio(ruta_json="clue_data.json"):
    try:
        with open(ruta_json, "r", encoding="utf-8") as archivo:
            casos = json.load(archivo)
            caso_seleccionado = random.choice(casos)
            return caso_seleccionado
    except FileNotFoundError:
        print("❌ No se encontró el archivo de casos.")
        return None
    except json.JSONDecodeError:
        print("❌ Error al decodificar el archivo JSON.")
        return None
    
# Salir del juego
def salir():
    pygame.quit()
    sys.exit()

# Mostrar reglas con fondo negro y borde rojo
def ver_reglas():
    reglas_original = [
        "• Tienes 5 turnos para descubrir al asesino.",
        "• Puedes interrogar personajes, inspeccionar armas o locaciones.",
        "• Elige al culpable, el arma y la locación al final.",
        "• Si aciertas, ganas el juego. Si fallas, pierdes."
    ]

    # Preparamos las líneas ajustadas al ancho máximo
    margen_lateral = 80
    max_ancho_texto = ANCHO - 2 * (margen_lateral + 20)
    lineas_ajustadas = []
    for regla in reglas_original:
        lineas_ajustadas += renderizar_texto_ajustado(regla, fuente_boton, max_ancho_texto)

    # Calcular tamaño del recuadro
    rect_x = margen_lateral
    rect_y = 120
    rect_w = ANCHO - 2 * margen_lateral
    rect_h = len(lineas_ajustadas) * 40 + 40

    fondo_texto = pygame.Surface((rect_w, rect_h), pygame.SRCALPHA)
    fondo_texto.fill((0, 0, 0, 180))  # negro semitransparente

    corriendo = True
    while corriendo:
        ventana.blit(fondo, (0, 0))

        # Título
        titulo = fuente_titulo.render("Reglas del Juego", True, AMARILLO)
        ventana.blit(titulo, (ANCHO // 2 - titulo.get_width() // 2, 40))

        # Cuadro negro con borde rojo
        ventana.blit(fondo_texto, (rect_x, rect_y))
        pygame.draw.rect(ventana, ROJO, (rect_x, rect_y, rect_w, rect_h), 5)

        # Dibujar todas las líneas de texto
        for i, linea in enumerate(lineas_ajustadas):
            texto = fuente_boton.render(linea, True, BLANCO)
            ventana.blit(texto, (rect_x + 20, rect_y + 20 + i * 40))

        # Botón para volver
        dibujar_boton("Volver", 20, 20, 120, 40, ROJO, AMARILLO, menu_principal)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                salir()

        pygame.display.update()

def mostrar_personajes():
    global investigacion
    personajes = ["homero", "marge", "bart", "lisa", "flanders"]
    imagenes = [pygame.image.load(f"imagenes/personajes/{p}.png") for p in personajes]

    corriendo = True
    while corriendo:
        ventana.blit(fondo, (0, 0))

        # Título
        titulo = fuente_titulo.render("Sospechosos", True, AMARILLO)
        ventana.blit(titulo, (ANCHO // 2 - titulo.get_width() // 2, 30))

        imagen_ancho = 200
        imagen_alto = 200
        espacio_horizontal = 40
        espacio_vertical = 30

        total_columnas = 3
        total_filas = 2

        # Calculamos inicio x para centrar las columnas
        total_anchura_fila = (imagen_ancho * total_columnas) + (espacio_horizontal * (total_columnas - 1))
        inicio_x = (ANCHO - total_anchura_fila) // 2

        # Coordenada base Y
        inicio_y = 120
        rect_imagenes = []  # NUEVO: guardar las áreas clicables

        for i, img in enumerate(imagenes):
            img = pygame.transform.scale(img, (imagen_ancho, imagen_alto))
            fila = i // total_columnas
            col = i % total_columnas if fila == 0 else i - 3
            x = inicio_x + col * (imagen_ancho + espacio_horizontal)
            y = inicio_y + fila * (imagen_alto + espacio_vertical + 40)
            ventana.blit(img, (x, y))
            nombre = fuente_boton.render(personajes[i].capitalize(), True, BLANCO)
            ventana.blit(nombre, (x + (imagen_ancho - nombre.get_width()) // 2, y + imagen_alto + 5))
            rect_imagenes.append((pygame.Rect(x, y, imagen_ancho, imagen_alto), personajes[i]))  # NUEVO
        if investigacion:
            dibujar_boton("Volver", ANCHO - 220, ALTO - 100, 180, 50, ROJO, AMARILLO, pantalla_investigacion)
        else:
            dibujar_boton("Volver", 20, 20, 120, 40, ROJO, AMARILLO, menu_principal)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                salir()
            elif evento.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                for rect, nombre in rect_imagenes:
                    if rect.collidepoint(pos):
                        mostrar_detalle(nombre, "personajes")

        pygame.display.update()

def mostrar_locaciones():
    global investigacion
    locaciones = ["casa_simpson", "casa_flanders", "bar_moe", "krustyland", "kwikemart"]
    nombres = ["Casa Simpson", "Casa Flanders", "Bar de Moe", "Krustyland", "Kwik-E-Mart"]
    imagenes = [pygame.image.load(f"imagenes/locaciones/{l}.png") for l in locaciones]

    corriendo = True
    while corriendo:
        ventana.blit(fondo, (0, 0))

        titulo = fuente_titulo.render("Locaciones", True, AMARILLO)
        ventana.blit(titulo, (ANCHO // 2 - titulo.get_width() // 2, 30))

        imagen_ancho = 200
        imagen_alto = 200
        espacio_horizontal = 40
        espacio_vertical = 30

        total_columnas = 3
        inicio_x = (ANCHO - ((imagen_ancho * total_columnas) + (espacio_horizontal * (total_columnas - 1)))) // 2
        inicio_y = 120
        rect_imagenes = []  # NUEVO: guardar las áreas clicables

        for i, img in enumerate(imagenes):
            img = pygame.transform.scale(img, (imagen_ancho, imagen_alto))
            fila = i // total_columnas
            col = i % total_columnas if fila == 0 else i - 3
            x = inicio_x + col * (imagen_ancho + espacio_horizontal)
            y = inicio_y + fila * (imagen_alto + espacio_vertical + 40)
            ventana.blit(img, (x, y))
            nombre = fuente_boton.render(locaciones[i].capitalize(), True, BLANCO)
            ventana.blit(nombre, (x + (imagen_ancho - nombre.get_width()) // 2, y + imagen_alto + 5))
            rect_imagenes.append((pygame.Rect(x, y, imagen_ancho, imagen_alto), locaciones[i]))  # NUEVO

        if investigacion:
            dibujar_boton("Volver", ANCHO - 220, ALTO - 100, 180, 50, ROJO, AMARILLO, pantalla_investigacion)
        else:
            dibujar_boton("Volver", 20, 20, 120, 40, ROJO, AMARILLO, menu_principal)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                salir()
            elif evento.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                for rect, nombre in rect_imagenes:
                    if rect.collidepoint(pos):
                        mostrar_detalle(nombre, "locaciones")

        pygame.display.update()

def mostrar_armas():
    global investigacion
    armas = ["pistola", "cuchillo", "jeringa", "hacha", "veneno"]
    imagenes = [pygame.image.load(f"imagenes/armas/{a}.png") for a in armas]

    corriendo = True
    while corriendo:
        ventana.blit(fondo, (0, 0))

        titulo = fuente_titulo.render("Armas", True, AMARILLO)
        ventana.blit(titulo, (ANCHO // 2 - titulo.get_width() // 2, 30))

        imagen_ancho = 200
        imagen_alto = 200
        espacio_horizontal = 40
        espacio_vertical = 30

        total_columnas = 3
        inicio_x = (ANCHO - ((imagen_ancho * total_columnas) + (espacio_horizontal * (total_columnas - 1)))) // 2
        inicio_y = 120

        rect_imagenes = []  # NUEVO: guardar las áreas clicables

        for i, img in enumerate(imagenes):
            img = pygame.transform.scale(img, (imagen_ancho, imagen_alto))
            fila = i // total_columnas
            col = i % total_columnas if fila == 0 else i - 3
            x = inicio_x + col * (imagen_ancho + espacio_horizontal)
            y = inicio_y + fila * (imagen_alto + espacio_vertical + 40)
            ventana.blit(img, (x, y))
            nombre = fuente_boton.render(armas[i].capitalize(), True, BLANCO)
            ventana.blit(nombre, (x + (imagen_ancho - nombre.get_width()) // 2, y + imagen_alto + 5))
            rect_imagenes.append((pygame.Rect(x, y, imagen_ancho, imagen_alto), armas[i]))  # NUEVO

        if investigacion:
            dibujar_boton("Volver", ANCHO - 220, ALTO - 100, 180, 50, ROJO, AMARILLO, pantalla_investigacion)
        else:
            dibujar_boton("Volver", 20, 20, 120, 40, ROJO, AMARILLO, menu_principal)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                salir()
            elif evento.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                for rect, nombre in rect_imagenes:
                    if rect.collidepoint(pos):
                        mostrar_detalle(nombre, "armas")
        pygame.display.update()

import textwrap

def renderizar_texto_ajustado(texto, fuente, max_ancho):
    """
    Divide el texto en líneas que se ajusten al ancho máximo permitido.
    """
    palabras = texto.split()
    lineas = []
    linea_actual = ""
    for palabra in palabras:
        test_linea = f"{linea_actual} {palabra}".strip()
        if fuente.size(test_linea)[0] <= max_ancho:
            linea_actual = test_linea
        else:
            lineas.append(linea_actual)
            linea_actual = palabra
    if linea_actual:
        lineas.append(linea_actual)
    return lineas

def introduccion_caso():
    texto_original = (
        "¡Atención en Springfield! Moe ha sido encontrado sin vida en circunstancias misteriosas. "
        "La policía local está desconcertada y necesita tu ayuda. Varios personajes han sido vistos "
        "en diferentes partes del pueblo, cada uno con posibles motivos y oportunidades. "
        "¿Podrás resolver este misterio antes de que sea demasiado tarde?"
    )

    # Parámetros de texto y cuadro
    margen_lateral = 80
    max_ancho_texto = ANCHO - 2 * (margen_lateral + 20)
    lineas_ajustadas = renderizar_texto_ajustado(texto_original, fuente_boton, max_ancho_texto)

    # Fondo de texto transparente
    rect_x = margen_lateral
    rect_y = 130
    rect_w = ANCHO - 2 * margen_lateral
    rect_h = len(lineas_ajustadas) * 40 + 40

    fondo_texto = pygame.Surface((rect_w, rect_h), pygame.SRCALPHA)
    fondo_texto.fill((0, 0, 0, 180))  # negro semitransparente

    # Inicialización de animación
    linea_actual = 0
    letra_actual = 0
    reloj = pygame.time.Clock()
    velocidad_lectura = 40  # letras por segundo
    tiempo_ultima_letra = pygame.time.get_ticks()

    letras_por_sonido = 4  # Cada cuántas letras sonará el sonido
    contador_letras = 0  # Contador de letras para controlar sonido

    # Cargar sonido de tecla
    sonido_tecla = pygame.mixer.Sound("tecla.wav")

    corriendo = True
    while corriendo:
        ventana.blit(fondo, (0, 0))

        # Título
        titulo = fuente_titulo.render("El Caso", True, AMARILLO)
        ventana.blit(titulo, (ANCHO // 2 - titulo.get_width() // 2, 50))

        # Fondo del texto con borde rojo
        ventana.blit(fondo_texto, (rect_x, rect_y))
        pygame.draw.rect(ventana, ROJO, (rect_x, rect_y, rect_w, rect_h), 5)

        # Mostrar texto animado tipo máquina de escribir
        for i in range(linea_actual + 1):
            linea = lineas_ajustadas[i]
            if i == linea_actual:
                visible_text = linea[:letra_actual]
            else:
                visible_text = linea
            texto_render = fuente_boton.render(visible_text, True, BLANCO)
            ventana.blit(texto_render, (rect_x + 20, rect_y + 20 + i * 40))

        # Control de letras que se muestran
        tiempo_actual = pygame.time.get_ticks()
        if tiempo_actual - tiempo_ultima_letra > 1000 // velocidad_lectura:
            tiempo_ultima_letra = tiempo_actual
            if linea_actual < len(lineas_ajustadas):
                if letra_actual < len(lineas_ajustadas[linea_actual]):
                    letra_actual += 1
                    contador_letras += 1

                    # Sonar cada X letras
                    if contador_letras >= letras_por_sonido:
                        sonido_tecla.play()
                        contador_letras = 0
                else:
                    if linea_actual < len(lineas_ajustadas) - 1:
                        linea_actual += 1
                        letra_actual = 0

        # Botón "Siguiente"
        if linea_actual == len(lineas_ajustadas) - 1 and letra_actual == len(lineas_ajustadas[-1]):
            dibujar_boton("Investigar", ANCHO - 220, ALTO - 100, 180, 50, ROJO, AMARILLO, pantalla_investigacion)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                salir()

        pygame.display.update()
        reloj.tick(60)

def mostrar_mensaje(texto, duracion=1500):
    global mensaje_temporal, temporizador_mensaje
    mensaje_temporal = texto
    temporizador_mensaje = pygame.time.get_ticks() + duracion

def realizar_accion(nombre_accion):
    global intentos_restantes
    if intentos_restantes > 0:
        intentos_restantes -= 1
        mostrar_mensaje(f"Realizaste: {nombre_accion}")
    else:
        mostrar_mensaje("¡No te quedan más intentos!")

def pantalla_investigacion():
    global intentos_restantes; global investigacion; global deduciendo
    corriendo = True
    investigacion = True
    while corriendo:
        ventana.blit(fondo, (0, 0))

        # Título
        titulo = fuente_titulo.render("Fase de Investigación", True, DORADO)
        ventana.blit(titulo, (ANCHO // 2 - titulo.get_width() // 2, 40))

        # Mostrar intentos restantes
        texto_intentos = fuente_boton.render(f"Intentos restantes: {intentos_restantes}", True, BLANCO)
        ventana.blit(texto_intentos, (ANCHO // 2 - texto_intentos.get_width() // 2, 120))

        # Botones de acción
        if intentos_restantes > 0:
            dibujar_boton("Interrogar Sospechoso", 300, 200, 400, 60, AZUL, BLANCO, lambda: usar_intento("sospechoso"))
            dibujar_boton("Revisar Locación", 300, 300, 400, 60, AZUL, BLANCO, lambda: usar_intento("locacion"))
            dibujar_boton("Inspeccionar Arma", 300, 400, 400, 60, AZUL, BLANCO, lambda: usar_intento("arma"))
        else:
            sin_intentos = fuente_boton.render("¡Sin intentos restantes! Haz tu deducción final.", True, ROJO)
            ventana.blit(sin_intentos, (ANCHO // 2 - sin_intentos.get_width() // 2, 500))
            deduciendo = True
            corriendo = False
            hacer_deduccion_final()

        # Botón volver
        dibujar_boton("Volver al menú", 20, 20, 200, 50, ROJO, AMARILLO, menu_principal)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                salir()

        pygame.display.update()
def usar_intento(tipo):
    global intentos_restantes, caso, seccion
    if intentos_restantes == 5:
        caso = seleccionar_caso_aleatorio()
    if tipo == "sospechoso":
            seccion = tipo
            mostrar_personajes()
    elif tipo == "locacion":
            seccion = tipo
            mostrar_locaciones()
    elif tipo == "arma":
            seccion = tipo
            mostrar_armas() 
            
def mostrar_detalle(nombre, tipo):
    global investigacion, intentos_restantes, deduciendo, seleccionado, investigado, caso
    # Cargar imagen y descripción dependiendo del tipo
    ruta_img = f"imagenes/{tipo}/{nombre}.png"
    imagen = pygame.image.load(ruta_img)
    imagen = pygame.transform.scale(imagen, (300, 300))

    # Simulamos una descripción (después se puede usar JSON para personalizar)
    descripciones = {
        "homero": "Homero Simpson es el padre de la familia. Le encanta comer rosquillas.",
        "marge": "Marge Simpson es la madre, conocida por su paciencia y su gran amor por su familia.",
        "bart": "Bart Simpson es el hijo travieso de la familia, conocido por sus bromas y travesuras.",
        "lisa": "Lisa Simpson es la hija intelectual, conocida por su talento para la música y la academia.",
        "flanders": "Ned Flanders es el vecino de los Simpson, conocido por su fe religiosa y su actitud amable.",
        "casa_simpson": "La casa de los Simpson, lugar donde viven los personajes principales.",
        "casa_flanders": "La casa de los Flanders, los amables vecinos de los Simpson.",
        "bar_moe": "El bar de Moe, lugar donde Homero y sus amigos suelen pasar su tiempo.",
        "krustyland": "Krustyland, el parque de diversiones de Krusty el payaso.",
        "kwikemart": "Kwik-E-Mart, la tienda de conveniencia de Apu.",
        "pistola": "Una pistola, usada generalmente para defensa.",
        "cuchillo": "Un cuchillo, herramienta de cocina que también puede ser un arma.",
        "jeringa": "Una jeringa, utilizada para inyecciones.",
        "hacha": "Un hacha, utilizada para cortar madera, pero también puede ser peligrosa.",
        "veneno": "Veneno, un líquido letal que puede matar en pequeñas dosis."
    }
    descripcion = descripciones.get(nombre, "Sin descripción disponible.")
    if investigacion: 
        if caso["caso"] == 1:
            descripcion = caso[nombre]
        elif caso["caso"] == 2: 
            descripcion = caso[nombre]
        elif caso["caso"] == 3: 
            descripcion = caso[nombre]
        elif caso["caso"] == 4:
            descripcion = caso[nombre]
        elif caso["caso"] == 5:  
            descripcion = caso[nombre]
        intentos_restantes -= 1
    if deduciendo:
        descripcion = nombre
    corriendo = True
    while corriendo:
        ventana.fill(NEGRO)
        ventana.blit(imagen, (ANCHO // 2 - 150, 100))

        titulo = fuente_titulo.render(nombre.capitalize().replace("_", " "), True, DORADO)
        ventana.blit(titulo, (ANCHO // 2 - titulo.get_width() // 2, 30))

        # Descripción en varias líneas
        lineas = textwrap.wrap(descripcion, width=50)
        for i, linea in enumerate(lineas):
            texto = fuente_boton.render(linea, True, BLANCO)
            ventana.blit(texto, (ANCHO // 2 - texto.get_width() // 2, 450 + i * 40))
        if investigacion:
            dibujar_boton("Investigar", ANCHO - 220, ALTO - 100, 180, 50, ROJO, AMARILLO, pantalla_investigacion)
        else:
            dibujar_boton("Volver", 20, 20, 120, 40, ROJO, AMARILLO, menu_principal)
        if deduciendo:
            dibujar_boton("Seleccionar", ANCHO - 220, ALTO - 100, 180, 50, ROJO, AMARILLO, hacer_deduccion_final)
            seleccionado = nombre
            investigado = True
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                salir()

        pygame.display.update()
def hacer_deduccion_final():
    global seleccionado, seccion, deduccion, resultado, investigado
    corriendo = True
    while corriendo:
        ventana.blit(fondo, (0, 0))

        # Título
        titulo = fuente_titulo.render("Fase de Deducción", True, DORADO)
        ventana.blit(titulo, (ANCHO // 2 - titulo.get_width() // 2, 40))

        dibujar_boton("Seleccionar Sospechoso", 300, 200, 400, 60, AZUL, BLANCO, lambda: usar_intento("sospechoso"))
        dibujar_boton("Seleccionar Locación", 300, 300, 400, 60, AZUL, BLANCO, lambda: usar_intento("locacion"))
        dibujar_boton("Seleccionar Arma", 300, 400, 400, 60, AZUL, BLANCO, lambda: usar_intento("arma"))
        if investigado:
            deduccion[seccion] = seleccionado
            investigado = False
        # Mostrar deducción actual en la parte inferior
        y_base = 500  # posición vertical inicial para los textos
        # Crear un rectángulo negro semi-transparente detrás de la deducción
        rect_ancho = 500
        rect_alto = 140
        rect_x = ANCHO // 2 - rect_ancho // 2
        rect_y = 490  # Un poco antes de y_base

        # Superficie con canal alfa
        fondo_transparente = pygame.Surface((rect_ancho, rect_alto), pygame.SRCALPHA)
        fondo_transparente.fill((0, 0, 0, 180))  # Negro con alfa (180 = semi-transparente)

        # Dibujar el rectángulo en la pantalla
        ventana.blit(fondo_transparente, (rect_x, rect_y))

        # Mostrar deducción actual en la parte inferior
        y_base = 500
        for i, (clave, valor) in enumerate(deduccion.items()):
            texto = f"{clave.capitalize()}: {valor if valor else 'No seleccionado'}"
            render_texto = fuente_boton.render(texto, True, BLANCO)
            ventana.blit(render_texto, (ANCHO // 2 - render_texto.get_width() // 2, y_base + i * 30))

        if deduccion["sospechoso"]!= None and deduccion["arma"]!= None and deduccion["locacion"]!= None:  
            dibujar_boton("Comprobar", 300, 640, 400, 60, VERDE, BLANCO, mostrar_resultado_final)
        
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                salir()
        pygame.display.update()

def mostrar_resultado_final():
    global deduccion, resultado, caso
    corriendo = True
    resultado = []
    mostrar_historia = False
    tiempo_inicio_historia = None
    texto_mostrado = ""

    # Comparar deducción con el caso
    for clave in ["sospechoso", "locacion", "arma"]:
        if deduccion[clave] and deduccion[clave].lower() == caso[clave].lower():
            resultado.append(f"✅ Acertaste en: {clave.capitalize()}")
        else:
            resultado.append(f"❌ Te equivocaste en: {clave.capitalize()}")

    def cambiar_estado():
        nonlocal mostrar_historia, tiempo_inicio_historia, texto_mostrado
        mostrar_historia = not mostrar_historia
        if mostrar_historia:
            tiempo_inicio_historia = pygame.time.get_ticks()
            texto_mostrado = ""  # Reiniciar animación de escritura

    while corriendo:
        if mostrar_historia:
            ventana.fill((0, 0, 0))  # Fondo negro

            # Título
            titulo = fuente_titulo.render("Historia del caso", True, DORADO)
            ventana.blit(titulo, (ANCHO // 2 - titulo.get_width() // 2, 40))

            # Obtener historia y dividir en líneas ajustadas al ancho
            historia_completa = caso.get("historia", "No hay historia disponible.")
            palabras = historia_completa.split(" ")
            lineas = []
            linea_actual = ""

            for palabra in palabras:
                if fuente_boton.size(linea_actual + palabra)[0] < ANCHO - 100:
                    linea_actual += palabra + " "
                else:
                    lineas.append(linea_actual.strip())
                    linea_actual = palabra + " "
            if linea_actual:
                lineas.append(linea_actual.strip())

            # Efecto de máquina de escribir
            tiempo_actual = pygame.time.get_ticks()
            caracteres_mostrados = (tiempo_actual - tiempo_inicio_historia) // 20  # velocidad de escritura
            historia_parcial = ""
            total_chars = 0

            for linea in lineas:
                if caracteres_mostrados >= total_chars + len(linea):
                    historia_parcial += linea + "\n"
                else:
                    historia_parcial += linea[:max(0, caracteres_mostrados - total_chars)]
                    break
                total_chars += len(linea) + 1  # +1 por el espacio o salto de línea

            # Mostrar texto tipo consola
            y = 120
            for linea in historia_parcial.split("\n"):
                texto = fuente_boton.render(linea, True, BLANCO)
                ventana.blit(texto, (60, y))
                y += 30

            # Botón para volver
            dibujar_boton("Ver resultados", 300, 640, 400, 60, DORADO, BLANCO, cambiar_estado)

        else:
            ventana.blit(fondo, (0, 0))

            # Fondo semitransparente para el texto
            ancho_fondo = ANCHO - 100
            alto_fondo = 550
            superficie_fondo = pygame.Surface((ancho_fondo, alto_fondo), pygame.SRCALPHA)
            superficie_fondo.fill((0, 0, 0, 180))  # Negro con alpha 180 (de 255)
            ventana.blit(superficie_fondo, (50,40))

            # Título
            titulo = fuente_titulo.render("Resultado de tu deducción", True, DORADO)
            ventana.blit(titulo, (ANCHO // 2 - titulo.get_width() // 2, 40))

            y = 120
            deduccion_titulo = fuente_boton.render("Tu deducción:", True, BLANCO)
            ventana.blit(deduccion_titulo, (ANCHO // 2 - deduccion_titulo.get_width() // 2, y))

            y += 40
            for key, value in deduccion.items():
                texto = fuente_boton.render(f"{key.capitalize()}: {value}", True, BLANCO)
                ventana.blit(texto, (ANCHO // 2 - texto.get_width() // 2, y))
                y += 30

            y += 20
            for linea in resultado:
                color = ROJO if "❌" in linea else VERDE
                resultado_texto = fuente_boton.render(linea, True, color)
                ventana.blit(resultado_texto, (ANCHO // 2 - resultado_texto.get_width() // 2, y))
                y += 30

            y += 30
            caso_titulo = fuente_boton.render("El caso verdadero era:", True, DORADO)
            ventana.blit(caso_titulo, (ANCHO // 2 - caso_titulo.get_width() // 2, y))
            y += 40
            for clave in ["sospechoso", "locacion", "arma"]:
                valor_real = fuente_boton.render(f"{clave.capitalize()}: {caso[clave]}", True, BLANCO)
                ventana.blit(valor_real, (ANCHO // 2 - valor_real.get_width() // 2, y))
                y += 30

            # Botones
            dibujar_boton("Menu", 150, 640, 250, 60, DORADO, BLANCO, lambda: reiniciar())
            dibujar_boton("Ver historia", 500, 640, 250, 60, DORADO, BLANCO, cambiar_estado)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                salir()

        pygame.display.update()

def reiniciar():
    global deduciendo, investigacion, caso, seleccionado, seccion, deduccion, resultado, intentos_restantes, mensaje_temporal, temporizador_mensaje
    deduciendo = False
    investigacion = False
    caso = ""
    seleccionado = ""
    seccion = ""
    deduccion = {"sospechoso": None, "locacion": None, "arma": None}
    resultado = []
    intentos_restantes = 5  # Intentos disponibles para investigar
    mensaje_temporal = ""
    temporizador_mensaje = 0
    menu_principal()
# Pantalla principal
def menu_principal():
    global investigacion
    ANCHO_BOTON = 300
    ALTO_BOTON = 60
    ESPACIO = 20
    botones = [
        ("Ver Reglas", ver_reglas),
        ("Sospechosos", mostrar_personajes),
        ("Locaciones", mostrar_locaciones),
        ("Armas", mostrar_armas),
        ("Jugar", introduccion_caso),  # Aquí luego va la función del juego
        ("Salir", salir)
    ]
    investigacion = False
    y_inicial = 180
    corriendo = True
    while corriendo:
        ventana.blit(fondo, (0, 0))
        # Cargar el logo del juego
        logo = pygame.image.load("imagenes/fondo/letrero.png")
        logo = pygame.transform.scale(logo, (500, 150))  # Ajusta el tamaño según tu imagen
        ventana.blit(logo, (ANCHO // 2 - logo.get_width() // 1, 10))  # Posición centrada


        for i, (texto, accion) in enumerate(botones):
            x = ANCHO // 2 - ANCHO_BOTON // 2
            y = y_inicial + i * (ALTO_BOTON + ESPACIO)
            dibujar_boton(texto, x, y, ANCHO_BOTON, ALTO_BOTON, AZUL if texto != "Salir" and texto != "Jugar" else (ROJO if texto == "Jugar" else GRIS), BLANCO, accion)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                salir()

        pygame.display.update()

# Iniciar juego
menu_principal()

