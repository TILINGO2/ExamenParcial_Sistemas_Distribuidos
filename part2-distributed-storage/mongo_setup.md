# Configuración de MongoDB Distribuido

##  Objetivo
Configurar un sistema de almacenamiento distribuido usando 2 instancias de MongoDB en contenedores Docker.

##  Requisitos Previos

```bash
# Verificar que Docker esté instalado
docker --version

# Verificar que Docker Compose esté instalado
docker-compose --version

# Instalar pymongo (cliente Python para MongoDB)
pip install pymongo
```

##  Pasos de Configuración

### 1. Iniciar los Contenedores

```bash
# En el directorio raíz del proyecto (donde está docker-compose.yml)
docker-compose up -d
```

**Salida esperada:**
```
Creating network "exam-sistemas-distribuidos_distributed_network" with the default driver
Creating mongodb_node1 ... done
Creating mongodb_node2 ... done
```

### 2. Verificar que los Contenedores Estén Corriendo

```bash
docker ps
```

**Deberías ver:**
```
CONTAINER ID   IMAGE       PORTS                      NAMES
abc123...      mongo:7.0   0.0.0.0:27017->27017/tcp  mongodb_node1
def456...      mongo:7.0   0.0.0.0:27018->27017/tcp  mongodb_node2
```

### 3. Verificar Conectividad de los Nodos

```bash
# Probar conexión al nodo 1
docker exec mongodb_node1 mongosh --eval "db.adminCommand('ping')"

# Probar conexión al nodo 2
docker exec mongodb_node2 mongosh --eval "db.adminCommand('ping')"
```

**Salida esperada:** `{ ok: 1 }`

##  Arquitectura del Sistema

```
┌─────────────────────────────────────────────┐
│         Aplicación Python                   │
│      (storage_system.py)                    │
└───────────────┬─────────────────────────────┘
                │
                │ Hash-based Distribution
                │
        ┌───────┴──────┐
        │              │
   ┌────▼────┐    ┌────▼────┐
   │  Nodo 1 │    │  Nodo 2 │
   │ MongoDB │    │ MongoDB │
   │ :27017  │    │ :27018  │
   └─────────┘    └─────────┘
   Container 1    Container 2
```

##  Configuración de Docker Compose

### Componentes Principales

**mongodb1:**
- Puerto: `27017` (puerto estándar de MongoDB)
- Base de datos: `distributed_db`
- Volumen: `mongodb1_data` (persistencia)
- Red: `distributed_network`

**mongodb2:**
- Puerto: `27018` (mapeado externamente para evitar conflictos)
- Base de datos: `distributed_db`
- Volumen: `mongodb2_data` (persistencia)
- Red: `distributed_network`

### Características Importantes

1. **Volúmenes Persistentes**: Los datos sobreviven al reinicio de contenedores
2. **Health Checks**: Verifican automáticamente que MongoDB esté respondiendo
3. **Red Bridge**: Permite comunicación entre contenedores
4. **Aislamiento**: Cada nodo tiene su propio almacenamiento

##  Estrategia de Distribución

### Hash-Based Sharding

```python
def _hash_to_node(self, document_id: str) -> int:
    hash_value = int(hashlib.md5(document_id.encode()).hexdigest(), 16)
    node_index = hash_value % len(self.nodes)
    return node_index
```

**¿Cómo funciona?**

1. **Hash MD5**: Convierte el ID del documento en un número grande
2. **Módulo**: Usa `% 2` para obtener 0 o 1 (número de nodo)
3. **Distribución uniforme**: MD5 garantiza distribución equitativa

**Ejemplo:**
```
doc_0001 → hash → 12345678... → % 2 → 0 (Nodo 1)
doc_0002 → hash → 87654321... → % 2 → 1 (Nodo 2)
doc_0003 → hash → 45678912... → % 2 → 1 (Nodo 2)
```

### Ventajas de Esta Estrategia

 **Distribución equitativa**: ~50% de documentos en cada nodo
 **Determinística**: El mismo ID siempre va al mismo nodo
 **Escalable**: Fácil agregar más nodos (cambiar el módulo)
 **Búsqueda optimizada**: Sabemos dónde buscar primero

##  Búsqueda Distribuida

### Proceso de Búsqueda

```
1. Calcular nodo esperado usando hash
2. Buscar en ese nodo primero (optimización)
3. Si no se encuentra, buscar en todos los demás nodos
4. Retornar resultado o None
```

**Código:**
```python
def find_document(self, document_id: str):
    # 1. Buscar en nodo esperado
    expected_node = self._hash_to_node(document_id)
    document = self.databases[expected_node]['documents'].find_one({'_id': document_id})
    
    if document:
        return document
    
    # 2. Fallback: buscar en todos
    for db in self.databases:
        document = db['documents'].find_one({'_id': document_id})
        if document:
            return document
    
    return None
```

### Complejidad

- **Mejor caso**: O(1) - encontrado en nodo esperado
- **Peor caso**: O(n) - buscar en todos los nodos
- **Caso promedio**: O(1) si la distribución funciona correctamente

##  Pruebas y Validación

### Ejecutar el Sistema

```bash
cd part2-distributed-storage
python storage_system.py
```

### Comandos Útiles

```bash
# Ver logs de los contenedores
docker-compose logs -f

# Detener los contenedores
docker-compose down

# Detener y eliminar volúmenes ( borra los datos)
docker-compose down -v

# Reiniciar un nodo específico
docker restart mongodb_node1
```

### Conectarse Manualmente a MongoDB

```bash
# Conectar al nodo 1
docker exec -it mongodb_node1 mongosh

# Conectar al nodo 2
docker exec -it mongodb_node2 mongosh
```

**Comandos útiles en mongosh:**
```javascript
// Ver bases de datos
show dbs

// Usar base de datos
use distributed_db

// Ver colecciones
show collections

// Contar documentos
db.documents.countDocuments()

// Ver primeros 5 documentos
db.documents.find().limit(5)

// Buscar documento específico
db.documents.findOne({_id: "doc_0001"})
```

##  Conceptos Demostrados

### 1. Sharding (Fragmentación)
- División de datos entre múltiples nodos
- Distribución basada en hash
- Balance de carga automático

### 2. Consistencia
- Cada documento existe en exactamente un nodo
- No hay replicación (sharding simple)
- Búsqueda garantiza encontrar el documento si existe

### 3. Escalabilidad Horizontal
- Agregar más nodos aumenta capacidad
- Cada nodo maneja una fracción de los datos
- Reduce carga individual

### 4. Tolerancia a Fallos (Limitada)
- Si un nodo falla, perdemos esos datos
- Para producción: agregar replicación
- Trade-off: simplicidad vs redundancia

##  Métricas de Rendimiento

### Distribución Esperada (100 documentos)

| Métrica | Valor Ideal | Valor Aceptable |
|---------|-------------|-----------------|
| Nodo 1 | 50 docs (50%) | 45-55 docs (45-55%) |
| Nodo 2 | 50 docs (50%) | 45-55 docs (45-55%) |
| Balance | 0% diferencia | <10% diferencia |

### Factores que Afectan la Distribución

- **Función hash**: MD5 da buena distribución
- **Número de documentos**: Más documentos = mejor balance
- **IDs secuenciales**: Pueden causar desbalance con malas funciones hash

##  Consideraciones de Seguridad

 **Esta es una configuración de desarrollo**

Para producción considera:
- Autenticación de MongoDB
- Encriptación de red (TLS)
- Firewall y reglas de red
- Backups automáticos
- Monitoreo y alertas

##  Solución de Problemas

### Problema: "Connection refused"
```bash
# Verificar que Docker esté corriendo
docker ps

# Reiniciar contenedores
docker-compose restart
```

### Problema: "pymongo not found"
```bash
pip install pymongo
```

### Problema: Puerto en uso
```bash
# Ver qué está usando el puerto
lsof -i :27017

# Cambiar puerto en docker-compose.yml
ports:
  - "27019:27017"  # Usar otro puerto
```

### Problema: Contenedor no inicia
```bash
# Ver logs detallados
docker-compose logs mongodb1

# Recrear contenedores
docker-compose down
docker-compose up -d
```

##  Referencias

- [MongoDB Docker Official Image](https://hub.docker.com/_/mongo)
- [PyMongo Documentation](https://pymongo.readthedocs.io/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [MongoDB Sharding](https://www.mongodb.com/docs/manual/sharding/)