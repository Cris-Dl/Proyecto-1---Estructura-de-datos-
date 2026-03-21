class Creador:
    def __init__(self, nombre_completo, imagen):
        self.nombre_completo = nombre_completo
        self.imagen = imagen

class Evento:
    def __init__(self, nombre, descripcion):
        self.nombre = nombre
        self.descripcion = descripcion

class Personaje:
    def __init__(self, nombre, imagen_referencia, descripcion=""):
        self.nombre = nombre
        self.imagen_referencia = imagen_referencia
        self.descripcion = descripcion
        self.creadores = []
        self.comics = []
        self.eventos = []

class Comic:
    def __init__(self, titulo, isbn, fecha_lanzamiento, imagen_referencia, descripcion=""):
        self.titulo = titulo
        self.isbn = isbn
        self.fecha_lanzamiento = fecha_lanzamiento
        self.imagen_referencia = imagen_referencia
        self.descripcion = descripcion
        self.personajes = []
        self.creadores = []

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