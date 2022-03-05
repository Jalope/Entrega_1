#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb 26 13:08:44 2022

@author: gispi
"""

from math import prod
from multiprocessing import BoundedSemaphore, Process, Lock, Semaphore, current_process
from multiprocessing import Array, Value
import random
from time import sleep

NPROD = 3  # numero de productores
vueltas = 5
#K = 3 #tamaño del buffer

def delay(factor=3):
    sleep(random.random() / factor)

'''
def positivos(lista):
    aux = True
    for elemento in lista:
        aux = aux and (elemento > 0)
    return aux

def min_positivo(lista):
    lista_positiva = [x for x in lista if x > 0]
    minimo_pos = min(lista_positiva)

    return minimo_pos
'''

def index_Array(Array):
    mini = 999999999
    indice = -5
    for i in range(NPROD):
        if Array[i] < mini and Array[i] != -1:
            mini = Array[i]
            indice = i
    return mini, indice


def lista_control(lista):
    salida = filter(lambda x: (x == -1), lista)
    lis_salida = list(salida)
    return len(lis_salida)


def add_dato(produccion, eM, pid, numero_fijo, num_anterior):
    eM.acquire()
    try:  # para garantizar que solo un proceso añade dato a la vez
        incremento = 0
        dato_nuevo = numero_fijo + random.randint(0, 20) + incremento
        while dato_nuevo < num_anterior:
            incremento += 1
            dato_nuevo = numero_fijo + random.randint(0, 20) + incremento
        produccion[pid] = dato_nuevo
        delay()
        print("Produccion actual", produccion[:], flush=True)
    finally:
        eM.release()


def get_dato(produccion, pid, eM):
    eM.acquire()
    try:
        dato, indice = index_Array(produccion)
        delay(6)
        #print("Produccion actual", produccion[:], flush=True)
    finally:
        eM.release()
    return dato


def productorM(produccion, lista_sem_v, lista_sem_nv, eM, parada):
    aux = 0  # se define fuera del buclque xq en la 1ª vuelta me da igual, y en las siguientes tendré guardada la nueva generación de cada proceso
    pid = int(current_process().name.split('_')[1])
    for i in range(vueltas):
        print(f"productor {current_process().name} produciendo")
        delay(6)
        lista_sem_v[pid].acquire()
        add_dato(produccion, eM, int(current_process().name.split('_')[1]), 100, aux)
        nueva_generacion = produccion[pid]
        lista_sem_nv[pid].release()
        print(f"productor {current_process().name} almacenando {nueva_generacion}")
        aux = nueva_generacion

    lista_sem_v[pid].acquire()
    produccion[int(current_process().name.split('_')[1])] = -1
    parada[pid] = 0
    print(f"El productor {current_process().name} ha acabado de producir")
    #print("Produccion actual", produccion[:], flush=True)
    lista_sem_nv[pid].release()


def consumidorM(produccion, lista_sem_v, lista_sem_nv, eM, parada):
    for i in range(NPROD):
        lista_sem_nv[i].acquire()
    while 1 in parada:
        _, indice = index_Array(produccion)
        dato = get_dato(produccion, int(current_process().name.split('_')[1]), eM)

        #almacenamiento de la consumición
        merge_almacen[aux.value] = dato
        aux.value += 1
        print(merge_almacen[:])

        lista_sem_v[indice].release()
        print(f"consumidor {current_process().name} desalmacenando")
        lista_sem_nv[indice].acquire()
        print(f"consumidor {current_process().name} consumiendo {dato}")
        delay()

def main():
    #merge_almacen = Array('i', NPROD * vueltas)

    #variable aux para aumentarla en el bucle en el que se almacenan los elementos consumidos
    aux = Value('i', 0)

    produccion = Array('i', NPROD)
    parada = Array('i', NPROD)

    for productor in range(NPROD):  # inicializacimos el hueco de cada productor con un -1
        produccion[productor] = -1

    for boleano in range(NPROD):  
        parada[boleano] = 1
    print("Produccion inicial", produccion[:])


    eM = Lock()  # mutex o exclusion mutua
    lista_sem_v = [Lock() for num in range(NPROD)]
    lista_sem_nv = [Semaphore(0) for num in range(NPROD)]  # 0 es porque se incializa en rojo

    lista_de_productores = [Process(target=productorM,
                                    name=f'prod_{num}',
                                    args=(produccion, lista_sem_v, lista_sem_nv, eM, parada))
                            for num in range(NPROD)]

    lista_de_consumidores = [Process(target=consumidorM,
                                     name=f'cons_1',
                                     args=(produccion, lista_sem_v, lista_sem_nv, eM, parada))]

    for productor in lista_de_productores + lista_de_consumidores:
        productor.start()

    for productor in lista_de_productores + lista_de_consumidores:
        productor.join()

    print("Produccion final", produccion[:])
    print("El proceso de producción y consumición ha acabado")
    print(merge_almacen[:])

if __name__ == '__main__':
    main()
