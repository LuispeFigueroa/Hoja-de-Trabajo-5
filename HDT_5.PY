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

    def run(self):
        # Estado NEW: esperando RAM
        with self.ram.get(self.memoria) as req:
            yield req
            # Estado READY: esperando CPU
            with self.cpu.request() as req_cpu:
                yield req_cpu
                while self.instrucciones > 0:
                    yield self.env.timeout(1)  # Ejecutando
                    self.instrucciones -= INSTRUCCIONES_POR_CICLO
                    if self.instrucciones > 0 and random.randint(1, 2) == 1:
                        yield self.env.timeout(1)  # Espera de I/O
                self.ram.put(self.memoria)  # Libera memoria
                tiempo_final.append(self.env.now - self.tiempo_inicio)

# Generador de procesos
def generar_procesos(env, ram, cpu, intervalo):
    proceso_id = 0
    while True:
        yield env.timeout(random.expovariate(1.0 / intervalo))
        proceso_id += 1
        Proceso(env, f'Proceso-{proceso_id}', ram, cpu)

# Función principal de simulación
def correr_simulacion(num_procesos, intervalo):
    global tiempo_final
    tiempo_final = []
    env = simpy.Environment()
    ram = simpy.Container(env, init=MEMORIA_TOTAL, capacity=MEMORIA_TOTAL)
    cpu = simpy.Resource(env, capacity=1)
    env.process(generar_procesos(env, ram, cpu, intervalo))
    env.run(until=1000)
    return np.mean(tiempo_final), np.std(tiempo_final)

# Ejecutar simulaciones y graficar resultados
resultados = {}
for intervalo in INTERVALOS:
    tiempos_promedio = []
    desviaciones = []
    for n in NUM_PROCESOS:
        promedio, desviacion = correr_simulacion(n, intervalo)
        tiempos_promedio.append(promedio)
        desviaciones.append(desviacion)
    resultados[intervalo] = (NUM_PROCESOS, tiempos_promedio, desviaciones)

# Graficar resultados con mejoras visuales
plt.figure(figsize=(10, 6))
colores = ['b', 'g', 'r']
marcadores = ['o', 's', 'D']

for i, (intervalo, datos) in enumerate(resultados.items()):
    plt.errorbar(
        datos[0], datos[1], yerr=datos[2], 
        label=f'Intervalo {intervalo}', 
        fmt=marcadores[i], color=colores[i], 
        capsize=5, capthick=2, markersize=6, linewidth=2
    )

plt.xlabel("Número de Procesos", fontsize=14)
plt.ylabel("Tiempo Promedio", fontsize=14)
plt.title("Impacto del Intervalo de Llegada en el Tiempo Promedio de Procesos", fontsize=16)
plt.legend(fontsize=12)
plt.grid(True, linestyle="--", alpha=0.7)
plt.show()