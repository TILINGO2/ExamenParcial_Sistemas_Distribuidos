import multiprocessing
import threading
import time
import random
from typing import List, Tuple

class TaskProcessor:
    def __init__(self):
        # Contador compartido entre procesos
        self.tasks_completed = multiprocessing.Value('i', 0)
        # Lock para hilos
        self.thread_lock = threading.Lock()
        # Contador para hilos
        self.thread_tasks_completed = 0
    
    def process_task(self, task_id: int, difficulty: int):
        """
        Simula procesamiento de tarea con diferente dificultad.
        La dificultad determina cuánto tiempo toma la tarea.
        """
        # Simular trabajo computacional
        processing_time = difficulty * 0.1  # 0.1 segundos por nivel de dificultad
        time.sleep(processing_time)
        
        # Simular cálculo pesado
        result = sum([i ** 2 for i in range(1000 * difficulty)])
        
        return f"Task {task_id} completed with difficulty {difficulty}, result: {result}"
    
    def process_task_with_lock(self, task_id: int, difficulty: int):
        """Procesa tarea usando hilos con lock para evitar race conditions"""
        result = self.process_task(task_id, difficulty)
        
        # CRITICAL SECTION - usando lock para evitar condiciones de carrera
        with self.thread_lock:
            self.thread_tasks_completed += 1
            print(f"[THREAD] {result} | Total completed: {self.thread_tasks_completed}")
        
        return result
    
    def process_task_with_shared_memory(self, task_id: int, difficulty: int):
        """Procesa tarea usando procesos con memoria compartida"""
        result = self.process_task(task_id, difficulty)
        
        # CRITICAL SECTION - usando multiprocessing.Value
        with self.tasks_completed.get_lock():
            self.tasks_completed.value += 1
            print(f"[PROCESS] {result} | Total completed: {self.tasks_completed.value}")
        
        return result
    
    def run_with_threads(self, tasks: List[Tuple[int, int]]) -> float:
        """
        Ejecutar tareas usando hilos.
        Returns: tiempo de ejecución
        """
        print("\n" + "="*60)
        print("EJECUTANDO CON HILOS (THREADS)")
        print("="*60)
        
        self.thread_tasks_completed = 0
        start_time = time.time()
        
        threads = []
        for task_id, difficulty in tasks:
            thread = threading.Thread(
                target=self.process_task_with_lock,
                args=(task_id, difficulty)
            )
            threads.append(thread)
            thread.start()
        
        # Esperar a que todos los hilos terminen
        for thread in threads:
            thread.join()
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        print(f"\n✅ Todas las tareas completadas con hilos")
        print(f"⏱️  Tiempo total: {execution_time:.2f} segundos")
        print(f"📊 Tareas completadas: {self.thread_tasks_completed}")
        
        return execution_time
    
    def run_with_processes(self, tasks: List[Tuple[int, int]]) -> float:
        """
        Ejecutar tareas usando procesos.
        Returns: tiempo de ejecución
        """
        print("\n" + "="*60)
        print("EJECUTANDO CON PROCESOS (PROCESSES)")
        print("="*60)
        
        self.tasks_completed.value = 0
        start_time = time.time()
        
        processes = []
        for task_id, difficulty in tasks:
            process = multiprocessing.Process(
                target=self.process_task_with_shared_memory,
                args=(task_id, difficulty)
            )
            processes.append(process)
            process.start()
        
        # Esperar a que todos los procesos terminen
        for process in processes:
            process.join()
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        print(f"\n✅ Todas las tareas completadas con procesos")
        print(f"⏱️  Tiempo total: {execution_time:.2f} segundos")
        print(f"📊 Tareas completadas: {self.tasks_completed.value}")
        
        return execution_time


def generate_tasks(num_tasks: int = 20) -> List[Tuple[int, int]]:
    """Genera tareas con dificultad aleatoria (1-5)"""
    tasks = []
    for i in range(num_tasks):
        difficulty = random.randint(1, 5)
        tasks.append((i + 1, difficulty))
    return tasks


def main():
    print("="*60)
    print("SISTEMA DE PROCESAMIENTO DISTRIBUIDO")
    print("Comparación: Procesos vs Hilos")
    print("="*60)
    
    # Generar 20 tareas aleatorias
    random.seed(42)  # Para reproducibilidad
    tasks = generate_tasks(20)
    
    print("\n📋 Tareas generadas:")
    for task_id, difficulty in tasks:
        print(f"  Task {task_id}: Dificultad {difficulty}")
    
    # Crear procesador
    processor = TaskProcessor()
    
    # Ejecutar con hilos
    thread_time = processor.run_with_threads(tasks)
    
    time.sleep(1)  # Pausa entre ejecuciones
    
    # Ejecutar con procesos
    process_time = processor.run_with_processes(tasks)
    
    # Análisis de resultados
    print("\n" + "="*60)
    print("ANÁLISIS DE RESULTADOS")
    print("="*60)
    print(f"⏱️  Tiempo con hilos:    {thread_time:.2f} segundos")
    print(f"⏱️  Tiempo con procesos: {process_time:.2f} segundos")
    print(f"📈 Diferencia:          {abs(thread_time - process_time):.2f} segundos")
    
    if thread_time < process_time:
        print(f"🏆 Los hilos fueron {process_time/thread_time:.2f}x más rápidos")
        print("💡 Razón: Menor overhead de creación y comunicación")
    else:
        print(f"🏆 Los procesos fueron {thread_time/process_time:.2f}x más rápidos")
        print("💡 Razón: Mejor aprovechamiento de múltiples CPUs")
    
    print("\n" + "="*60)
    print("CONCEPTOS APLICADOS")
    print("="*60)
    print("✅ Locks: threading.Lock() previene condiciones de carrera en hilos")
    print("✅ Memoria compartida: multiprocessing.Value para contador entre procesos")
    print("✅ Sincronización: get_lock() para acceso seguro a memoria compartida")
    print("✅ Comparación: Hilos vs Procesos para diferentes cargas de trabajo")


if __name__ == "__main__":
    main()
