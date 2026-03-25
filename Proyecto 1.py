import sys
import requests
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,QPushButton, QLabel, QGridLayout, QFrame, QSizePolicy)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap, QColor, QPainter, QLinearGradient, QBrush


# =========================
# 🎨 PALETA Y ESTILOS
# =========================
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

QPushButton {{
    border-radius: 6px;
}}
"""


# =========================
# 🔴 DIVISOR DECORATIVO
# =========================
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


# =========================
# 🧾 MODELO BÁSICO DE COMIC
# =========================
class Comic:
    def __init__(self, titulo, fecha, imagen):
        self.titulo = titulo
        self.fecha = fecha
        self.imagen = imagen
        self.personajes = []


# =========================
# 🧩 TARJETA VISUAL DE COMIC
# =========================
class TarjetaComic(QFrame):

    clic = pyqtSignal(object)

    def __init__(self, comic):
        super().__init__()
        self.comic = comic

        self.setFixedSize(380, 200)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        self._construir_ui()
        self._estilo_normal()

    def _construir_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)

        # Imagen
        self.lbl_imagen = QLabel("⏳")
        self.lbl_imagen.setFixedSize(100, 150)
        self.lbl_imagen.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_imagen.setStyleSheet(f"""
            background: {PALETA['superficie']};
            border-radius: 6px;
        """)

        # Info
        info = QVBoxLayout()

        self.lbl_titulo = QLabel(self.comic.titulo)
        self.lbl_titulo.setWordWrap(True)
        self.lbl_titulo.setStyleSheet("font-weight: bold;")

        self.lbl_fecha = QLabel(self.comic.fecha)
        self.lbl_fecha.setStyleSheet(f"color: {PALETA['texto_medio']};")

        self.btn = QPushButton("Ver detalle")
        self.btn.clicked.connect(self._emitir)

        info.addWidget(self.lbl_titulo)
        info.addWidget(self.lbl_fecha)
        info.addStretch()
        info.addWidget(self.btn)

        layout.addWidget(self.lbl_imagen)
        layout.addLayout(info)

    def _emitir(self):
        self.clic.emit(self.comic)

    def _estilo_normal(self):
        self.setStyleSheet(f"""
            QFrame {{
                background: {PALETA['tarjeta']};
                border: 1px solid {PALETA['borde']};
                border-radius: 8px;
            }}
        """)

    def _estilo_hover(self):
        self.setStyleSheet(f"""
            QFrame {{
                background: {PALETA['tarjeta_hover']};
                border: 1px solid {PALETA['acento']};
                border-radius: 8px;
            }}
        """)

    def enterEvent(self, event):
        self._estilo_hover()

    def leaveEvent(self, event):
        self._estilo_normal()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._emitir()


# =========================
# 🪟 VENTANA BASE (PRIMERA VERSION)
# =========================
class Ventana(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Catálogo de Comics")
        self.resize(900, 600)

        self.setStyleSheet(ESTILO_PRINCIPAL)

        self._construir_ui()

    def _construir_ui(self):
        contenedor = QWidget()
        self.setCentralWidget(contenedor)

        layout = QVBoxLayout(contenedor)

        titulo = QLabel("Catálogo")
        titulo.setStyleSheet("font-size: 24px; font-weight: bold;")

        self.grid = QGridLayout()

        layout.addWidget(titulo)
        layout.addWidget(DivisorRojo())
        layout.addLayout(self.grid)

        self._cargar_ejemplo()

    def _cargar_ejemplo(self):
        ejemplos = [
            Comic("Spider-Man #1", "2020", ""),
            Comic("Iron Man #5", "2019", ""),
            Comic("Thor #3", "2021", ""),
            Comic("Hulk #10", "2018", "")
        ]

        for i, comic in enumerate(ejemplos):
            tarjeta = TarjetaComic(comic)
            self.grid.addWidget(tarjeta, i // 2, i % 2)


# =========================
# 🚀 MAIN
# =========================
if __name__ == "__main__":
    app = QApplication(sys.argv)

    ventana = Ventana()
    ventana.show()

    sys.exit(app.exec())