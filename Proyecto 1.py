import sys
import os
import json
import requests
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,QPushButton, QLabel, QGridLayout, QFrame, QSizePolicy
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap, QColor, QPainter, QLinearGradient, QBrush

PALETA = {
    "fondo": "#0d0d0d",
    "superficie": "#141414",
    "tarjeta": "#1a1a1a",
    "tarjeta_hover": "#222222",
    "borde": "#2a2a2a",
    "acento": "#e23636",
    "acento2": "#ff6b35",
    "dorado": "#f5c518",
    "texto_alto": "#f0f0f0",
    "texto_medio": "#a0a0a0",
    "texto_bajo": "#555555"
}

ESTILO_PRINCIPAL = f"""
QWidget {{
    color: {PALETA['texto_alto']};
    font-family: 'Segoe UI';
}}
QMainWindow {{
    background: {PALETA['fondo']};
}}
"""

class DivisorRojo(QWidget):
    def __init__(self, altura=1, parent=None):
        super().__init__(parent)
        self.setFixedHeight(altura)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

    def paintEvent(self, event):
        painter = QPainter(self)
        gradient = QLinearGradient(0, 0, self.width(), 0)

        gradient.setColorAt(0.0, QColor(0, 0, 0, 0))
        gradient.setColorAt(0.5, QColor(PALETA["acento"]))
        gradient.setColorAt(1.0, QColor(0, 0, 0, 0))

        painter.fillRect(self.rect(), QBrush(gradient))

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
        return {
            "titulo": self.titulo,
            "isbn": self.isbn,
            "fecha_lanzamiento": self.fecha_lanzamiento,
            "imagen_referencia": self.imagen_referencia,
            "descripcion": self.descripcion,
            "personajes": self.personajes,
            "creadores": self.creadores,
        }

class NodoPagina:
    def __init__(self, datos):
        self.datos = datos
        self.siguiente = None
        self.anterior = None


class ListaCircularDoblementeEnlazada:
    def __init__(self):
        self.cabeza = None
        self.cola = None

    def agregar_pagina(self, datos):
        nuevo = NodoPagina(datos)

        if not self.cabeza:
            self.cabeza = nuevo
            self.cola = nuevo
            self.cabeza.siguiente = self.cabeza
            self.cabeza.anterior = self.cabeza
        else:
            nuevo.anterior = self.cola
            nuevo.siguiente = self.cabeza
            self.cola.siguiente = nuevo
            self.cabeza.anterior = nuevo
            self.cola = nuevo

class GestorArchivos:

    @staticmethod
    def guardar_en_json(ruta, lista):
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(lista, f, indent=4, ensure_ascii=False)

    @staticmethod
    def leer_de_json(ruta):
        if not os.path.exists(ruta):
            return []
        with open(ruta, "r", encoding="utf-8") as f:
            return json.load(f)

class Paginador:

    @staticmethod
    def construir_lista_paginada(lista, tamano=5):
        estructura = ListaCircularDoblementeEnlazada()
        for i in range(0, len(lista), tamano):
            estructura.agregar_pagina(lista[i:i+tamano])
        return estructura

class TarjetaComic(QFrame):

    clic = pyqtSignal(object)

    def __init__(self, comic):
        super().__init__()
        self.comic = comic
        self.setFixedSize(380, 200)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        self._ui()
        self._estilo()

    def _ui(self):
        layout = QHBoxLayout(self)

        self.lbl_img = QLabel("⏳")
        self.lbl_img.setFixedSize(100, 150)

        info = QVBoxLayout()

        self.lbl_titulo = QLabel(self.comic.titulo)
        self.lbl_fecha = QLabel(self.comic.fecha_lanzamiento)

        btn = QPushButton("Ver detalle")
        btn.clicked.connect(lambda: self.clic.emit(self.comic))

        info.addWidget(self.lbl_titulo)
        info.addWidget(self.lbl_fecha)
        info.addStretch()
        info.addWidget(btn)

        layout.addWidget(self.lbl_img)
        layout.addLayout(info)

    def _estilo(self):
        self.setStyleSheet(f"""
        QFrame {{
            background: {PALETA['tarjeta']};
            border: 1px solid {PALETA['borde']};
        }}
        """)

class Ventana(QMainWindow):

    def __init__(self, comics):
        super().__init__()
        self.comics = comics

        self.setWindowTitle("Catálogo")
        self.resize(900, 600)
        self.setStyleSheet(ESTILO_PRINCIPAL)

        self._ui()

    def _ui(self):
        cont = QWidget()
        self.setCentralWidget(cont)

        layout = QVBoxLayout(cont)

        self.grid = QGridLayout()

        layout.addWidget(QLabel("Catálogo de Comics"))
        layout.addWidget(DivisorRojo())
        layout.addLayout(self.grid)

        self._cargar()

    def _cargar(self):
        for i, c in enumerate(self.comics):
            t = TarjetaComic(c)
            self.grid.addWidget(t, i // 2, i % 2)


if __name__ == "__main__":

    ARCHIVO = "comics.json"

    if not os.path.exists(ARCHIVO):
        comics = [
            Comic("Spider-Man", "1", "2020", ""),
            Comic("Iron Man", "2", "2019", ""),
            Comic("Thor", "3", "2021", ""),
            Comic("Hulk", "4", "2018", "")
        ]

        datos = [c.mostrar_info() for c in comics]
        GestorArchivos.guardar_en_json(ARCHIVO, datos)

    datos = GestorArchivos.leer_de_json(ARCHIVO)

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
    v = Ventana(comics)
    v.show()
    sys.exit(app.exec())