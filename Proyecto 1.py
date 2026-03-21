import json
import os

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