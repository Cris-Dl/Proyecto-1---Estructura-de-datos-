import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QGridLayout, QFrame, QDialog, QTextBrowser, QLineEdit, QComboBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
import json
import os
import requests
import time

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

    def obtener_comics(self, limite_por_heroe=10):
        url_search = f"{self.base_url}/search/"
        heroes_marvel = ["Spider-Man", "Iron Man", "Thor", "Hulk", "X-Men"]
        ids_encontrados = []
        print("Paso 1: Recolectando cómics de varios héroes de Marvel...")
        for heroe in heroes_marvel:
            parametros_search = {"api_key": self.api_key, "format": "json", "limit": limite_por_heroe, "resources": "issue", "query": heroe}
            respuesta_search = requests.get(url_search, headers=self.headers, params=parametros_search)
            if respuesta_search.status_code == 200:
                resultados = respuesta_search.json().get("results", [])
                for comic in resultados:
                    ids_encontrados.append(str(comic["id"]))
            time.sleep(1)
        ids_finales = ids_encontrados[:50]
        filtro_ids = "|".join(ids_finales)
        url_issues = f"{self.base_url}/issues/"
        parametros_issues = {"api_key": self.api_key, "format": "json", "filter": f"id:{filtro_ids}"}
        print("Paso 2: Descargando la información completa del multiverso...")
        respuesta_issues = requests.get(url_issues, headers=self.headers, params=parametros_issues)
        if respuesta_issues.status_code == 200:
            return respuesta_issues.json().get("results", [])
        else:
            print(f"Error al obtener detalles: {respuesta_issues.status_code}")
            return []

#Inicio de la interfaz gráfica
class VentanaCatalogo(QMainWindow):
    def __init__(self, comics_totales):
        super().__init__()
        self.comics_totales = comics_totales
        self.lista_paginada = Paginador.construir_lista_paginada(self.comics_totales, 10)
        self.pagina_actual = self.lista_paginada.cabeza
        self.inicializar_gui()

    def aplicar_filtros(self):
        texto_busqueda = self.input_busqueda.text().lower()
        anio_busqueda = self.input_anio.text()
        orden = self.combo_orden.currentText()
        comics_filtrados = []
        for comic in self.comics_totales:
            coincide_nombre = texto_busqueda in comic.titulo.lower()
            coincide_anio = anio_busqueda in comic.fecha_lanzamiento if anio_busqueda else True
            if coincide_nombre and coincide_anio:
                comics_filtrados.append(comic)
        if orden == "Nombre (A-Z)":
            comics_filtrados.sort(key=lambda x: x.titulo)
        elif orden == "Nombre (Z-A)":
            comics_filtrados.sort(key=lambda x: x.titulo, reverse=True)
        elif orden == "Más recientes":
            comics_filtrados.sort(key=lambda x: x.fecha_lanzamiento, reverse=True)
        elif orden == "Más antiguos":
            comics_filtrados.sort(key=lambda x: x.fecha_lanzamiento)
        self.lista_paginada = Paginador.construir_lista_paginada(comics_filtrados, 10)
        self.pagina_actual = self.lista_paginada.cabeza
        self.actualizar_vista()

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
        layout_filtros = QHBoxLayout()
        self.input_busqueda = QLineEdit()
        self.input_busqueda.setPlaceholderText("Buscar por título...")
        self.input_anio = QLineEdit()
        self.input_anio.setPlaceholderText("Año (ej. 2024)")
        self.input_anio.setFixedWidth(100)
        self.combo_orden = QComboBox()
        self.combo_orden.addItems(["Ordenar por...","Nombre (A-Z)","Nombre (Z-A)","Más recientes","Más antiguos"])
        btn_filtrar = QPushButton("Aplicar Filtros")
        btn_filtrar.setStyleSheet("background-color: #2b2b2b; color: white; padding: 5px;")
        btn_filtrar.clicked.connect(self.aplicar_filtros)

        # Agregamos los elementos a la barrita horizontal
        layout_filtros.addWidget(self.input_busqueda)
        layout_filtros.addWidget(self.input_anio)
        layout_filtros.addWidget(self.combo_orden)
        layout_filtros.addWidget(btn_filtrar)
        layout_principal.addLayout(layout_filtros)

        #Área de Cómics
        self.grid_comics = QGridLayout()
        self.grid_comics.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout_principal.addLayout(self.grid_comics)
        layout_principal.addStretch()

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
        while self.grid_comics.count():
            item = self.grid_comics.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        if not self.pagina_actual:
            lbl_vacio = QLabel("No se encontraron cómics con esos filtros.")
            self.grid_comics.addWidget(lbl_vacio, 0, 0, alignment=Qt.AlignmentFlag.AlignCenter)
            return
        comics = self.pagina_actual.datos
        fila, columna = 0, 0
        for comic in comics:
            tarjeta = QFrame()
            tarjeta.setObjectName("tarjeta_comic")
            tarjeta.setStyleSheet("#tarjeta_comic { background-color: #f8f9fa; border: 1px solid #dee2e6; border-radius: 8px; }")
            layout_tarjeta = QHBoxLayout(tarjeta)
            layout_tarjeta.setContentsMargins(10, 10, 10, 10)
            lbl_imagen = QLabel()
            lbl_imagen.setFixedSize(80, 120)
            lbl_imagen.setScaledContents(True)
            if comic.imagen_referencia and comic.imagen_referencia != "N/A":
                try:
                    respuesta_img = requests.get(comic.imagen_referencia, timeout=5)
                    if respuesta_img.status_code == 200:
                        pixmap = QPixmap()
                        pixmap.loadFromData(respuesta_img.content)
                        lbl_imagen.setPixmap(pixmap)
                    else:
                        lbl_imagen.setText("Sin\nImagen")
                except:
                    lbl_imagen.setText("Error")
            else:
                lbl_imagen.setText("N/A")
            layout_info = QVBoxLayout()
            lbl_titulo = QLabel(f"<b>{comic.titulo}</b>")
            lbl_titulo.setWordWrap(True)
            lbl_fecha = QLabel(f"Lanzamiento: {comic.fecha_lanzamiento}")
            lbl_fecha.setStyleSheet("color: #555; font-size: 11px;")
            btn_detalle = QPushButton("Ver Detalle")
            btn_detalle.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_detalle.setStyleSheet("background-color: #E23636; color: white; border-radius: 4px; padding: 5px;")
            btn_detalle.clicked.connect(lambda checked, c=comic: self.mostrar_detalle(c))
            layout_info.addWidget(lbl_titulo)
            layout_info.addWidget(lbl_fecha)
            layout_info.addWidget(btn_detalle)
            layout_info.addStretch()
            layout_tarjeta.addWidget(lbl_imagen)
            layout_tarjeta.addLayout(layout_info)
            self.grid_comics.addWidget(tarjeta, fila, columna, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
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

    def mostrar_detalle(self, comic):
        dialogo = QDialog(self)
        dialogo.setWindowTitle(f"Detalle: {comic.titulo}")
        dialogo.setMinimumSize(400, 500)
        dialogo.setStyleSheet("background-color: white;")
        layout = QVBoxLayout(dialogo)
        lbl_titulo = QLabel(f"<h2 style='color: #E23636;'>{comic.titulo}</h2>")
        lbl_titulo.setWordWrap(True)
        layout.addWidget(lbl_titulo)
        lbl_isbn = QLabel(f"<b>ISBN:</b> {comic.isbn}")
        layout.addWidget(lbl_isbn)
        layout.addWidget(QLabel("<b>Descripción:</b>"))
        txt_desc = QTextBrowser()
        descripcion_texto = comic.descripcion if comic.descripcion else "Sin descripción disponible para este número."
        txt_desc.setHtml(descripcion_texto)
        layout.addWidget(txt_desc)
        layout.addWidget(QLabel("<br><b>Personajes que aparecen:</b>"))
        nombres_personajes = [p["nombre"] for p in comic.personajes] if comic.personajes else []
        texto_personajes = ", ".join(nombres_personajes) if nombres_personajes else "No especificados en la base de datos."
        lbl_personajes = QLabel(texto_personajes)
        lbl_personajes.setWordWrap(True)
        lbl_personajes.setStyleSheet("color: #444; font-size: 11px;")
        layout.addWidget(lbl_personajes)
        layout.addWidget(QLabel("<b>Creadores:</b>"))
        nombres_creadores = [c["nombre"] for c in comic.creadores] if comic.creadores else []
        texto_creadores = ", ".join(nombres_creadores) if nombres_creadores else "No especificados."
        lbl_creadores = QLabel(texto_creadores)
        lbl_creadores.setWordWrap(True)
        lbl_creadores.setStyleSheet("color: #444; font-size: 11px;")
        layout.addWidget(lbl_creadores)
        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.setStyleSheet("background-color: #333; color: white; padding: 5px;")
        btn_cerrar.clicked.connect(dialogo.accept)
        layout.addWidget(btn_cerrar)
        dialogo.exec()

if __name__ == "__main__":
    API_KEY = "aca41dd517e3946fa374082173c07f73050d497b"
    ARCHIVO_LOCAL = "comics_oficiales.json"
    if not os.path.exists(ARCHIVO_LOCAL):
        print("Es la primera vez que se ejecuta. ¡Descargando datos reales!")
        cliente_api = ClienteComicVineAPI(API_KEY)
        datos_crudos = cliente_api.obtener_comics()
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
            if "character_credits" in item:
                for char in item["character_credits"]:
                    nuevo_comic.personajes.append({"nombre": char.get("name"), "imagen": "N/A"})
            if "person_credits" in item:
                for creador in item["person_credits"]:
                    nuevo_comic.creadores.append({"nombre": creador.get("name"), "imagen": "N/A"})
            lista_objetos_comics.append(nuevo_comic)
        lista_diccionarios = [comic.mostrar_info() for comic in lista_objetos_comics]
        GestorArchivos.guardar_en_json(ARCHIVO_LOCAL, lista_diccionarios)
    datos_json = GestorArchivos.leer_de_json(ARCHIVO_LOCAL)
    comics_reales = []
    for dato in datos_json:
        nuevo_comic = Comic(titulo=dato["titulo"], isbn=dato["isbn"], fecha_lanzamiento=dato["fecha_lanzamiento"], imagen_referencia=dato["imagen_referencia"], descripcion=dato["descripcion"])
        nuevo_comic.personajes = dato.get("personajes", [])
        nuevo_comic.creadores = dato.get("creadores", [])
        comics_reales.append(nuevo_comic)
    catalogo_paginado = Paginador.construir_lista_paginada(comics_reales, 10)
    app = QApplication(sys.argv)
    ventana = VentanaCatalogo(comics_reales)
    ventana.show()
    sys.exit(app.exec())