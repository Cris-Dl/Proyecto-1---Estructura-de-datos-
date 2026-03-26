import sys
import threading
import os
import json
import time
import requests
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QGridLayout, QFrame, QDialog, QTextBrowser, QLineEdit, QComboBox, QScrollArea, QGraphicsDropShadowEffect, QSizePolicy
from PyQt6.QtCore import Qt, pyqtSignal, QThread
from PyQt6.QtGui import QPixmap, QImage, QColor, QPainter, QLinearGradient, QBrush

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

class Personaje:
    def __init__(self, nombre, imagen_referencia="", descripcion=""):
        self.nombre = nombre
        self.imagen_referencia = imagen_referencia
        self.descripcion = descripcion
        self.creadores = []
        self.comics = []
        self.eventos = []

    def mostrar_info(self):
        return {"nombre": self.nombre, "imagen_referencia": self.imagen_referencia, "descripcion": self.descripcion, "creadores": self.creadores, "comics": self.comics, "eventos": self.eventos}

class NodoPersonaje:
    def __init__(self, personaje):
        self.personaje = personaje
        self.siguiente = None

class ListaSimplementeLigadaPersonajes:
    def __init__(self):
        self.cabeza = None
        self.total = 0

    def agregar(self, personaje):
        nuevo = NodoPersonaje(personaje)
        if not self.cabeza:
            self.cabeza = nuevo
        else:
            actual = self.cabeza
            while actual.siguiente:
                actual = actual.siguiente
            actual.siguiente = nuevo
        self.total += 1

    def lista(self):
        resultado = []
        actual = self.cabeza
        while actual:
            resultado.append(actual.personaje)
            actual = actual.siguiente
        return resultado

class NodoPagina:
    def __init__(self, comics, numero_pagina):
        self.comics = comics
        self.numero_pagina = numero_pagina
        self.siguiente = None
        self.anterior = None

class ListaCircularDoblementeEnlazada:
    def __init__(self):
        self.cabeza = None
        self.cola = None
        self.total_paginas = 0

    def agregar_pagina(self, comics):
        self.total_paginas += 1
        nuevo_nodo = NodoPagina(comics, self.total_paginas)
        if not self.cabeza:
            self.cabeza = nuevo_nodo
            self.cola = nuevo_nodo
            nuevo_nodo.siguiente = nuevo_nodo
            nuevo_nodo.anterior = nuevo_nodo
        else:
            nuevo_nodo.anterior = self.cola
            nuevo_nodo.siguiente = self.cabeza
            self.cola.siguiente = nuevo_nodo
            self.cabeza.anterior = nuevo_nodo
            self.cola = nuevo_nodo

class GestorArchivos:
    @staticmethod
    def guardar_en_json(nombre_archivo, lista_diccionarios):
        with open(nombre_archivo, 'w', encoding='utf-8') as archivo:
            json.dump(lista_diccionarios, archivo, indent=4, ensure_ascii=False)

    @staticmethod
    def leer_de_json(nombre_archivo):
        if not os.path.exists(nombre_archivo):
            return []
        with open(nombre_archivo, 'r', encoding='utf-8') as archivo:
            return json.load(archivo)

class ClienteComicVineAPI:
    VOLUMENES_MARVEL = ["2127", "2407", "2294", "6211", "87182", "86113", ]

    def __init__(self, clave_api):
        self.clave_api = clave_api
        self.encabezados = {"User-Agent": "MundoComicApp/4.0"}
        self.sesion = requests.Session()
        self.sesion.headers.update(self.encabezados)

    def obtener_urls_de_volumen(self, id_volumen, limite=10):
        url = "https://comicvine.gamespot.com/api/issues/"
        parametros = {"api_key": self.clave_api, "format": "json", "filter": f"volume:{id_volumen}", "limit": limite,
                      "sort": "issue_number:asc"}
        for intento in range(3):
            try:
                respuesta = self.sesion.get(url, params=parametros, timeout=15)
                if respuesta.status_code == 200:
                    datos = respuesta.json()
                    if datos.get("status_code") == 1:
                        return [issue["api_detail_url"] for issue in datos.get("results", [])]
                elif respuesta.status_code == 429:
                    time.sleep(2)
            except Exception:
                pass
            time.sleep(1)
        return []

    def obtener_detalle_issue(self, url_issue):
        parametros = {"api_key": self.clave_api, "format": "json"}

        for intento in range(3):
            try:
                respuesta = self.sesion.get(url_issue, params=parametros, timeout=15)
                if respuesta.status_code == 200:
                    datos = respuesta.json()
                    if datos.get("status_code") == 1:
                        return datos.get("results")
                elif respuesta.status_code == 429:
                    time.sleep(2)
            except Exception:
                pass
            time.sleep(1)
        return None

    def obtener_comics(self):
        print("Paso 1: Buscando colecciones Marvel verificadas...")
        urls_issues = []

        for id_vol in self.VOLUMENES_MARVEL:
            urls = self.obtener_urls_de_volumen(id_vol, limite=10)
            urls_issues.extend(urls)
            time.sleep(1)

        total_encontrados = len(urls_issues)
        print(f"\nPaso 2: Se aseguraron {total_encontrados} cómics 100% Marvel.")
        print("Descargando personajes y creadores de forma segura...")
        resultados = []
        for i, url in enumerate(urls_issues, 1):
            detalle = self.obtener_detalle_issue(url)
            if detalle:
                resultados.append(detalle)
            print(f"  {i}/{total_encontrados} descargados...", end="\r")
            time.sleep(1.2)
        print(f"\n\n¡Listo! {len(resultados)} cómics obtenidos con éxito.")
        return resultados


PALETA = {"fondo": "#0d0d0d", "superficie": "#141414", "tarjeta": "#1a1a1a", "tarjeta_hover": "#222222","borde": "#2a2a2a", "acento": "#e23636", "acento2": "#ff6b35", "dorado": "#f5c518", "texto_alto": "#f0f0f0", "texto_medio": "#a0a0a0", "texto_bajo": "#555555"}
ESTILO_PRINCIPAL = f"""QMainWindow, QWidget#raiz {{background-color: {PALETA['fondo']};}}
    QWidget {{color: {PALETA['texto_alto']};font-family: 'Segoe UI', sans-serif;}}
    QScrollArea {{border: none;background: transparent;}}
    QScrollBar:vertical {{background: {PALETA['superficie']};width: 6px;border-radius: 3px;}}
    QScrollBar::handle:vertical {{background: {PALETA['acento']};border-radius: 3px;min-height: 30px;}}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{height: 0px;}}
    QLineEdit {{background: {PALETA['superficie']};border: 1px solid {PALETA['borde']};border-radius: 6px;padding: 9px 14px;color: {PALETA['texto_alto']};font-size: 13px;selection-background-color: {PALETA['acento']};}}
    QLineEdit:focus {{border: 1px solid {PALETA['acento']};}}
    QComboBox {{background: {PALETA['superficie']};border: 1px solid {PALETA['borde']};border-radius: 6px;padding: 9px 14px;color: {PALETA['texto_alto']};font-size: 13px;min-width: 160px;}}
    QComboBox:focus {{border: 1px solid {PALETA['acento']};}}
    QComboBox::drop-down {{border: none;width: 30px;}}
    QComboBox::down-arrow {{image: none;border-left: 5px solid transparent;border-right: 5px solid transparent;border-top: 6px solid {PALETA['acento']};width: 0; height: 0;margin-right: 10px;}}
    QComboBox QAbstractItemView {{background: {PALETA['superficie']};border: 1px solid {PALETA['borde']};selection-background-color: {PALETA['acento']};color: {PALETA['texto_alto']};outline: none;}}
    QDialog {{background: {PALETA['fondo']};}}
    QTextBrowser {{background: transparent;border: none;color: {PALETA['texto_medio']};font-size: 13px;}}"""

class DivisorRojo(QWidget):
    def __init__(self, altura=1, parent=None):
        super().__init__(parent)
        self.setFixedHeight(altura)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

    def pintar(self, evento):
        pintor = QPainter(self)
        pintor.setRenderHint(QPainter.RenderHint.Antialiasing)
        degradado = QLinearGradient(0, 0, self.width(), 0)
        degradado.setColorAt(0.0, QColor(0, 0, 0, 0))
        degradado.setColorAt(0.2, QColor(PALETA['acento']))
        degradado.setColorAt(0.8, QColor(PALETA['acento']))
        degradado.setColorAt(1.0, QColor(0, 0, 0, 0))
        pintor.fillRect(self.rect(), QBrush(degradado))

class TarjetaComic(QFrame):
    senal_detalle = pyqtSignal(object)

    def __init__(self, comic, parent=None):
        super().__init__(parent)
        self.comic = comic
        self.setFixedSize(420, 210)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.construir_ui()
        self.aplicar_sombra()
        self.estilo_normal()

    def aplicar_sombra(self):
        sombra = QGraphicsDropShadowEffect(self)
        sombra.setBlurRadius(20)
        sombra.setOffset(0, 4)
        sombra.setColor(QColor(0, 0, 0, 120))
        self.setGraphicsEffect(sombra)

    def estilo_normal(self):
        self.setStyleSheet(f"""
            QFrame {{background: {PALETA['tarjeta']};border: 1px solid {PALETA['borde']};border-radius: 10px;}}""")

    def estilo_hover(self):
        self.setStyleSheet(f"""
            QFrame {{background: {PALETA['tarjeta_hover']};border: 1px solid {PALETA['acento']};border-radius: 10px;}}""")

    def enterEvent(self, evento):
        self.estilo_hover()
        super().enterEvent(evento)

    def leaveEvent(self, evento):
        self.estilo_normal()
        super().leaveEvent(evento)

    def mousePressEvent(self, evento):
        if evento.button() == Qt.MouseButton.LeftButton:
            self.senal_detalle.emit(self.comic)

    def construir_ui(self):
        contenedor = QHBoxLayout(self)
        contenedor.setContentsMargins(14, 14, 18, 14)
        contenedor.setSpacing(16)

        self.lbl_imagen = QLabel()
        self.lbl_imagen.setFixedSize(110, 166)
        self.lbl_imagen.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_imagen.setStyleSheet(
            f"""background: {PALETA['superficie']};border-radius: 6px;color: {PALETA['texto_bajo']};font-size: 20px;""")
        self.lbl_imagen.setText("⏳")
        columna_info = QVBoxLayout()
        columna_info.setSpacing(6)
        lbl_editorial = QLabel("MARVEL COMICS")
        lbl_editorial.setStyleSheet(
            f"""color: {PALETA['acento']};font-size: 10px;font-weight: bold;letter-spacing: 2px;""")
        titulo_recortado = self.comic.titulo[:58] + ("…" if len(self.comic.titulo) > 58 else "")
        lbl_titulo = QLabel(titulo_recortado)
        lbl_titulo.setWordWrap(True)
        lbl_titulo.setStyleSheet(f"""color: {PALETA['texto_alto']};font-size: 15px;font-weight: bold;""")
        fila_fecha = QHBoxLayout()
        lbl_rombo = QLabel("◆")
        lbl_rombo.setStyleSheet(f"color: {PALETA['dorado']}; font-size: 8px;")
        lbl_rombo.setFixedWidth(14)
        lbl_fecha_val = QLabel(self.comic.fecha_lanzamiento or "Fecha desconocida")
        lbl_fecha_val.setStyleSheet(f"color: {PALETA['texto_medio']}; font-size: 12px;")
        fila_fecha.addWidget(lbl_rombo)
        fila_fecha.addWidget(lbl_fecha_val)
        fila_fecha.addStretch()
        cantidad_personajes = len(self.comic.personajes)
        lbl_personajes = QLabel(f"👥  {cantidad_personajes} personaje{'s' if cantidad_personajes != 1 else ''}")
        lbl_personajes.setStyleSheet(f"color: {PALETA['texto_bajo']}; font-size: 11px;")
        btn_detalle = QPushButton("Ver detalle  →")
        btn_detalle.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_detalle.setFixedHeight(32)
        btn_detalle.setStyleSheet(
            f"""QPushButton {{background: transparent;color: {PALETA['acento']};border: 1px solid {PALETA['acento']};border-radius: 6px;font-size: 12px;font-weight: bold;padding: 0 12px;}}
            QPushButton:hover {{background: {PALETA['acento']};color: white;}}""")
        btn_detalle.clicked.connect(lambda: self.senal_detalle.emit(self.comic))
        columna_info.addWidget(lbl_editorial)
        columna_info.addWidget(lbl_titulo)
        columna_info.addLayout(fila_fecha)
        columna_info.addWidget(lbl_personajes)
        columna_info.addStretch()
        columna_info.addWidget(btn_detalle)
        contenedor.addWidget(self.lbl_imagen)
        contenedor.addLayout(columna_info)


class CargadorImagen(QThread):
    carga_completa = pyqtSignal(object, QPixmap)

    def __init__(self, url, id_widget, sesion, ancho=110, alto=166):
        super().__init__()
        self.url = url
        self.id_widget = id_widget
        self.sesion = sesion
        self.ancho = ancho
        self.alto = alto
        self._cancelado = False

    def cancelar(self):
        self._cancelado = True

    def run(self):
        if self._cancelado:
            return
        try:
            respuesta = self.sesion.get(self.url, timeout=6)
            if self._cancelado:
                return
            if respuesta.status_code == 200:
                imagen = QImage()
                imagen.loadFromData(respuesta.content)
                pixmap = QPixmap.fromImage(imagen).scaled(self.ancho, self.alto, Qt.AspectRatioMode.KeepAspectRatio,
                                                          Qt.TransformationMode.SmoothTransformation)
                if not self._cancelado:
                    self.carga_completa.emit(self.id_widget, pixmap)
        except Exception:
            pass


class TarjetaPersonaje(QFrame):
    senal_detalle = pyqtSignal(object)

    def __init__(self, personaje, parent=None):
        super().__init__(parent)
        self.personaje = personaje
        self.setFixedSize(420, 100)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.construir_ui()
        self.aplicar_sombra()
        self.estilo_normal()

    def aplicar_sombra(self):
        sombra = QGraphicsDropShadowEffect(self)
        sombra.setBlurRadius(16)
        sombra.setOffset(0, 3)
        sombra.setColor(QColor(0, 0, 0, 100))
        self.setGraphicsEffect(sombra)

    def estilo_normal(self):
        self.setStyleSheet(f"""
            QFrame {{background: {PALETA['tarjeta']};border: 1px solid {PALETA['borde']};border-radius: 10px;}}""")

    def estilo_hover(self):
        self.setStyleSheet(f"""QFrame {{background: {PALETA['tarjeta_hover']}; border: 1px solid {PALETA['acento']}; border-radius: 10px;}}""")

    def enterEvent(self, e):
        self.estilo_hover()
        super().enterEvent(e)

    def leaveEvent(self, e):
        self.estilo_normal()
        super().leaveEvent(e)

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self.senal_detalle.emit(self.personaje)

    def construir_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 10, 16, 10)
        layout.setSpacing(14)
        self.lbl_imagen = QLabel()
        self.lbl_imagen.setFixedSize(60, 60)
        self.lbl_imagen.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_imagen.setStyleSheet(f"""background: {PALETA['superficie']}; border-radius: 30px; color: {PALETA['texto_bajo']}; font-size: 18px;""")
        self.lbl_imagen.setText("👤")
        col = QVBoxLayout()
        col.setSpacing(4)
        lbl_categoria = QLabel("MARVEL — PERSONAJE")
        lbl_categoria.setStyleSheet(f"color: {PALETA['acento']}; font-size: 9px; font-weight: bold; letter-spacing: 2px;")
        nombre_recortado = self.personaje.nombre[:55] + ("…" if len(self.personaje.nombre) > 55 else "")
        lbl_nombre = QLabel(nombre_recortado)
        lbl_nombre.setStyleSheet(f"color: {PALETA['texto_alto']}; font-size: 14px; font-weight: bold;")
        cant_comics = len(self.personaje.comics)
        lbl_comics = QLabel(f"📖  {cant_comics} comic{'s' if cant_comics != 1 else ''}")
        lbl_comics.setStyleSheet(f"color: {PALETA['texto_bajo']}; font-size: 11px;")
        col.addWidget(lbl_categoria)
        col.addWidget(lbl_nombre)
        col.addWidget(lbl_comics)
        btn = QPushButton("Ver detalle  →")
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setFixedHeight(28)
        btn.setStyleSheet(f"""
            QPushButton {{background: transparent; color: {PALETA['acento']}; border: 1px solid {PALETA['acento']}; border-radius: 6px; font-size: 11px; font-weight: bold; padding: 0 10px;}}
            QPushButton:hover {{background: {PALETA['acento']}; color: white;}}""")
        btn.clicked.connect(lambda: self.senal_detalle.emit(self.personaje))
        layout.addWidget(self.lbl_imagen)
        layout.addLayout(col)
        layout.addStretch()
        layout.addWidget(btn)

class VentanaPersonajes(QWidget):
    def __init__(self, personajes_totales, sesion, cache_imagenes, parent=None):
        super().__init__(parent)
        self.personajes_totales = personajes_totales
        self.personajes_filtrados = list(personajes_totales)
        self.sesion = sesion
        self.cache_imagenes = cache_imagenes
        self.tamano_pagina = 10
        self.lista_paginas = ListaCircularDoblementeEnlazada()
        self.nodo_actual = None
        self.hilos_activos = []
        self.mapa_labels = {}
        self._construir_ui()

    def _construir_ui(self):
        raiz = QVBoxLayout(self)
        raiz.setContentsMargins(0, 0, 0, 0)
        raiz.setSpacing(0)
        raiz.addWidget(self._construir_barra_filtros())
        raiz.addWidget(DivisorRojo(1))
        area_scroll = QScrollArea()
        area_scroll.setWidgetResizable(True)
        area_scroll.setStyleSheet(f"background: {PALETA['fondo']}; border: none;")
        contenido = QWidget()
        contenido.setStyleSheet(f"background: {PALETA['fondo']};")
        diseno_contenido = QVBoxLayout(contenido)
        diseno_contenido.setContentsMargins(28, 24, 28, 24)
        diseno_contenido.setSpacing(16)
        centrado = QWidget()
        centrado.setStyleSheet("background: transparent;")
        diseno_centrado = QHBoxLayout(centrado)
        diseno_centrado.setContentsMargins(0, 0, 0, 0)
        self.widget_grid = QWidget()
        self.widget_grid.setStyleSheet("background: transparent;")
        self.grid_personajes = QGridLayout(self.widget_grid)
        self.grid_personajes.setSpacing(12)
        self.grid_personajes.setAlignment(Qt.AlignmentFlag.AlignTop)
        diseno_centrado.addStretch()
        diseno_centrado.addWidget(self.widget_grid)
        diseno_centrado.addStretch()
        diseno_contenido.addWidget(centrado)
        diseno_contenido.addStretch()
        area_scroll.setWidget(contenido)
        raiz.addWidget(area_scroll, 1)
        raiz.addWidget(DivisorRojo(1))
        raiz.addWidget(self._construir_pie())
        self._al_cambiar_filtro()

    def _construir_barra_filtros(self):
        barra = QWidget()
        barra.setFixedHeight(70)
        barra.setStyleSheet(f"background: {PALETA['superficie']};")
        diseno = QHBoxLayout(barra)
        diseno.setContentsMargins(28, 12, 28, 12)
        diseno.setSpacing(10)
        self.campo_nombre = QLineEdit()
        self.campo_nombre.setPlaceholderText("🔍  Buscar por nombre…")
        self.campo_nombre.setFixedWidth(240)
        self.campo_nombre.textChanged.connect(self._al_cambiar_filtro)
        self.campo_creador = QLineEdit()
        self.campo_creador.setPlaceholderText("✏️  Buscar por creador…")
        self.campo_creador.setFixedWidth(200)
        self.campo_creador.textChanged.connect(self._al_cambiar_filtro)
        sep = QLabel("|")
        sep.setStyleSheet(f"color: {PALETA['borde']}; font-size: 20px;")
        lbl_ord = QLabel("Ordenar:")
        lbl_ord.setStyleSheet(f"color: {PALETA['texto_medio']}; font-size: 12px;")
        self.combo_orden = QComboBox()
        self.combo_orden.addItems(["Nombre  A → Z", "Nombre  Z → A", "Más comics primero"])
        self.combo_orden.currentIndexChanged.connect(self._al_cambiar_filtro)
        btn_limpiar = QPushButton("✕  Limpiar")
        btn_limpiar.setFixedHeight(36)
        btn_limpiar.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_limpiar.setStyleSheet(f"""
            QPushButton {{background: transparent; color: {PALETA['texto_bajo']}; border: 1px solid {PALETA['borde']}; border-radius: 6px; padding: 0 14px;font-size: 12px;}}
            QPushButton:hover {{color: {PALETA['texto_alto']}; border-color: {PALETA['texto_medio']};}}""")
        btn_limpiar.clicked.connect(self._limpiar_filtros)
        diseno.addWidget(self.campo_nombre)
        diseno.addWidget(self.campo_creador)
        diseno.addWidget(sep)
        diseno.addWidget(lbl_ord)
        diseno.addWidget(self.combo_orden)
        diseno.addStretch()
        diseno.addWidget(btn_limpiar)
        return barra

    def _construir_pie(self):
        pie = QWidget()
        pie.setFixedHeight(64)
        pie.setStyleSheet(f"background: {PALETA['superficie']};")
        diseno = QHBoxLayout(pie)
        diseno.setContentsMargins(28, 0, 28, 0)
        self.lbl_resultados = QLabel("")
        self.lbl_resultados.setStyleSheet(f"color: {PALETA['texto_bajo']}; font-size: 12px;")
        self.btn_anterior = QPushButton("← Anterior")
        self.btn_siguiente = QPushButton("Siguiente →")
        for b in [self.btn_anterior, self.btn_siguiente]:
            b.setFixedHeight(38)
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.setStyleSheet(f"""
                QPushButton {{background: transparent; color: {PALETA['texto_alto']}; border: 1px solid {PALETA['borde']}; border-radius: 8px; padding: 0 20px; font-size: 13px;}}
                QPushButton:hover {{background: {PALETA['acento']}; border-color: {PALETA['acento']}; color: white;}}
                QPushButton:disabled {{color: {PALETA['texto_bajo']}; border-color: {PALETA['borde']}; background: transparent;}}""")
        self.btn_anterior.clicked.connect(self._ir_anterior)
        self.btn_siguiente.clicked.connect(self._ir_siguiente)
        self.lbl_pagina = QLabel("")
        self.lbl_pagina.setStyleSheet(f"color: {PALETA['texto_medio']}; font-size: 13px;")
        self.lbl_pagina.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_pagina.setFixedWidth(120)
        diseno.addWidget(self.lbl_resultados)
        diseno.addStretch()
        diseno.addWidget(self.btn_anterior)
        diseno.addWidget(self.lbl_pagina)
        diseno.addWidget(self.btn_siguiente)
        return pie

    def _limpiar_filtros(self):
        self.campo_nombre.clear()
        self.campo_creador.clear()
        self.combo_orden.setCurrentIndex(0)

    def _al_cambiar_filtro(self):
        txt_nombre = self.campo_nombre.text().lower().strip()
        txt_creador = self.campo_creador.text().lower().strip()
        orden = self.combo_orden.currentText()

        def tiene_creador(p):
            if not txt_creador:
                return True
            return any(txt_creador in c.get("nombre", "").lower() for c in p.creadores)

        lista_f = [p for p in self.personajes_totales
                   if txt_nombre in p.nombre.lower() and tiene_creador(p)]
        if orden == "Nombre  A → Z":
            lista_f.sort(key=lambda x: x.nombre.lower())
        elif orden == "Nombre  Z → A":
            lista_f.sort(key=lambda x: x.nombre.lower(), reverse=True)
        elif orden == "Más comics primero":
            lista_f.sort(key=lambda x: len(x.comics), reverse=True)
        self.personajes_filtrados = lista_f
        self.lista_paginas = ListaCircularDoblementeEnlazada()
        for i in range(0, len(self.personajes_filtrados), self.tamano_pagina):
            self.lista_paginas.agregar_pagina(self.personajes_filtrados[i: i + self.tamano_pagina])
        self.nodo_actual = self.lista_paginas.cabeza
        self._actualizar_vista()

    def _cancelar_hilos(self):
        for h in self.hilos_activos:
            h.cancelar()
        for h in self.hilos_activos:
            h.wait(200)
        self.hilos_activos.clear()
        self.mapa_labels.clear()

    def _actualizar_vista(self):
        self._cancelar_hilos()
        while self.grid_personajes.count():
            elem = self.grid_personajes.takeAt(0)
            w = elem.widget()
            if w:
                w.deleteLater()
        total = len(self.personajes_filtrados)
        total_pags = self.lista_paginas.total_paginas
        self.lbl_resultados.setText(
            f"{total} personaje{'s' if total != 1 else ''} encontrado{'s' if total != 1 else ''}")
        if not self.nodo_actual:
            self.lbl_pagina.setText("0  /  0")
            self.btn_anterior.setEnabled(False)
            self.btn_siguiente.setEnabled(False)
            lbl_vacio = QLabel("No se encontraron personajes con esos filtros.")
            lbl_vacio.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl_vacio.setStyleSheet(f"color: {PALETA['texto_bajo']}; font-size: 16px; padding: 60px;")
            self.grid_personajes.addWidget(lbl_vacio, 0, 0, 1, 2)
            return
        self.lbl_pagina.setText(f"{self.nodo_actual.numero_pagina}  /  {total_pags}")
        self.btn_anterior.setEnabled(total_pags > 1)
        self.btn_siguiente.setEnabled(total_pags > 1)
        for i, personaje in enumerate(self.nodo_actual.comics):  # NodoPagina guarda la lista bajo .comics
            tarjeta = TarjetaPersonaje(personaje)
            tarjeta.senal_detalle.connect(self._mostrar_detalle)
            self.grid_personajes.addWidget(tarjeta, i // 2, i % 2)
            if personaje.imagen_referencia:
                self._cargar_imagen_async(personaje.imagen_referencia, tarjeta.lbl_imagen, 60, 60, circular=True)

    def _cargar_imagen_async(self, url, lbl, ancho=60, alto=60, circular=False):
        if url in self.cache_imagenes:
            pixmap = self.cache_imagenes[url]
            lbl.setPixmap(pixmap)
            estilo = "border-radius: 30px; background: transparent;" if circular else "border-radius: 6px; background: transparent;"
            lbl.setStyleSheet(estilo)
            return
        ident = id(lbl)
        self.mapa_labels[ident] = (lbl, circular)
        hilo = CargadorImagen(url, ident, self.sesion, ancho, alto)
        hilo.carga_completa.connect(self._al_cargar_imagen)
        hilo.start()
        self.hilos_activos.append(hilo)
        self.hilos_activos = [h for h in self.hilos_activos if h.isRunning()]

    def _al_cargar_imagen(self, ident, pixmap):
        dato = self.mapa_labels.get(ident)
        if dato is None:
            return
        lbl, circular = dato
        try:
            lbl.setPixmap(pixmap)
            estilo = "border-radius: 30px; background: transparent;" if circular else "border-radius: 6px; background: transparent;"
            lbl.setStyleSheet(estilo)
        except RuntimeError:
            pass

    def _ir_anterior(self):
        if self.nodo_actual and self.nodo_actual.anterior:
            self.nodo_actual = self.nodo_actual.anterior
            self._actualizar_vista()

    def _ir_siguiente(self):
        if self.nodo_actual and self.nodo_actual.siguiente:
            self.nodo_actual = self.nodo_actual.siguiente
            self._actualizar_vista()

    def _mostrar_detalle(self, personaje):
        dialogo = QDialog(self)
        dialogo.setWindowTitle(personaje.nombre)
        dialogo.setMinimumSize(820, 680)
        dialogo.setStyleSheet(f"QDialog {{ background: {PALETA['fondo']}; }}")
        raiz = QVBoxLayout(dialogo)
        raiz.setContentsMargins(0, 0, 0, 0)
        raiz.setSpacing(0)
        cab = QWidget()
        cab.setFixedHeight(80)
        cab.setStyleSheet(f"""background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #001020, stop:1 {PALETA['fondo']});""")
        dis_cab = QHBoxLayout(cab)
        dis_cab.setContentsMargins(28, 0, 28, 0)
        barra = QWidget()
        barra.setFixedSize(4, 48)
        barra.setStyleSheet(f"background: {PALETA['acento']}; border-radius: 2px;")
        lbl_tit = QLabel(personaje.nombre)
        lbl_tit.setWordWrap(True)
        lbl_tit.setStyleSheet(f"color: {PALETA['texto_alto']}; font-size: 20px; font-weight: bold; padding-left: 14px;")
        dis_cab.addWidget(barra)
        dis_cab.addWidget(lbl_tit, 1)
        raiz.addWidget(cab)
        raiz.addWidget(DivisorRojo(1))
        area_scroll = QScrollArea()
        area_scroll.setWidgetResizable(True)
        area_scroll.setStyleSheet(f"background: {PALETA['fondo']}; border: none;")
        contenido = QWidget()
        contenido.setStyleSheet(f"background: {PALETA['fondo']};")
        dis_contenido = QVBoxLayout(contenido)
        dis_contenido.setContentsMargins(28, 24, 28, 24)
        dis_contenido.setSpacing(20)
        fila_top = QHBoxLayout()
        fila_top.setSpacing(24)
        lbl_img = QLabel()
        lbl_img.setFixedSize(120, 120)
        lbl_img.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_img.setStyleSheet(f"background: {PALETA['superficie']}; border-radius: 60px; color: {PALETA['texto_bajo']}; font-size: 30px;")
        lbl_img.setText("👤")
        if personaje.imagen_referencia:
            def _cargar(url, lbl_ref):
                try:
                    r = self.sesion.get(url, timeout=6)
                    if r.status_code == 200:
                        img = QImage()
                        img.loadFromData(r.content)
                        px = QPixmap.fromImage(img).scaled(
                            120, 120, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                        try:
                            lbl_ref.setPixmap(px)
                            lbl_ref.setStyleSheet("border-radius: 60px; background: transparent;")
                        except RuntimeError:
                            pass
                except Exception:
                    pass

            threading.Thread(target=_cargar, args=(personaje.imagen_referencia, lbl_img), daemon=True).start()
        col_desc = QVBoxLayout()
        col_desc.setSpacing(8)
        lbl_etiq_nombre = QLabel("PERSONAJE")
        lbl_etiq_nombre.setStyleSheet(f"color: {PALETA['acento']}; font-size: 10px; font-weight: bold; letter-spacing: 2px;")
        lbl_nombre_grande = QLabel(personaje.nombre)
        lbl_nombre_grande.setStyleSheet(f"color: {PALETA['texto_alto']}; font-size: 18px; font-weight: bold;")
        lbl_nombre_grande.setWordWrap(True)
        lbl_etiq_desc = QLabel("DESCRIPCIÓN")
        lbl_etiq_desc.setStyleSheet(f"color: {PALETA['acento']}; font-size: 10px; font-weight: bold; letter-spacing: 2px; margin-top: 4px;")
        visor_desc = QTextBrowser()
        visor_desc.setStyleSheet(f"""background: {PALETA['superficie']};border: 1px solid {PALETA['borde']}; border-radius: 8px; color: {PALETA['texto_medio']}; font-size: 13px;padding: 10px;""")
        visor_desc.setHtml(personaje.descripcion or "<i>Sin descripción disponible.</i>")
        visor_desc.setFixedHeight(100)
        col_desc.addWidget(lbl_etiq_nombre)
        col_desc.addWidget(lbl_nombre_grande)
        col_desc.addWidget(lbl_etiq_desc)
        col_desc.addWidget(visor_desc)
        col_desc.addStretch()
        fila_top.addWidget(lbl_img)
        fila_top.addLayout(col_desc, 1)
        dis_contenido.addLayout(fila_top)

        def _seccion_lista(titulo_sec, items, campo_nombre="nombre"):
            sec = QVBoxLayout()
            sec.setSpacing(6)
            lbl_sec = QLabel(titulo_sec.upper())
            lbl_sec.setStyleSheet(
                f"color: {PALETA['acento']}; font-size: 10px; font-weight: bold; letter-spacing: 2px;")
            sec.addWidget(lbl_sec)
            if not items:
                lbl_vacio = QLabel("No disponible")
                lbl_vacio.setStyleSheet(f"color: {PALETA['texto_bajo']}; font-size: 13px;")
                sec.addWidget(lbl_vacio)
                return sec
            paginas_items = [items[i:i + 10] for i in range(0, len(items), 10)]
            estado = {"pag": 0}
            contenedor_chips = QWidget()
            contenedor_chips.setStyleSheet("background: transparent;")
            dis_chips = QVBoxLayout(contenedor_chips)
            dis_chips.setContentsMargins(0, 0, 0, 0)
            dis_chips.setSpacing(4)
            pie_pag = QHBoxLayout()
            lbl_pag_num = QLabel(f"1 / {len(paginas_items)}")
            lbl_pag_num.setStyleSheet(f"color: {PALETA['texto_medio']}; font-size: 11px;")
            lbl_pag_num.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl_pag_num.setFixedWidth(70)

            def _renderizar_pagina():
                while dis_chips.count():
                    it = dis_chips.takeAt(0)
                    if it.widget():
                        it.widget().deleteLater()
                pag_items = paginas_items[estado["pag"]]
                fila_actual = None
                for idx, item in enumerate(pag_items):
                    if idx % 3 == 0:
                        fila_w = QWidget()
                        fila_w.setStyleSheet("background: transparent;")
                        fila_actual = QHBoxLayout(fila_w)
                        fila_actual.setContentsMargins(0, 0, 0, 0)
                        fila_actual.setSpacing(6)
                        dis_chips.addWidget(fila_w)
                    nombre_item = item.get(campo_nombre, "Desconocido")
                    chip = QLabel(nombre_item)
                    chip.setStyleSheet(
                        f"""background: {PALETA['superficie']};border: 1px solid {PALETA['borde']}; border-radius: 12px; color: {PALETA['texto_medio']}; font-size: 11px; padding: 4px 10px;""")
                    chip.setWordWrap(False)
                    fila_actual.addWidget(chip)
                if fila_actual:
                    fila_actual.addStretch()
                lbl_pag_num.setText(f"{estado['pag'] + 1} / {len(paginas_items)}")

            def _ant():
                if estado["pag"] > 0:
                    estado["pag"] -= 1
                    _renderizar_pagina()

            def _sig():
                if estado["pag"] < len(paginas_items) - 1:
                    estado["pag"] += 1
                    _renderizar_pagina()

            btn_ant_i = QPushButton("‹")
            btn_sig_i = QPushButton("›")
            for b in [btn_ant_i, btn_sig_i]:
                b.setFixedSize(26, 26)
                b.setCursor(Qt.CursorShape.PointingHandCursor)
                b.setStyleSheet(f"""QPushButton {{background: transparent; color: {PALETA['texto_medio']};border: 1px solid {PALETA['borde']}; border-radius: 13px;font-size: 14px;}}
                    QPushButton:hover {{background: {PALETA['acento']};color: white;border-color: {PALETA['acento']};}}""")
            btn_ant_i.clicked.connect(_ant)
            btn_sig_i.clicked.connect(_sig)
            pie_pag.addStretch()
            pie_pag.addWidget(btn_ant_i)
            pie_pag.addWidget(lbl_pag_num)
            pie_pag.addWidget(btn_sig_i)
            pie_pag.addStretch()
            _renderizar_pagina()
            sec.addWidget(contenedor_chips)
            if len(paginas_items) > 1:
                sec.addLayout(pie_pag)
            return sec

        dis_contenido.addLayout(_seccion_lista("Creadores", personaje.creadores))
        dis_contenido.addLayout(_seccion_lista("Comics", personaje.comics))
        dis_contenido.addLayout(_seccion_lista("Eventos", personaje.eventos))
        dis_contenido.addStretch()
        area_scroll.setWidget(contenido)
        raiz.addWidget(area_scroll, 1)
        pie_modal = QWidget()
        pie_modal.setFixedHeight(56)
        pie_modal.setStyleSheet(f"background: {PALETA['superficie']};")
        dis_pie = QHBoxLayout(pie_modal)
        dis_pie.setContentsMargins(28, 0, 28, 0)
        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.setFixedSize(100, 36)
        btn_cerrar.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cerrar.setStyleSheet(f"""
            QPushButton {{background: {PALETA['acento']}; color: white; border: none; border-radius: 8px; font-weight: bold; font-size: 13px;}}
            QPushButton:hover {{ background: #c42c2c; }}""")
        btn_cerrar.clicked.connect(dialogo.accept)
        dis_pie.addStretch()
        dis_pie.addWidget(btn_cerrar)
        raiz.addWidget(pie_modal)
        dialogo.exec()


class VentanaCatalogo(QMainWindow):
    def __init__(self, comics_totales, personajes_totales=None):
        super().__init__()
        self.comics_totales = comics_totales
        self.personajes_totales = personajes_totales or []
        self.comics_filtrados = list(comics_totales)
        self.tamano_pagina = 10
        self.lista_paginas = ListaCircularDoblementeEnlazada()
        self.nodo_actual = None
        self.cache_imagenes = {}
        self.hilos_activos = []
        self.mapa_labels = {}
        self.sesion = requests.Session()
        self._construir_ui()

    def _construir_ui(self):
        self.setWindowTitle("MUNDO COMIC — Catálogo Marvel")
        self.setMinimumSize(960, 720)
        self.setStyleSheet(ESTILO_PRINCIPAL)
        self.showMaximized()
        raiz = QWidget()
        raiz.setObjectName("raiz")
        raiz.setStyleSheet(f"background: {PALETA['fondo']};")
        self.setCentralWidget(raiz)
        contenedor_principal = QVBoxLayout(raiz)
        contenedor_principal.setContentsMargins(0, 0, 0, 0)
        contenedor_principal.setSpacing(0)
        contenedor_principal.addWidget(self._construir_encabezado())
        contenedor_principal.addWidget(self._construir_tabs())
        contenedor_principal.addWidget(DivisorRojo(1))
        self.panel_comics = QWidget()
        self.panel_comics.setStyleSheet(f"background: {PALETA['fondo']};")
        dis_comics = QVBoxLayout(self.panel_comics)
        dis_comics.setContentsMargins(0, 0, 0, 0)
        dis_comics.setSpacing(0)
        dis_comics.addWidget(self._construir_barra_filtros())
        dis_comics.addWidget(DivisorRojo(1))
        area_scroll = QScrollArea()
        area_scroll.setWidgetResizable(True)
        area_scroll.setStyleSheet(f"background: {PALETA['fondo']}; border: none;")
        self.widget_contenido = QWidget()
        self.widget_contenido.setStyleSheet(f"background: {PALETA['fondo']};")
        diseno_contenido = QVBoxLayout(self.widget_contenido)
        diseno_contenido.setContentsMargins(28, 24, 28, 24)
        diseno_contenido.setSpacing(16)
        contenedor_grid = QWidget()
        contenedor_grid.setStyleSheet("background: transparent;")
        diseno_centrado = QHBoxLayout(contenedor_grid)
        diseno_centrado.setContentsMargins(0, 0, 0, 0)
        self.widget_grid = QWidget()
        self.widget_grid.setStyleSheet("background: transparent;")
        self.grid_comics = QGridLayout(self.widget_grid)
        self.grid_comics.setSpacing(16)
        self.grid_comics.setAlignment(Qt.AlignmentFlag.AlignTop)
        diseno_centrado.addStretch()
        diseno_centrado.addWidget(self.widget_grid)
        diseno_centrado.addStretch()
        diseno_contenido.addWidget(contenedor_grid)
        diseno_contenido.addStretch()
        area_scroll.setWidget(self.widget_contenido)
        dis_comics.addWidget(area_scroll, 1)
        dis_comics.addWidget(DivisorRojo(1))
        dis_comics.addWidget(self._construir_pie())
        self.panel_personajes = VentanaPersonajes(self.personajes_totales, self.sesion, self.cache_imagenes)
        self.panel_personajes.setStyleSheet(f"background: {PALETA['fondo']};")
        self.stack = QWidget()
        self.stack.setStyleSheet(f"background: {PALETA['fondo']};")
        dis_stack = QVBoxLayout(self.stack)
        dis_stack.setContentsMargins(0, 0, 0, 0)
        dis_stack.setSpacing(0)
        dis_stack.addWidget(self.panel_comics)
        dis_stack.addWidget(self.panel_personajes)
        self.panel_personajes.hide()
        contenedor_principal.addWidget(self.stack, 1)
        self._al_cambiar_filtro()

    def _construir_tabs(self):
        barra_tabs = QWidget()
        barra_tabs.setFixedHeight(46)
        barra_tabs.setStyleSheet(f"background: {PALETA['superficie']};")
        diseno = QHBoxLayout(barra_tabs)
        diseno.setContentsMargins(28, 0, 28, 0)
        diseno.setSpacing(0)
        estilo_tab_activo = f"""QPushButton {{background: transparent;color: {PALETA['texto_alto']}; border: none; border-bottom: 2px solid {PALETA['acento']}; padding: 0 24px; font-size: 13px; font-weight: bold; height: 46px;}}"""
        estilo_tab_inactivo = f"""QPushButton {{background: transparent;color: {PALETA['texto_bajo']}; border: none;border-bottom: 2px solid transparent; padding: 0 24px; font-size: 13px; height: 46px;}}
            QPushButton:hover {{color: {PALETA['texto_medio']}; border-bottom: 2px solid {PALETA['borde']};}}"""
        self.btn_tab_comics = QPushButton("📚  Cómics")
        self.btn_tab_comics.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_tab_comics.setStyleSheet(estilo_tab_activo)
        self.btn_tab_comics.setFixedHeight(46)
        self.btn_tab_personajes = QPushButton("🦸  Personajes")
        self.btn_tab_personajes.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_tab_personajes.setStyleSheet(estilo_tab_inactivo)
        self.btn_tab_personajes.setFixedHeight(46)

        def _ir_comics():
            self.panel_comics.show()
            self.panel_personajes.hide()
            self.btn_tab_comics.setStyleSheet(estilo_tab_activo)
            self.btn_tab_personajes.setStyleSheet(estilo_tab_inactivo)

        def _ir_personajes():
            self.panel_comics.hide()
            self.panel_personajes.show()
            self.btn_tab_personajes.setStyleSheet(estilo_tab_activo)
            self.btn_tab_comics.setStyleSheet(estilo_tab_inactivo)

        self.btn_tab_comics.clicked.connect(_ir_comics)
        self.btn_tab_personajes.clicked.connect(_ir_personajes)
        diseno.addWidget(self.btn_tab_comics)
        diseno.addWidget(self.btn_tab_personajes)
        diseno.addStretch()
        return barra_tabs

    def _construir_encabezado(self):
        encabezado = QWidget()
        encabezado.setFixedHeight(100)
        encabezado.setStyleSheet(f"""background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1a0000, stop:0.5 #0d0d0d, stop:1 #1a0000);""")
        diseno = QHBoxLayout(encabezado)
        diseno.setContentsMargins(32, 0, 32, 0)
        col_logo = QVBoxLayout()
        col_logo.setSpacing(2)
        lbl_marca = QLabel("MUNDO MARVEL")
        lbl_marca.setStyleSheet(f"""color: {PALETA['acento']}; font-size: 36px; font-weight: 900; letter-spacing: 6px;font-family: 'Impact', 'Arial Black', sans-serif;""")
        lbl_slogan = QLabel("TU CATÁLOGO OFICIAL")
        lbl_slogan.setStyleSheet(f"color: {PALETA['texto_bajo']}; font-size: 10px; letter-spacing: 4px;")
        col_logo.addStretch()
        col_logo.addWidget(lbl_marca)
        col_logo.addWidget(lbl_slogan)
        col_logo.addStretch()
        col_stats = QVBoxLayout()
        col_stats.setSpacing(4)
        col_stats.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.lbl_total = QLabel(f"{len(self.comics_totales)} cómics")
        self.lbl_total.setStyleSheet(f"color: {PALETA['dorado']}; font-size: 22px; font-weight: bold;")
        self.lbl_total.setAlignment(Qt.AlignmentFlag.AlignRight)
        lbl_subtitulo = QLabel("en la biblioteca")
        lbl_subtitulo.setStyleSheet(f"color: {PALETA['texto_bajo']}; font-size: 11px;")
        lbl_subtitulo.setAlignment(Qt.AlignmentFlag.AlignRight)
        col_stats.addStretch()
        col_stats.addWidget(self.lbl_total)
        col_stats.addWidget(lbl_subtitulo)
        col_stats.addStretch()
        diseno.addLayout(col_logo)
        diseno.addStretch()
        diseno.addLayout(col_stats)
        return encabezado

    def _construir_barra_filtros(self):
        barra = QWidget()
        barra.setFixedHeight(70)
        barra.setStyleSheet(f"background: {PALETA['superficie']};")
        diseno = QHBoxLayout(barra)
        diseno.setContentsMargins(28, 12, 28, 12)
        diseno.setSpacing(10)
        self.campo_titulo = QLineEdit()
        self.campo_titulo.setPlaceholderText("🔍  Buscar por título…")
        self.campo_titulo.setFixedWidth(240)
        self.campo_titulo.textChanged.connect(self._al_cambiar_filtro)
        self.campo_anio = QLineEdit()
        self.campo_anio.setPlaceholderText("📅  Año")
        self.campo_anio.setFixedWidth(140)
        self.campo_anio.textChanged.connect(self._al_cambiar_filtro)
        separador = QLabel("|")
        separador.setStyleSheet(f"color: {PALETA['borde']}; font-size: 20px;")
        lbl_ordenar = QLabel("Ordenar:")
        lbl_ordenar.setStyleSheet(f"color: {PALETA['texto_medio']}; font-size: 12px;")
        self.combo_orden = QComboBox()
        self.combo_orden.addItems(["Más recientes primero", "Más antiguos primero", "Título  A → Z", "Título  Z → A"])
        self.combo_orden.currentIndexChanged.connect(self._al_cambiar_filtro)
        btn_limpiar = QPushButton("✕  Limpiar")
        btn_limpiar.setFixedHeight(36)
        btn_limpiar.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_limpiar.setStyleSheet(f"""QPushButton {{background: transparent; color: {PALETA['texto_bajo']}; border: 1px solid {PALETA['borde']}; border-radius: 6px; padding: 0 14px; font-size: 12px;}}
            QPushButton:hover {{color: {PALETA['texto_alto']}; border-color: {PALETA['texto_medio']};}}""")
        btn_limpiar.clicked.connect(self._limpiar_filtros)
        diseno.addWidget(self.campo_titulo)
        diseno.addWidget(self.campo_anio)
        diseno.addWidget(separador)
        diseno.addWidget(lbl_ordenar)
        diseno.addWidget(self.combo_orden)
        diseno.addStretch()
        diseno.addWidget(btn_limpiar)
        return barra

    def _construir_pie(self):
        pie = QWidget()
        pie.setFixedHeight(64)
        pie.setStyleSheet(f"background: {PALETA['superficie']};")
        diseno = QHBoxLayout(pie)
        diseno.setContentsMargins(28, 0, 28, 0)
        self.lbl_resultados = QLabel("")
        self.lbl_resultados.setStyleSheet(f"color: {PALETA['texto_bajo']}; font-size: 12px;")
        self.btn_anterior = QPushButton("← Anterior")
        self.btn_siguiente = QPushButton("Siguiente →")
        for boton in [self.btn_anterior, self.btn_siguiente]:
            boton.setFixedHeight(38)
            boton.setCursor(Qt.CursorShape.PointingHandCursor)
            self._aplicar_estilo_boton_nav(boton)
        self.btn_anterior.clicked.connect(self._ir_anterior)
        self.btn_siguiente.clicked.connect(self._ir_siguiente)
        self.lbl_pagina = QLabel("")
        self.lbl_pagina.setStyleSheet(f"color: {PALETA['texto_medio']}; font-size: 13px;")
        self.lbl_pagina.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_pagina.setFixedWidth(120)
        diseno.addWidget(self.lbl_resultados)
        diseno.addStretch()
        diseno.addWidget(self.btn_anterior)
        diseno.addWidget(self.lbl_pagina)
        diseno.addWidget(self.btn_siguiente)
        return pie

    def _aplicar_estilo_boton_nav(self, boton):
        boton.setStyleSheet(f"""QPushButton {{background: transparent; color: {PALETA['texto_alto']}; border: 1px solid {PALETA['borde']}; border-radius: 8px; padding: 0 20px; font-size: 13px;}}
            QPushButton:hover {{background: {PALETA['acento']}; border-color: {PALETA['acento']}; color: white;}}
            QPushButton:disabled {{color: {PALETA['texto_bajo']}; border-color: {PALETA['borde']}; background: transparent;}}""")

    def _al_cambiar_filtro(self):
        texto = self.campo_titulo.text().lower().strip()
        anio = self.campo_anio.text().strip()
        orden = self.combo_orden.currentText()
        lista_filtrada = [c for c in self.comics_totales if (texto in c.titulo.lower()) and (anio in (c.fecha_lanzamiento or "") if anio else True)]
        if orden == "Título  A → Z":
            lista_filtrada.sort(key=lambda x: x.titulo.lower())
        elif orden == "Título  Z → A":
            lista_filtrada.sort(key=lambda x: x.titulo.lower(), reverse=True)
        elif orden == "Más recientes primero":
            lista_filtrada.sort(key=lambda x: x.fecha_lanzamiento or "", reverse=True)
        elif orden == "Más antiguos primero":
            lista_filtrada.sort(key=lambda x: x.fecha_lanzamiento or "")
        self.comics_filtrados = lista_filtrada
        self.lista_paginas = ListaCircularDoblementeEnlazada()
        for i in range(0, len(self.comics_filtrados), self.tamano_pagina):
            pagina_comics = self.comics_filtrados[i: i + self.tamano_pagina]
            self.lista_paginas.agregar_pagina(pagina_comics)
        self.nodo_actual = self.lista_paginas.cabeza
        self._actualizar_vista()

    def _limpiar_filtros(self):
        self.campo_titulo.clear()
        self.campo_anio.clear()
        self.combo_orden.setCurrentIndex(0)

    def _cancelar_hilos_activos(self):
        for hilo in self.hilos_activos:
            hilo.cancelar()
        for hilo in self.hilos_activos:
            hilo.wait(200)
        self.hilos_activos.clear()
        self.mapa_labels.clear()

    def _actualizar_vista(self):
        self._cancelar_hilos_activos()
        while self.grid_comics.count():
            elemento = self.grid_comics.takeAt(0)
            widget = elemento.widget()
            if widget:
                widget.deleteLater()
        total_comics = len(self.comics_filtrados)
        total_paginas = self.lista_paginas.total_paginas
        self.lbl_resultados.setText(f"{total_comics} resultado{'s' if total_comics != 1 else ''} encontrado{'s' if total_comics != 1 else ''}")
        if not self.nodo_actual:
            self.lbl_pagina.setText("0  /  0")
            self.btn_anterior.setEnabled(False)
            self.btn_siguiente.setEnabled(False)
            lbl_vacio = QLabel("No se encontraron cómics con esos filtros.")
            lbl_vacio.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl_vacio.setStyleSheet(f"color: {PALETA['texto_bajo']}; font-size: 16px; padding: 60px;")
            self.grid_comics.addWidget(lbl_vacio, 0, 0, 1, 2)
            return
        self.lbl_pagina.setText(f"{self.nodo_actual.numero_pagina}  /  {total_paginas}")
        self.btn_anterior.setEnabled(total_paginas > 1)
        self.btn_siguiente.setEnabled(total_paginas > 1)
        comics_mostrar = self.nodo_actual.comics
        for i, comic in enumerate(comics_mostrar):
            tarjeta = TarjetaComic(comic)
            tarjeta.senal_detalle.connect(self._mostrar_detalle)
            self.grid_comics.addWidget(tarjeta, i // 2, i % 2)
            if comic.imagen_referencia:
                self._cargar_imagen_async(comic.imagen_referencia, tarjeta.lbl_imagen)

    def _cargar_imagen_async(self, url, lbl):
        if url in self.cache_imagenes:
            lbl.setPixmap(self.cache_imagenes[url])
            lbl.setStyleSheet("border-radius: 6px; background: transparent;")
            return
        identificador = id(lbl)
        self.mapa_labels[identificador] = lbl
        hilo = CargadorImagen(url, identificador, self.sesion, 110, 166)
        hilo.carga_completa.connect(self._al_cargar_imagen)
        hilo.start()
        self.hilos_activos.append(hilo)
        self.hilos_activos = [h for h in self.hilos_activos if h.isRunning()]

    def _al_cargar_imagen(self, identificador, pixmap):
        lbl = self.mapa_labels.get(identificador)
        if lbl is None:
            return
        try:
            lbl.setPixmap(pixmap)
            lbl.setStyleSheet("border-radius: 6px; background: transparent;")
        except RuntimeError:
            pass

    def _ir_anterior(self):
        if self.nodo_actual and self.nodo_actual.anterior:
            self.nodo_actual = self.nodo_actual.anterior
            self._actualizar_vista()

    def _ir_siguiente(self):
        if self.nodo_actual and self.nodo_actual.siguiente:
            self.nodo_actual = self.nodo_actual.siguiente
            self._actualizar_vista()

    def _mostrar_detalle(self, comic):
        dialogo = QDialog(self)
        dialogo.setWindowTitle(comic.titulo)
        dialogo.setMinimumSize(760, 620)
        dialogo.setStyleSheet(f"QDialog {{ background: {PALETA['fondo']}; }}")
        diseno_raiz = QVBoxLayout(dialogo)
        diseno_raiz.setContentsMargins(0, 0, 0, 0)
        diseno_raiz.setSpacing(0)
        cabecera = QWidget()
        cabecera.setFixedHeight(80)
        cabecera.setStyleSheet(f"""background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #200000, stop:1 {PALETA['fondo']});""")
        diseno_cabecera = QHBoxLayout(cabecera)
        diseno_cabecera.setContentsMargins(28, 0, 28, 0)
        barra_acento = QWidget()
        barra_acento.setFixedSize(4, 48)
        barra_acento.setStyleSheet(f"background: {PALETA['acento']}; border-radius: 2px;")
        lbl_titulo_modal = QLabel(comic.titulo)
        lbl_titulo_modal.setWordWrap(True)
        lbl_titulo_modal.setStyleSheet(f"""color: {PALETA['texto_alto']}; font-size: 20px; font-weight: bold;padding-left: 14px;""")
        diseno_cabecera.addWidget(barra_acento)
        diseno_cabecera.addWidget(lbl_titulo_modal, 1)
        diseno_raiz.addWidget(cabecera)
        diseno_raiz.addWidget(DivisorRojo(1))
        cuerpo = QWidget()
        cuerpo.setStyleSheet(f"background: {PALETA['fondo']};")
        diseno_cuerpo = QHBoxLayout(cuerpo)
        diseno_cuerpo.setContentsMargins(28, 24, 28, 24)
        diseno_cuerpo.setSpacing(28)
        col_imagen = QVBoxLayout()
        col_imagen.setAlignment(Qt.AlignmentFlag.AlignTop)
        lbl_imagen_det = QLabel()
        lbl_imagen_det.setFixedSize(160, 240)
        lbl_imagen_det.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_imagen_det.setStyleSheet(f"""background: {PALETA['superficie']}; border-radius: 8px; color: {PALETA['texto_bajo']};font-size: 20px;""")
        lbl_imagen_det.setText("⏳")
        lbl_fecha_det = QLabel(f"📅  {comic.fecha_lanzamiento or 'N/A'}")
        lbl_fecha_det.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_fecha_det.setStyleSheet(f"color: {PALETA['texto_medio']}; font-size: 12px; padding-top: 8px;")
        col_imagen.addWidget(lbl_imagen_det)
        col_imagen.addWidget(lbl_fecha_det)
        col_imagen.addStretch()
        if comic.imagen_referencia:
            def _cargar_img_detalle(url, lbl):
                try:
                    resp = self.sesion.get(url, timeout=6)
                    if resp.status_code == 200:
                        imagen = QImage()
                        imagen.loadFromData(resp.content)
                        pixmap = QPixmap.fromImage(imagen).scaled(160, 240, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                        try:
                            lbl.setPixmap(pixmap)
                            lbl.setStyleSheet("border-radius: 8px; background: transparent;")
                        except RuntimeError:
                            pass
                except Exception:
                    pass
            hilo_det = threading.Thread(target=_cargar_img_detalle, args=(comic.imagen_referencia, lbl_imagen_det), daemon=True)
            hilo_det.start()
        col_texto = QVBoxLayout()
        col_texto.setSpacing(14)

        def _crear_seccion(titulo_seccion, contenido_texto):
            seccion = QVBoxLayout()
            seccion.setSpacing(4)
            lbl_tit = QLabel(titulo_seccion.upper())
            lbl_tit.setStyleSheet(f"""color: {PALETA['acento']}; font-size: 10px; font-weight: bold; letter-spacing: 2px; """)
            lbl_cont = QLabel(contenido_texto)
            lbl_cont.setWordWrap(True)
            lbl_cont.setStyleSheet(f"color: {PALETA['texto_medio']}; font-size: 13px;")
            seccion.addWidget(lbl_tit)
            seccion.addWidget(lbl_cont)
            return seccion

        def _obtener_nombre(d):
            return d.get("nombre") or d.get("name") or "Desconocido"
        lista_personajes = comic.personajes or []
        lista_creadores = comic.creadores or []
        texto_personajes = (", ".join(_obtener_nombre(p) for p in lista_personajes) if lista_personajes else "No disponible")
        texto_creadores = (", ".join(_obtener_nombre(c) for c in lista_creadores) if lista_creadores else "No disponible")
        col_texto.addLayout(_crear_seccion("Personajes", texto_personajes))
        col_texto.addLayout(_crear_seccion("Creadores", texto_creadores))
        lbl_sin_titulo = QLabel("SINOPSIS")
        lbl_sin_titulo.setStyleSheet(f"""color: {PALETA['acento']}; font-size: 10px; font-weight: bold;letter-spacing: 2px;""")
        visor_descripcion = QTextBrowser()
        visor_descripcion.setStyleSheet(f"""background: {PALETA['superficie']}; border: 1px solid {PALETA['borde']}; border-radius: 8px; color: {PALETA['texto_medio']}; font-size: 13px; padding: 12px;""")
        visor_descripcion.setHtml(comic.descripcion or "<i>Sin descripción disponible.</i>")
        visor_descripcion.setMinimumHeight(160)
        col_texto.addWidget(lbl_sin_titulo)
        col_texto.addWidget(visor_descripcion, 1)
        diseno_cuerpo.addLayout(col_imagen)
        diseno_cuerpo.addLayout(col_texto, 1)
        diseno_raiz.addWidget(cuerpo, 1)
        pie_modal = QWidget()
        pie_modal.setFixedHeight(56)
        pie_modal.setStyleSheet(f"background: {PALETA['superficie']};")
        diseno_pie = QHBoxLayout(pie_modal)
        diseno_pie.setContentsMargins(28, 0, 28, 0)
        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.setFixedSize(100, 36)
        btn_cerrar.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cerrar.setStyleSheet(f"""QPushButton {{background: {PALETA['acento']}; color: white; border: none; border-radius: 8px; font-weight: bold; font-size: 13px;}}
            QPushButton:hover {{background: #c42c2c;}}""")
        btn_cerrar.clicked.connect(dialogo.accept)
        diseno_pie.addStretch()
        diseno_pie.addWidget(btn_cerrar)
        diseno_raiz.addWidget(pie_modal)
        dialogo.exec()

if __name__ == "__main__":
    CLAVE_API = "aca41dd517e3946fa374082173c07f73050d497b"
    ARCHIVO_JSON = "comics_oficiales.json"
    def _json_necesita_regeneracion(ruta):
        if not os.path.exists(ruta):
            return True
        try:
            datos = GestorArchivos.leer_de_json(ruta)
            if not datos:
                return True
            vacios = any(
                len(d.get("personajes", [])) == 0 or len(d.get("creadores", [])) == 0 for d in datos)
            return vacios
        except Exception:
            return True

    if _json_necesita_regeneracion(ARCHIVO_JSON):
        print("=" * 55)
        print("  Generando cómics MARVEL (versión estable)...")
        print("=" * 55)
        if os.path.exists(ARCHIVO_JSON):
            os.remove(ARCHIVO_JSON)
        cliente = ClienteComicVineAPI(CLAVE_API)
        datos_crudos = cliente.obtener_comics()
        lista_comics = []
        for elemento in datos_crudos:
            titulo = elemento.get("name")
            if not titulo:
                titulo = f"{elemento.get('volume', {}).get('name', 'Sin título')} #{elemento.get('issue_number', '0')}"
            imagen = elemento.get("image", {})
            url_imagen = imagen.get("original_url") or imagen.get("medium_url") or ""
            nuevo_comic = Comic(titulo, "N/A", elemento.get("cover_date", "N/A"), url_imagen, elemento.get("description", ""))
            nuevo_comic.personajes = [{"nombre": p.get("name", "Desconocido")} for p in (elemento.get("character_credits") or [])]
            nuevo_comic.creadores = [{"nombre": c.get("name", "Desconocido")} for c in (elemento.get("person_credits") or [])]
            lista_comics.append(nuevo_comic.mostrar_info())
        GestorArchivos.guardar_en_json(ARCHIVO_JSON, lista_comics)
    datos_guardados = GestorArchivos.leer_de_json(ARCHIVO_JSON)
    comics_cargados = []
    for dato in datos_guardados:
        comic_obj = Comic(dato["titulo"], dato["isbn"], dato["fecha_lanzamiento"], dato["imagen_referencia"], dato.get("descripcion", ""))
        comic_obj.personajes = dato.get("personajes", [])
        comic_obj.creadores = dato.get("creadores", [])
        comics_cargados.append(comic_obj)
    lista_sl_personajes = ListaSimplementeLigadaPersonajes()
    mapa_personajes = {}
    for comic_obj in comics_cargados:
        creadores_comic = comic_obj.creadores
        for p_dict in comic_obj.personajes:
            nombre_p = p_dict.get("nombre", "").strip()
            if not nombre_p or nombre_p == "Desconocido":
                continue
            if nombre_p not in mapa_personajes:
                personaje_obj = Personaje(nombre=nombre_p)
                personaje_obj.creadores = list(creadores_comic)
                personaje_obj.comics.append({"nombre": comic_obj.titulo})
                mapa_personajes[nombre_p] = personaje_obj
                lista_sl_personajes.agregar(personaje_obj)
            else:
                personaje_existente = mapa_personajes[nombre_p]
                titulos_existentes = {c["nombre"] for c in personaje_existente.comics}
                if comic_obj.titulo not in titulos_existentes:
                    personaje_existente.comics.append({"nombre": comic_obj.titulo})
    personajes_cargados = lista_sl_personajes.lista()
    print(f"Personajes únicos extraídos: {len(personajes_cargados)}")
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    ventana = VentanaCatalogo(comics_cargados, personajes_cargados)
    ventana.show()
    sys.exit(app.exec())