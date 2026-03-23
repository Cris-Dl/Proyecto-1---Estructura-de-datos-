import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QGridLayout, QFrame)
from PyQt6.QtCore import Qt
import json
import os
import requests

class Creador:
    def __init__(self, nombre_completo, imagen):
        self.nombre_completo = nombre_completo
        self.imagen = imagen

    def mostrar_creador(self):
        return {"nombre": self.nombre_completo, "imagen": self.imagen}

class Evento:
    def __init__(self, nombre, descripcion):
        self.nombre = nombre
        self.descripcion = descripcion

    def mostrar_evento(self):
        return {"nombre": self.nombre, "descripcion": self.descripcion}

class Personaje:
    def __init__(self, nombre, imagen_referencia, descripcion=""):
        self.nombre = nombre
        self.imagen_referencia = imagen_referencia
        self.descripcion = descripcion
        self.creadores = []
        self.comics = []
        self.eventos = []

    def mostrar_personaje(self):
        return {"nombre": self.nombre, "imagen_referencia": self.imagen_referencia, "descripcion": self.descripcion, "creadores": self.creadores, "comics": self.comics, "eventos": self.eventos}

class Comic:
    def __init__(self, titulo, isbn, fecha_lanzamiento, imagen_referencia, descripcion=""):
        self.titulo = titulo
        self.isbn = isbn
        self.fecha_lanzamiento = fecha_lanzamiento
        self.imagen_referencia = imagen_referencia
        self.descripcion = descripcion
        self.personajes = []
        self.creadores = []

    def mostrar_info(self):
        return {"titulo": self.titulo, "isbn": self.isbn, "fecha_lanzamiento": self.fecha_lanzamiento, "imagen_referencia": self.imagen_referencia, "descripcion": self.descripcion, "personajes": self.personajes, "creadores": self.creadores}

class NodoPagina:
    def __init__(self, datos):
        self.datos = datos
        self.siguiente = None
        self.anterior = None

class ListaCircularDoblementeEnlazada:
    def __init__(self):
        self.cabeza = None
        self.cola = None

    def lista_vacia(self):
        return self.cabeza is None

    def agregar_pagina(self, datos):
        nuevo_nodo = NodoPagina(datos)
        if self.lista_vacia():
            self.cabeza = nuevo_nodo
            self.cola = nuevo_nodo
            self.cabeza.siguiente = self.cabeza
            self.cabeza.anterior = self.cabeza
        else:
            nuevo_nodo.anterior = self.cola
            nuevo_nodo.siguiente = self.cabeza
            self.cola.siguiente = nuevo_nodo
            self.cabeza.anterior = nuevo_nodo
            self.cola = nuevo_nodo

    def recorrer_adelante(self, nodo_actual):
        if nodo_actual and nodo_actual.siguiente:
            return nodo_actual.siguiente
        return None

    def recorrer_atras(self, nodo_actual):
        if nodo_actual and nodo_actual.anterior:
            return nodo_actual.anterior
        return None

class GestorArchivos:
    @staticmethod
    def guardar_en_json(nombre_archivo, lista_diccionarios):
        with open(nombre_archivo, 'w', encoding='utf-8') as archivo:
            json.dump(lista_diccionarios, archivo, indent=4, ensure_ascii=False)
        print(f"Datos guardados exitosamente en {nombre_archivo}")

    @staticmethod
    def leer_de_json(nombre_archivo):
        if not os.path.exists(nombre_archivo):
            print(f"El archivo {nombre_archivo} no existe. Retornando lista vacía.")
            return []
        with open(nombre_archivo, 'r', encoding='utf-8') as archivo:
            return json.load(archivo)

class Paginador:
    @staticmethod
    def construir_lista_paginada(datos_completos, tamano_pagina=10):
        lista_circular = ListaCircularDoblementeEnlazada()
        if not datos_completos:
            return lista_circular
        for i in range(0, len(datos_completos), tamano_pagina):
            pagina = datos_completos[i: i + tamano_pagina]
            lista_circular.agregar_pagina(pagina)
        return lista_circular

class ClienteComicVineAPI:
    def __init__(self, api_key):
        self.base_url = "https://comicvine.gamespot.com/api"
        self.api_key = api_key
        self.headers = {"User-Agent": "MundoComicApp_ProyectoUniversitario/1.0"}

    def obtener_comics(self, limite=50):
        url = f"{self.base_url}/issues/"
        parametros = {"api_key": self.api_key, "format": "json", "limit": limite, "sort": "cover_date:desc"}
        print("Conectando con Comic Vine API para obtener cómics...")
        respuesta = requests.get(url, headers=self.headers, params=parametros)
        if respuesta.status_code == 200:
            return respuesta.json().get("results", [])
        else:
            print(f"Error al conectar: {respuesta.status_code}")
            return []

#Inicio de la interfaz gráfica
class VentanaCatalogo(QMainWindow):
    def __init__(self, lista_paginada):
        super().__init__()
        self.lista_paginada = lista_paginada
        self.pagina_actual = self.lista_paginada.cabeza
        self.inicializar_gui()

    def inicializar_gui(self):
        self.setWindowTitle("Mundo Comic - Catálogo Virtual")
        self.setMinimumSize(800, 600)
        widget_central = QWidget()
        self.setCentralWidget(widget_central)
        layout_principal = QVBoxLayout(widget_central)

        #Título
        titulo = QLabel("Listado de Cómics de Marvel")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titulo.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px;")
        layout_principal.addWidget(titulo)

        #Área de Cómics
        self.grid_comics = QGridLayout()
        layout_principal.addLayout(self.grid_comics)

        #Botones de Navegación
        layout_botones = QHBoxLayout()
        self.btn_atras = QPushButton("<< Anterior")
        self.btn_siguiente = QPushButton("Siguiente >>")
        self.btn_atras.clicked.connect(self.ir_atras)
        self.btn_siguiente.clicked.connect(self.ir_siguiente)
        layout_botones.addWidget(self.btn_atras)
        layout_botones.addStretch()
        layout_botones.addWidget(self.btn_siguiente)
        layout_principal.addLayout(layout_botones)
        self.actualizar_vista()

    def actualizar_vista(self):
        for i in reversed(range(self.grid_comics.count())):
            widget = self.grid_comics.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        if not self.pagina_actual:
            self.grid_comics.addWidget(QLabel("No hay cómics disponibles."))
            return
        comics = self.pagina_actual.datos
        fila, columna = 0, 0
        for comic in comics:
            tarjeta = QFrame()
            tarjeta.setStyleSheet("background-color: #f8f9fa; border: 1px solid #dee2e6; border-radius: 5px;")
            layout_tarjeta = QVBoxLayout(tarjeta)

            # Mostrar datos del cómic
            lbl_titulo = QLabel(f"<b>{comic.titulo}</b>")  # Nombre del comic
            lbl_fecha = QLabel(f"Lanzamiento: {comic.fecha_lanzamiento}")  # Fecha de lanzamiento
            btn_detalle = QPushButton("Ver Detalle")  # Botón de detalle
            layout_tarjeta.addWidget(lbl_titulo)
            layout_tarjeta.addWidget(lbl_fecha)
            layout_tarjeta.addWidget(btn_detalle)
            self.grid_comics.addWidget(tarjeta, fila, columna)
            columna += 1
            if columna > 1:
                columna = 0
                fila += 1

    def ir_siguiente(self):
        if self.pagina_actual:
            self.pagina_actual = self.lista_paginada.recorrer_adelante(self.pagina_actual)
            self.actualizar_vista()

    def ir_atras(self):
        if self.pagina_actual:
            self.pagina_actual = self.lista_paginada.recorrer_atras(self.pagina_actual)
            self.actualizar_vista()


if __name__ == "__main__":
    API_KEY = "aca41dd517e3946fa374082173c07f73050d497b"
    ARCHIVO_LOCAL = "comics_oficiales.json"
    if not os.path.exists(ARCHIVO_LOCAL):
        print("Es la primera vez que se ejecuta. ¡Descargando datos reales!")
        cliente_api = ClienteComicVineAPI(API_KEY)
        datos_crudos = cliente_api.obtener_comics(limite=50)
        lista_objetos_comics = []
        for item in datos_crudos:
            titulo = item.get("name")
            if not titulo:
                volumen = item.get("volume", {}).get("name", "Desconocido")
                numero = item.get("issue_number", "0")
                titulo = f"{volumen} #{numero}"
            fecha = item.get("cover_date", "Sin fecha")
            descripcion = item.get("description", "Sin descripción")
            imagen = item.get("image", {}).get("original_url", "")
            nuevo_comic = Comic(titulo, "N/A", fecha, imagen, descripcion)
            lista_objetos_comics.append(nuevo_comic)
        lista_diccionarios = [comic.mostrar_info() for comic in lista_objetos_comics]
        GestorArchivos.guardar_en_json(ARCHIVO_LOCAL, lista_diccionarios)
    datos_json = GestorArchivos.leer_de_json(ARCHIVO_LOCAL)
    comics_reales = []
    for dato in datos_json:
        nuevo_comic = Comic(titulo=dato["titulo"], isbn=dato["isbn"], fecha_lanzamiento=dato["fecha_lanzamiento"], imagen_referencia=dato["imagen_referencia"], descripcion=dato["descripcion"])
        comics_reales.append(nuevo_comic)
    catalogo_paginado = Paginador.construir_lista_paginada(comics_reales, 10)
    app = QApplication(sys.argv)
    ventana = VentanaCatalogo(catalogo_paginado)
    ventana.show()
    sys.exit(app.exec())