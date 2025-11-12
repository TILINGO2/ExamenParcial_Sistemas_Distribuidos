from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import hashlib
import time
from typing import Dict, List, Optional, Any
import random
from datetime import datetime

class DistributedStorage:
    def __init__(self, nodes: List[str] = None):
        """
        Inicializa el sistema de almacenamiento distribuido.
        
        Args:
            nodes: Lista de URIs de los nodos MongoDB
        """
        if nodes is None:
            nodes = [
                "mongodb://localhost:27017/",
                "mongodb://localhost:27018/"
            ]
        
        self.nodes = []
        self.clients = []
        self.databases = []
        
        print("🔌 Conectando a nodos MongoDB...")
        for i, node_uri in enumerate(nodes):
            try:
                client = MongoClient(node_uri, serverSelectionTimeoutMS=5000)
                # Verificar conexión
                client.admin.command('ping')
                
                db = client['distributed_db']
                self.clients.append(client)
                self.databases.append(db)
                self.nodes.append(node_uri)
                
                print(f"  ✅ Nodo {i+1} conectado: {node_uri}")
            except ConnectionFailure as e:
                print(f"  ❌ Error conectando a {node_uri}: {e}")
        
        if not self.nodes:
            raise ConnectionError("No se pudo conectar a ningún nodo MongoDB")
        
        print(f"\n✅ Sistema inicializado con {len(self.nodes)} nodos\n")
    
    def _hash_to_node(self, document_id: str) -> int:
        """
        Determina a qué nodo va un documento usando hash consistente.
        
        Args:
            document_id: ID del documento
            
        Returns:
            Índice del nodo (0 o 1)
        """
        # Usar hash MD5 para distribución uniforme
        hash_value = int(hashlib.md5(document_id.encode()).hexdigest(), 16)
        node_index = hash_value % len(self.nodes)
        return node_index
    
    def insert_document(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Inserta documento distribuyéndolo entre nodos según hash del ID.
        
        Args:
            data: Diccionario con los datos del documento
            
        Returns:
            Documento insertado con metadata
        """
        # Generar ID único si no existe
        if '_id' not in data:
            data['_id'] = f"doc_{int(time.time() * 1000000)}"
        
        document_id = str(data['_id'])
        
        # Determinar nodo usando hash
        node_index = self._hash_to_node(document_id)
        
        # Agregar metadata
        data['_node'] = node_index
        data['_inserted_at'] = datetime.now()
        
        # Insertar en el nodo correspondiente
        collection = self.databases[node_index]['documents']
        result = collection.insert_one(data)
        
        print(f"📝 Documento {document_id} → Nodo {node_index + 1}")
        
        return {
            'document_id': document_id,
            'node': node_index,
            'inserted': result.acknowledged
        }
    
    def find_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        """
        Busca documento en todos los nodos (búsqueda distribuida).
        
        Args:
            document_id: ID del documento a buscar
            
        Returns:
            Documento encontrado o None
        """
        print(f"\n🔍 Buscando documento: {document_id}")
        
        # Primero intentar con el nodo esperado (optimización)
        expected_node = self._hash_to_node(document_id)
        print(f"  → Buscando en nodo esperado {expected_node + 1}...")
        
        collection = self.databases[expected_node]['documents']
        document = collection.find_one({'_id': document_id})
        
        if document:
            print(f"  ✅ Encontrado en nodo {expected_node + 1} (como se esperaba)")
            return document
        
        # Si no está en el nodo esperado, buscar en todos (fallback)
        print(f"  ⚠️  No encontrado en nodo esperado, buscando en todos...")
        
        for i, db in enumerate(self.databases):
            if i == expected_node:
                continue  # Ya lo buscamos
            
            collection = db['documents']
            document = collection.find_one({'_id': document_id})
            
            if document:
                print(f"  ✅ Encontrado en nodo {i + 1}")
                return document
        
        print(f"  ❌ Documento no encontrado en ningún nodo")
        return None
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas de distribución de datos.
        
        Returns:
            Diccionario con estadísticas de cada nodo
        """
        print("\n" + "="*60)
        print("📊 ESTADÍSTICAS DE DISTRIBUCIÓN")
        print("="*60)
        
        stats = {
            'nodes': [],
            'total_documents': 0,
            'distribution': {}
        }
        
        for i, db in enumerate(self.databases):
            collection = db['documents']
            count = collection.count_documents({})
            
            node_stats = {
                'node_id': i,
                'node_uri': self.nodes[i],
                'document_count': count,
                'percentage': 0
            }
            
            stats['nodes'].append(node_stats)
            stats['total_documents'] += count
        
        # Calcular porcentajes
        if stats['total_documents'] > 0:
            for node_stat in stats['nodes']:
                percentage = (node_stat['document_count'] / stats['total_documents']) * 100
                node_stat['percentage'] = round(percentage, 2)
        
        # Imprimir estadísticas
        print(f"\n📦 Total de documentos: {stats['total_documents']}")
        print(f"🖥️  Número de nodos: {len(self.nodes)}")
        print("\n" + "-"*60)
        
        for node_stat in stats['nodes']:
            print(f"\nNodo {node_stat['node_id'] + 1}: {node_stat['node_uri']}")
            print(f"  📄 Documentos: {node_stat['document_count']}")
            print(f"  📊 Porcentaje: {node_stat['percentage']}%")
            
            # Barra visual
            bar_length = int(node_stat['percentage'] / 2)  # Escala a 50 caracteres max
            bar = "█" * bar_length
            print(f"  📈 {bar}")
        
        # Análisis de balance
        if stats['total_documents'] > 0:
            percentages = [n['percentage'] for n in stats['nodes']]
            balance = max(percentages) - min(percentages)
            
            print("\n" + "-"*60)
            print(f"\n⚖️  Balance de distribución:")
            if balance < 10:
                print(f"  ✅ Excelente (diferencia: {balance:.2f}%)")
            elif balance < 20:
                print(f"  ✓ Bueno (diferencia: {balance:.2f}%)")
            else:
                print(f"  ⚠️  Puede mejorar (diferencia: {balance:.2f}%)")
        
        print("="*60 + "\n")
        
        return stats
    
    def clear_all_data(self):
        """Limpia todos los datos de todos los nodos (útil para testing)"""
        print("\n🗑️  Limpiando todos los datos...")
        for i, db in enumerate(self.databases):
            collection = db['documents']
            result = collection.delete_many({})
            print(f"  Nodo {i + 1}: {result.deleted_count} documentos eliminados")
        print("✅ Datos limpiados\n")
    
    def close(self):
        """Cierra todas las conexiones"""
        for client in self.clients:
            client.close()
        print("🔌 Conexiones cerradas")


def generate_sample_documents(count: int = 100) -> List[Dict[str, Any]]:
    """Genera documentos de ejemplo para testing"""
    categories = ['tecnología', 'ciencia', 'arte', 'deportes', 'música']
    documents = []
    
    for i in range(count):
        doc = {
            '_id': f'doc_{i:04d}',
            'title': f'Documento {i}',
            'category': random.choice(categories),
            'value': random.randint(1, 1000),
            'description': f'Este es el documento número {i} de prueba',
            'created': datetime.now()
        }
        documents.append(doc)
    
    return documents


def main():
    """Función principal para demostrar el sistema"""
    print("="*60)
    print("SISTEMA DE ALMACENAMIENTO DISTRIBUIDO")
    print("MongoDB con 2 nodos")
    print("="*60 + "\n")
    
    try:
        # Inicializar sistema
        storage = DistributedStorage()
        
        # Limpiar datos previos
        storage.clear_all_data()
        
        # Generar y insertar 100 documentos
        print("📝 Generando 100 documentos de ejemplo...")
        documents = generate_sample_documents(100)
        
        print("\n📤 Insertando documentos en el sistema distribuido...")
        for doc in documents:
            storage.insert_document(doc)
        
        print(f"\n✅ {len(documents)} documentos insertados\n")
        
        # Mostrar estadísticas
        stats = storage.get_stats()
        
        # Probar búsqueda distribuida
        print("\n" + "="*60)
        print("🔍 PRUEBA DE BÚSQUEDA DISTRIBUIDA")
        print("="*60)
        
        # Buscar algunos documentos
        test_ids = ['doc_0000', 'doc_0050', 'doc_0099', 'doc_9999']
        
        for doc_id in test_ids:
            result = storage.find_document(doc_id)
            if result:
                print(f"\n  📄 Documento encontrado:")
                print(f"     ID: {result['_id']}")
                print(f"     Título: {result['title']}")
                print(f"     Categoría: {result['category']}")
                print(f"     Nodo: {result['_node'] + 1}")
        
        # Cerrar conexiones
        storage.close()
        
    except ConnectionError as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Asegúrate de que Docker esté ejecutando los contenedores:")
        print("   docker-compose up -d")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
