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


class ClienteComicVineAPI:
    IDS_MARVEL_CLASICOS = [
        # The Amazing Spider-Man
        "4000-6496", "4000-6497", "4000-6498", "4000-6499", "4000-6500",
        "4000-6501", "4000-6502", "4000-6503", "4000-6504", "4000-6505",
        # Uncanny X-Men
        "4000-6906", "4000-6907", "4000-6908", "4000-6909", "4000-6910",
        # Iron Man
        "4000-7171", "4000-7172", "4000-7173", "4000-7174", "4000-7175",
        # Thor
        "4000-8158", "4000-8159", "4000-8160", "4000-8161", "4000-8162",
        # Captain America
        "4000-6085", "4000-6086", "4000-6087", "4000-6088", "4000-6089",
        # Avengers
        "4000-6023", "4000-6024", "4000-6025", "4000-6026", "4000-6027",
        # Hulk
        "4000-7480", "4000-7481", "4000-7482", "4000-7483", "4000-7484",
        # Daredevil
        "4000-6644", "4000-6645", "4000-6646", "4000-6647", "4000-6648",
        # Fantastic Four
        "4000-6831", "4000-6832", "4000-6833", "4000-6834", "4000-6835",
        # Silver Surfer
        "4000-9092", "4000-9093", "4000-9094", "4000-9095", "4000-9096",
    ]

    def __init__(self, clave_api):
        self.clave_api    = clave_api
        self.encabezados  = {"User-Agent": "MundoComicApp/1.0"}
        self.sesion       = requests.Session()
        self.sesion.headers.update(self.encabezados)

    def _obtener_issue(self, id_completo):
        url = f"https://comicvine.gamespot.com/api/issue/{id_completo}/"
        parametros = {
            "api_key":  self.clave_api,
            "format":   "json",
        }
        try:
            respuesta = self.sesion.get(url, params=parametros, timeout=15)
            if respuesta.status_code == 200:
                datos = respuesta.json()
                if datos.get("status_code") == 1:
                    return datos.get("results")
        except Exception as error:
            print(f"  Error obteniendo {id_completo}: {error}")
        return None

    def obtener_comics(self):
        import time
        from concurrent.futures import ThreadPoolExecutor, as_completed

        print("Descargando cómics Marvel clásicos con datos completos...")
        resultados = []

        def _descargar(id_completo):
            issue = self._obtener_issue(id_completo)
            time.sleep(0.25)
            return issue

        with ThreadPoolExecutor(max_workers=4) as ejecutor:
            futuros = {ejecutor.submit(_descargar, id_c): id_c
                       for id_c in self.IDS_MARVEL_CLASICOS}
            for i, futuro in enumerate(as_completed(futuros), 1):
                issue = futuro.result()
                if issue:
                    resultados.append(issue)
                print(f"  {i}/{len(self.IDS_MARVEL_CLASICOS)} descargados...", end="\r")

        print(f"\n{len(resultados)} cómics obtenidos.")
        return resultados

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
        contenedor_principal.addWidget(self._construir_barra_filtros())
        contenedor_principal.addWidget(DivisorRojo(1))

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
        contenedor_principal.addWidget(area_scroll, 1)

        contenedor_principal.addWidget(DivisorRojo(1))
        contenedor_principal.addWidget(self._construir_pie())

        self._actualizar_vista()

    def _construir_encabezado(self):
        encabezado = QWidget()
        encabezado.setFixedHeight(100)
        encabezado.setStyleSheet(f"""
            background: qlineargradient(
                x1:0, y1:0, x2:1, y2:0,
                stop:0 #1a0000, stop:0.5 #0d0d0d, stop:1 #1a0000
            );
        """)
        diseno = QHBoxLayout(encabezado)
        diseno.setContentsMargins(32, 0, 32, 0)

        col_logo = QVBoxLayout()
        col_logo.setSpacing(2)
        lbl_marca = QLabel("MUNDO MARVEL")
        lbl_marca.setStyleSheet(f"""
            color: {PALETA['acento']};
            font-size: 36px;
            font-weight: 900;
            letter-spacing: 6px;
            font-family: 'Impact', 'Arial Black', sans-serif;
        """)
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
        self.combo_orden.addItems([
            "Más recientes primero",
            "Más antiguos primero",
            "Título  A → Z",
            "Título  Z → A",
        ])
        self.combo_orden.currentIndexChanged.connect(self._al_cambiar_filtro)

        btn_limpiar = QPushButton("✕  Limpiar")
        btn_limpiar.setFixedHeight(36)
        btn_limpiar.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_limpiar.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {PALETA['texto_bajo']};
                border: 1px solid {PALETA['borde']};
                border-radius: 6px;
                padding: 0 14px;
                font-size: 12px;
            }}
            QPushButton:hover {{
                color: {PALETA['texto_alto']};
                border-color: {PALETA['texto_medio']};
            }}
        """)
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
        boton.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {PALETA['texto_alto']};
                border: 1px solid {PALETA['borde']};
                border-radius: 8px;
                padding: 0 20px;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background: {PALETA['acento']};
                border-color: {PALETA['acento']};
                color: white;
            }}
            QPushButton:disabled {{
                color: {PALETA['texto_bajo']};
                border-color: {PALETA['borde']};
                background: transparent;
            }}
        """)

    def _al_cambiar_filtro(self):
        texto = self.campo_titulo.text().lower().strip()
        anio = self.campo_anio.text().strip()
        orden = self.combo_orden.currentText()

        lista_filtrada = [
            c for c in self.comics_totales
            if (texto in c.titulo.lower())
               and (anio in (c.fecha_lanzamiento or "") if anio else True)
        ]

        if orden == "Título  A → Z":
            lista_filtrada.sort(key=lambda x: x.titulo.lower())
        elif orden == "Título  Z → A":
            lista_filtrada.sort(key=lambda x: x.titulo.lower(), reverse=True)
        elif orden == "Más recientes primero":
            lista_filtrada.sort(key=lambda x: x.fecha_lanzamiento or "", reverse=True)
        elif orden == "Más antiguos primero":
            lista_filtrada.sort(key=lambda x: x.fecha_lanzamiento or "")

        self.comics_filtrados = lista_filtrada
        self.indice_pagina = 0
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

        inicio = self.indice_pagina * self.tamano_pagina
        comics = self.comics_filtrados[inicio: inicio + self.tamano_pagina]
        total = len(self.comics_filtrados)
        total_p = max(1, (total + self.tamano_pagina - 1) // self.tamano_pagina)

        self.lbl_resultados.setText(
            f"{total} resultado{'s' if total != 1 else ''} encontrado{'s' if total != 1 else ''}")
        self.lbl_pagina.setText(f"{self.indice_pagina + 1}  /  {total_p}")
        self.btn_anterior.setEnabled(self.indice_pagina > 0)
        self.btn_siguiente.setEnabled(self.indice_pagina < total_p - 1)

        if not comics:
            lbl_vacio = QLabel("No se encontraron cómics con esos filtros.")
            lbl_vacio.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl_vacio.setStyleSheet(f"color: {PALETA['texto_bajo']}; font-size: 16px; padding: 60px;")
            self.grid_comics.addWidget(lbl_vacio, 0, 0, 1, 2)
            return
        for i, comic in enumerate(comics):
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
        if self.indice_pagina > 0:
            self.indice_pagina -= 1
            self._actualizar_vista()

    def _ir_siguiente(self):
        total_paginas = (len(self.comics_filtrados) + self.tamano_pagina - 1) // self.tamano_pagina
        if self.indice_pagina < total_paginas - 1:
            self.indice_pagina += 1
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
        cabecera.setStyleSheet(f"""
            background: qlineargradient(
                x1:0, y1:0, x2:1, y2:0,
                stop:0 #200000, stop:1 {PALETA['fondo']}
            );
        """)
        diseno_cabecera = QHBoxLayout(cabecera)
        diseno_cabecera.setContentsMargins(28, 0, 28, 0)

        barra_acento = QWidget()
        barra_acento.setFixedSize(4, 48)
        barra_acento.setStyleSheet(f"background: {PALETA['acento']}; border-radius: 2px;")

        lbl_titulo_modal = QLabel(comic.titulo)
        lbl_titulo_modal.setWordWrap(True)
        lbl_titulo_modal.setStyleSheet(f"""
            color: {PALETA['texto_alto']};
            font-size: 20px;
            font-weight: bold;
            padding-left: 14px;
        """)
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
        lbl_imagen_det.setStyleSheet(f"""
            background: {PALETA['superficie']};
            border-radius: 8px;
            color: {PALETA['texto_bajo']};
            font-size: 20px;
        """)
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
                        pixmap = QPixmap.fromImage(imagen).scaled(
                            160, 240,
                            Qt.AspectRatioMode.KeepAspectRatio,
                            Qt.TransformationMode.SmoothTransformation
                        )
                        try:
                            lbl.setPixmap(pixmap)
                            lbl.setStyleSheet("border-radius: 8px; background: transparent;")
                        except RuntimeError:
                            pass
                except Exception:
                    pass

            hilo_det = threading.Thread(
                target=_cargar_img_detalle,
                args=(comic.imagen_referencia, lbl_imagen_det),
                daemon=True
            )
            hilo_det.start()

        col_texto = QVBoxLayout()
        col_texto.setSpacing(14)

        def _crear_seccion(titulo_seccion, contenido_texto):
            seccion = QVBoxLayout()
            seccion.setSpacing(4)
            lbl_tit = QLabel(titulo_seccion.upper())
            lbl_tit.setStyleSheet(f"""
                color: {PALETA['acento']};
                font-size: 10px;
                font-weight: bold;
                letter-spacing: 2px;
            """)
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

        texto_personajes = (
            ", ".join(_obtener_nombre(p) for p in lista_personajes) if lista_personajes else "No disponible")
        texto_creadores = (
            ", ".join(_obtener_nombre(c) for c in lista_creadores) if lista_creadores else "No disponible")

        col_texto.addLayout(_crear_seccion("Personajes", texto_personajes))
        col_texto.addLayout(_crear_seccion("Creadores", texto_creadores))

        lbl_sin_titulo = QLabel("SINOPSIS")
        lbl_sin_titulo.setStyleSheet(f"""
            color: {PALETA['acento']};
            font-size: 10px;
            font-weight: bold;
            letter-spacing: 2px;
        """)
        visor_descripcion = QTextBrowser()
        visor_descripcion.setStyleSheet(f"""
            background: {PALETA['superficie']};
            border: 1px solid {PALETA['borde']};
            border-radius: 8px;
            color: {PALETA['texto_medio']};
            font-size: 13px;
            padding: 12px;
        """)
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
        btn_cerrar.setStyleSheet(f"""
            QPushButton {{
                background: {PALETA['acento']};
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background: #c42c2c;
            }}
        """)
        btn_cerrar.clicked.connect(dialogo.accept)
        diseno_pie.addStretch()
        diseno_pie.addWidget(btn_cerrar)
        diseno_raiz.addWidget(pie_modal)

        dialogo.exec()
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