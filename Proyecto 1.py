import sys
import threading
import os
import json
import requests
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,QPushButton, QLabel, QGridLayout, QFrame, QDialog, QTextBrowser,QLineEdit, QComboBox, QScrollArea, QGraphicsDropShadowEffect,QSizePolicy, QScrollBar
from PyQt6.QtCore import Qt, pyqtSignal, QThread
from PyQt6.QtGui import QPixmap, QImage, QColor, QPainter, QLinearGradient, QBrush

PALETA = {"fondo":"#0d0d0d","superficie":"#141414","tarjeta":"#1a1a1a","tarjeta_hover":"#222222","borde":"#2a2a2a","acento":"#e23636","acento2":"#ff6b35","dorado":"#f5c518","texto_alto":"#f0f0f0","texto_medio":"#a0a0a0","texto_bajo":"#555555"}

ESTILO_PRINCIPAL = f"""
    QMainWindow, QWidget#raiz {{
        background-color: {PALETA['fondo']};
    }}
    QWidget {{
        color: {PALETA['texto_alto']};
        font-family: 'Segoe UI', sans-serif;
    }}
    QScrollArea {{
        border: none;
        background: transparent;
    }}
    QScrollBar:vertical {{
        background: {PALETA['superficie']};
        width: 6px;
        border-radius: 3px;
    }}
    QScrollBar::handle:vertical {{
        background: {PALETA['acento']};
        border-radius: 3px;
        min-height: 30px;
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}
    QLineEdit {{
        background: {PALETA['superficie']};
        border: 1px solid {PALETA['borde']};
        border-radius: 6px;
        padding: 9px 14px;
        color: {PALETA['texto_alto']};
        font-size: 13px;
        selection-background-color: {PALETA['acento']};
    }}
    QLineEdit:focus {{
        border: 1px solid {PALETA['acento']};
    }}
    QComboBox {{
        background: {PALETA['superficie']};
        border: 1px solid {PALETA['borde']};
        border-radius: 6px;
        padding: 9px 14px;
        color: {PALETA['texto_alto']};
        font-size: 13px;
        min-width: 160px;
    }}
    QComboBox:focus {{
        border: 1px solid {PALETA['acento']};
    }}
    QComboBox::drop-down {{
        border: none;
        width: 30px;
    }}
    QComboBox::down-arrow {{
        image: none;
        border-left: 5px solid transparent;
        border-right: 5px solid transparent;
        border-top: 6px solid {PALETA['acento']};
        width: 0; height: 0;
        margin-right: 10px;
    }}
    QComboBox QAbstractItemView {{
        background: {PALETA['superficie']};
        border: 1px solid {PALETA['borde']};
        selection-background-color: {PALETA['acento']};
        color: {PALETA['texto_alto']};
        outline: none;
    }}
    QDialog {{
        background: {PALETA['fondo']};
    }}
    QTextBrowser {{
        background: transparent;
        border: none;
        color: {PALETA['texto_medio']};
        font-size: 13px;
    }}
"""

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
        self._construir_ui()
        self._aplicar_sombra()
        self._estilo_normal()

    def _aplicar_sombra(self):
        sombra = QGraphicsDropShadowEffect(self)
        sombra.setBlurRadius(20)
        sombra.setOffset(0, 4)
        sombra.setColor(QColor(0, 0, 0, 120))
        self.setGraphicsEffect(sombra)

    def _estilo_normal(self):
        self.setStyleSheet(f"""
            QFrame {{
                background: {PALETA['tarjeta']};
                border: 1px solid {PALETA['borde']};
                border-radius: 10px;
            }}
        """)

    def _estilo_hover(self):
        self.setStyleSheet(f"""
            QFrame {{
                background: {PALETA['tarjeta_hover']};
                border: 1px solid {PALETA['acento']};
                border-radius: 10px;
            }}
        """)

    def enterEvento(self, evento):
        self._estilo_hover()
        super().enterEvent(evento)

    def leaveEvento(self, evento):
        self._estilo_normal()
        super().leaveEvent(evento)

    def mousePressEvent(self, evento):
        if evento.button() == Qt.MouseButton.LeftButton:
            self.senal_detalle.emit(self.comic)

    def _construir_ui(self):
        contenedor = QHBoxLayout(self)
        contenedor.setContentsMargins(14, 14, 18, 14)
        contenedor.setSpacing(16)

        self.lbl_imagen = QLabel()
        self.lbl_imagen.setFixedSize(110, 166)
        self.lbl_imagen.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_imagen.setStyleSheet(f"""
            background: {PALETA['superficie']};
            border-radius: 6px;
            color: {PALETA['texto_bajo']};
            font-size: 20px;
        """)
        self.lbl_imagen.setText("⏳")

        columna_info = QVBoxLayout()
        columna_info.setSpacing(6)

        lbl_editorial = QLabel("MARVEL COMICS")
        lbl_editorial.setStyleSheet(f"""
            color: {PALETA['acento']};
            font-size: 10px;
            font-weight: bold;
            letter-spacing: 2px;
        """)

        titulo_recortado = self.comic.titulo[:58] + ("…" if len(self.comic.titulo) > 58 else "")
        lbl_titulo = QLabel(titulo_recortado)
        lbl_titulo.setWordWrap(True)
        lbl_titulo.setStyleSheet(f"""
            color: {PALETA['texto_alto']};
            font-size: 15px;
            font-weight: bold;
        """)

        #Aqui mostramos que fecha salio el comic
        fila_fecha = QHBoxLayout()
        lbl_rombo = QLabel("◆")
        lbl_rombo.setStyleSheet(f"color: {PALETA['dorado']}; font-size: 8px;")
        lbl_rombo.setFixedWidth(14)
        lbl_fecha_val = QLabel(self.comic.fecha_lanzamiento or "Fecha desconocida")
        lbl_fecha_val.setStyleSheet(f"color: {PALETA['texto_medio']}; font-size: 12px;")
        fila_fecha.addWidget(lbl_rombo)
        fila_fecha.addWidget(lbl_fecha_val)
        fila_fecha.addStretch()

        #Aqui mostramos cuantos personajes hay en comic
        cantidad_personajes = len(self.comic.personajes)
        lbl_personajes = QLabel(f"👥  {cantidad_personajes} personaje{'s' if cantidad_personajes != 1 else ''}")
        lbl_personajes.setStyleSheet(f"color: {PALETA['texto_bajo']}; font-size: 11px;")

        btn_detalle = QPushButton("Ver detalle  →")
        btn_detalle.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_detalle.setFixedHeight(32)
        btn_detalle.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {PALETA['acento']};
                border: 1px solid {PALETA['acento']};
                border-radius: 6px;
                font-size: 12px;
                font-weight: bold;
                padding: 0 12px;
            }}
            QPushButton:hover {{
                background: {PALETA['acento']};
                color: white;
            }}
        """)
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
        self.url        = url
        self.id_widget  = id_widget
        self.sesion     = sesion
        self.ancho      = ancho
        self.alto       = alto
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
                pixmap = QPixmap.fromImage(imagen).scaled(
                    self.ancho, self.alto,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                if not self._cancelado:
                    self.carga_completa.emit(self.id_widget, pixmap)
        except Exception:
            pass

class Comic:
    def __init__(self, titulo, isbn, fecha_lanzamiento, imagen_referencia, descripcion=""):
        self.titulo           = titulo
        self.isbn             = isbn
        self.fecha_lanzamiento = fecha_lanzamiento
        self.imagen_referencia = imagen_referencia
        self.descripcion      = descripcion
        self.personajes       = []
        self.creadores        = []

    def mostrar_info(self):
        return {
            "titulo":            self.titulo,
            "isbn":              self.isbn,
            "fecha_lanzamiento": self.fecha_lanzamiento,
            "imagen_referencia": self.imagen_referencia,
            "descripcion":       self.descripcion,
            "personajes":        self.personajes,
            "creadores":         self.creadores,
        }


class NodoPagina:
    def __init__(self, datos):
        self.datos     = datos
        self.siguiente = None
        self.anterior  = None


class ListaCircularDoblementeEnlazada:
    def __init__(self):
        self.cabeza = None
        self.cola   = None

    def agregar_pagina(self, datos):
        nuevo_nodo = NodoPagina(datos)
        if not self.cabeza:
            self.cabeza           = nuevo_nodo
            self.cola             = nuevo_nodo
            self.cabeza.siguiente = self.cabeza
            self.cabeza.anterior  = self.cabeza
        else:
            nuevo_nodo.anterior      = self.cola
            nuevo_nodo.siguiente     = self.cabeza
            self.cola.siguiente      = nuevo_nodo
            self.cabeza.anterior     = nuevo_nodo
            self.cola                = nuevo_nodo


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


class Paginador:
    @staticmethod
    def construir_lista_paginada(datos_completos, tamano_pagina=10):
        lista_circular = ListaCircularDoblementeEnlazada()
        for i in range(0, len(datos_completos), tamano_pagina):
            lista_circular.agregar_pagina(datos_completos[i:i + tamano_pagina])
        return lista_circular

class VentanaCatalogo(QMainWindow):
    def __init__(self, comics_totales):
        super().__init__()
        self.comics_totales   = comics_totales
        self.comics_filtrados = list(comics_totales)
        self.indice_pagina    = 0
        self.tamano_pagina    = 8
        self.cache_imagenes   = {}
        self.hilos_activos    = []
        self.mapa_labels      = {}
        self.sesion           = requests.Session()
        self._construir_ui()

if __name__ == "__main__":
    CLAVE_API = "aca41dd517e3946fa374082173c07f73050d497b"
    ARCHIVO_JSON = "comics_oficiales.json"

    PALABRAS_MARVEL = [
        "spider", "x-men", "avengers", "iron man", "thor",
        "captain", "hulk", "daredevil", "fantastic",
        "silver surfer", "marvel", "ultimate"
    ]

    def _json_necesita_regeneracion(ruta):
        if not os.path.exists(ruta):
            return True
        try:
            datos = GestorArchivos.leer_de_json(ruta)
            if not datos:
                return True

            vacios = any(
                len(d.get("personajes", [])) == 0 or len(d.get("creadores", [])) == 0
                for d in datos
            )
            return vacios
        except Exception:
            return True

    comics = []
    for d in datos:
        c = Comic(
            d["titulo"],
            d["isbn"],
            d["fecha_lanzamiento"],
            d["imagen_referencia"]
        )
        comics.append(c)

    app = QApplication(sys.argv)
    sys.exit(app.exec())