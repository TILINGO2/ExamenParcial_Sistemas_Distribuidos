Descripción General
Este proyecto implementa dos sistemas distribuidos que demuestran conceptos fundamentales de computación paralela y distribuida vistos en clase:
Parte 1: Sistema de Procesamiento Distribuido (50 puntos)

Compara el rendimiento entre hilos (threads) y procesos (processes)
Implementa locks para evitar condiciones de carrera
Usa memoria compartida con multiprocessing.Value
Procesa 20 tareas con dificultad aleatoria


Software Necesario
Python 3.8 
pip3 20.0
Docker
Docker Compose 1.29
Git
Dependencia  pip3 install pymongo

Verificar Requisitos Previos
bash# Verificar Python
python3 --version
# Salida esperada: Python 3.8.0 o superior

# Verificar pip
pip3 --version
# Salida esperada: pip 20.0 o superior

# Verificar Docker
docker --version
# Salida esperada: Docker version 20.0 o superior

# Verificar Docker Compose
docker-compose --version
# Salida esperada: docker-compose version 1.29 o superior

Sofware Faltante Ubuntu
pip3 install pymongo


Instrucciones de Ejecución
Procesamiento Distribuido
Ejecutar el Sistema
1. Navegar al directorio
cd ~/exam-sistemas-distribuidos/part1-processes-threads

# 2. Activar entorno virtual (si lo usas)
source ../venv/bin/activate

# 3. Ejecutar el procesador
python3 task_processor.py

# 4. (Opcional) Guardar output en archivo
python3 task_processor.py > resultados.txt

Salida Esperada
============================================================
SISTEMA DE PROCESAMIENTO DISTRIBUIDO
Comparación: Procesos vs Hilos
============================================================

📋 Tareas generadas:
  Task 1: Dificultad 3
  Task 2: Dificultad 5
  ...

============================================================
EJECUTANDO CON HILOS (THREADS)
============================================================
[THREAD] Task 1 completed with difficulty 3, result: 2998000 | Total completed: 1
[THREAD] Task 2 completed with difficulty 5, result: 4998000 | Total completed: 2
...

✅ Todas las tareas completadas con hilos
⏱️  Tiempo total: 0.65 segundos
📊 Tareas completadas: 20

============================================================
EJECUTANDO CON PROCESOS (PROCESSES)
============================================================
[PROCESS] Task 1 completed with difficulty 3, result: 2998000 | Total completed: 1
...

✅ Todas las tareas completadas con procesos
⏱️  Tiempo total: 1.42 segundos
📊 Tareas completadas: 20

============================================================
ANÁLISIS DE RESULTADOS
============================================================
⏱️  Tiempo con hilos:    0.65 segundos
⏱️  Tiempo con procesos: 1.42 segundos
📈 Diferencia:          0.77 segundos
🏆 Los hilos fueron 2.18x más rápidos
💡 Razón: Menor overhead de creación y comunicación

¿Qué Hace Este Código?

Genera 20 tareas con dificultad aleatoria (1-5)
Ejecuta con hilos: Crea 20 threads, cada uno procesa una tarea
Ejecuta con procesos: Crea 20 procesos, cada uno procesa una tarea
Compara tiempos: Muestra qué método fue más rápido y por qué
Demuestra sincronización: Usa locks para evitar race conditions

PARTE 2: Almacenamiento Distribuido
Paso 1: Iniciar Contenedores MongoDB
 Navegar al directorio raíz
cd ~/exam-sistemas-distribuidos

# Iniciar contenedores en segundo plano
docker-compose up -d

# Verificar que estén corriendo
docker ps
Verificar Conectividad de MongoDB
bash# Probar conexión al nodo 1
docker exec mongodb_node1 mongosh --eval "db.adminCommand('ping')"
# Salida esperada: { ok: 1 }

# Probar conexión al nodo 2
docker exec mongodb_node2 mongosh --eval "db.adminCommand('ping')"
# Salida esperada: { ok: 1 }

# Ejecutar el Sistema de Almacenamiento
Navegar al directorio de parte 2
cd part2-distributed-storage


# Ejecutar el sistema
python3 storage_system.py

============================================================
SISTEMA DE ALMACENAMIENTO DISTRIBUIDO
MongoDB con 2 nodos
============================================================

🔌 Conectando a nodos MongoDB...
  ✅ Nodo 1 conectado: mongodb://localhost:27017/
  ✅ Nodo 2 conectado: mongodb://localhost:27018/

✅ Sistema inicializado con 2 nodos

🗑️  Limpiando todos los datos...
  Nodo 1: 0 documentos eliminados
  Nodo 2: 0 documentos eliminados
✅ Datos limpiados

📝 Generando 100 documentos de ejemplo...

📤 Insertando documentos en el sistema distribuido...
📝 Documento doc_0000 → Nodo 1
📝 Documento doc_0001 → Nodo 2
📝 Documento doc_0002 → Nodo 2
...

✅ 100 documentos insertados

============================================================
📊 ESTADÍSTICAS DE DISTRIBUCIÓN
============================================================

📦 Total de documentos: 100
🖥️  Número de nodos: 2

------------------------------------------------------------

Nodo 1: mongodb://localhost:27017/
  📄 Documentos: 51
  📊 Porcentaje: 51.0%
  📈 █████████████████████████

Nodo 2: mongodb://localhost:27018/
  📄 Documentos: 49
  📊 Porcentaje: 49.0%
  📈 ████████████████████████

------------------------------------------------------------

⚖️  Balance de distribución:
  ✅ Excelente (diferencia: 2.0%)
============================================================

============================================================
🔍 PRUEBA DE BÚSQUEDA DISTRIBUIDA
============================================================

🔍 Buscando documento: doc_0000
  → Buscando en nodo esperado 1...
  ✅ Encontrado en nodo 1 (como se esperaba)

  📄 Documento encontrado:
     ID: doc_0000
     Título: Documento 0
     Categoría: tecnología
     Nodo: 1

[... más búsquedas ...]

🔌 Conexiones cerradas


Resultados y Análisis
PARTE 1: Comparación Hilos vs Procesos
Resultados Típicos
Métrica,Hilos,Procesos,Ganador
Tiempo de ejecución,∼0.6 seg,∼1.4 seg,🏆 Hilos
Overhead de creación,Bajo,Alto,🏆 Hilos
Uso de memoria,Compartida,Separada,🏆 Hilos
Paralelismo real,No (GIL),Sí,🏆 Procesos
Aislamiento,No,Sí,🏆 Procesos

¿Por Qué los Hilos Fueron Más Rápidos?

Tareas I/O-bound: Las tareas simulan operaciones I/O con time.sleep()
Menor overhead: Crear un thread es ~10x más rápido que crear un proceso
Memoria compartida: Los hilos comparten memoria, no necesitan IPC
GIL no es problema: Para I/O, el GIL se libera automáticamente

¿Cuándo Usar Cada Uno?
Usar HILOS cuando:

 Operaciones I/O: lectura/escritura archivos, network, DB
 Muchas tareas pequeñas y rápidas
 Necesitas compartir mucha información
 Ejemplo: Servidor web, web scraping, cliente API

Usar PROCESOS cuando:

 Cálculos intensivos (CPU-bound)
 Necesitas paralelismo verdadero (múltiples CPUs)
 Quieres aislar fallos
 Ejemplo: Machine learning, procesamiento de imágenes, criptografía

PARTE 2: Distribución de Datos
Resultados de Distribución (100 documentos)
Nodo 1: ~50 documentos (50%)
Nodo 2: ~50 documentos (50%)
Balance: ±2% (Excelente)

Ventajas de Hash-Based Sharding:

 Distribución uniforme (~50/50)
 Determinista (mismo ID → mismo nodo siempre)
 Escalable (fácil agregar más nodos)
 Búsqueda optimizada (sabemos dónde buscar)


¿Qué hace el lock?
Solo un hilo puede entrar a la vez
Los demás esperan su turno
Garantiza operaciones atómicas

Ventajas:

 Escalabilidad horizontal (agregar más nodos)
 Cada nodo maneja menos datos
 Mejor rendimiento

 Estrategias:

Range-based: Rangos de IDs (0-499 → Nodo1, 500-999 → Nodo2)
Hash-based: Hash del ID (usado en este proyecto)
Directory-based: Tabla lookup


Conclusiones
Lecciones Aprendidas

Concurrencia es Compleja

Los locks son esenciales para evitar race conditions
Cada operación compartida necesita sincronización
El debugging concurrente es difícil


No Hay Solución Universal

Hilos vs procesos depende del tipo de tarea
I/O-bound → hilos
CPU-bound → procesos


Distribución de Datos

Hash-based sharding es simple y efectivo
Balance de carga es crucial
Trade-off: consistencia vs rendimiento


Infraestructura como Código

Docker facilita reproducibilidad
docker-compose.yml define toda la infraestructura
Fácil de escalar (agregar más nodos)



Aplicaciones en el Mundo Real
Sistemas que Usan Hilos/Procesos

Django/Flask: Servidores web (hilos + procesos)
Celery: Task queue distribuido (procesos)
Scrapy: Web scraping (async/threads)
NumPy/Pandas: Procesamiento paralelo (procesos)

Sistemas que Usan Sharding

MongoDB: Sharding automático en producción
Cassandra: Distributed NoSQL database
Redis Cluster: In-memory cache distribuido
Elasticsearch: Búsqueda distribuida
HDFS: Hadoop Distributed File System

Mejoras Futuras
Si tuviera más tiempo, implementaría:

Replicación: Cada documento en múltiples nodos (tolerancia a fallos)
Consistent Hashing: Minimizar redistribución al agregar/quitar nodos
Rebalanceo Automático: Redistribuir datos si un nodo se sobrecarga
Monitoreo: Dashboards en tiempo real (Grafana + Prometheus)
API REST: Exponer funcionalidad vía HTTP
Testing: Unit tests y integration tests
CI/CD: GitHub Actions para testing automático

Conceptos Demostrados

 Procesos vs Hilos: Implementación y comparación práctica
 Locks y Sincronización: Prevención de race conditions
 Memoria Compartida: multiprocessing.Value
 Sharding: Distribución hash-based
 Búsqueda Distribuida: Estrategia optimista + exhaustiva
 Docker: Infraestructura containerizada
 MongoDB: Base de datos NoSQL distribuida

