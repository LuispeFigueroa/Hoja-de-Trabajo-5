import simpy
import random
import numpy as np
import matplotlib.pyplot as plt

# Configuración inicial
RANDOM_SEED = 83298
random.seed(RANDOM_SEED)

# Parámetros de la simulación
INTERVALOS = [10, 5, 1]  # Diferentes intervalos de llegada
NUM_PROCESOS = [25, 50, 100, 150, 200]  # Cantidades de procesos
MEMORIA_TOTAL = 100
INSTRUCCIONES_POR_CICLO = 3

tiempo_final = []

# Definición de la clase Proceso
class Proceso:
    def __init__(self, env, nombre, ram, cpu):
        self.env = env
        self.nombre = nombre
        self.ram = ram
        self.cpu = cpu
        self.instrucciones = random.randint(1, 10)
        self.memoria = random.randint(1, 10)
        self.tiempo_inicio = env.now
        env.process(self.run())