"""
embeddings.py — Memoria semántica con ChromaDB y sentence-transformers

Representaciones numéricas (vectores) de textos. Dos textos con
significado similar tendrán vectores parecidos, aunque usen palabras distintas.

Ejemplo:
- "Me gusta el fútbol" y "Soy fanático del balompié" → vectores muy cercanos
- "Me gusta el fútbol" y "Hoy hace calor" → vectores lejanos

Esto permite buscar mensajes relevantes por SIGNIFICADO, no por palabras exactas.

ChromaDB es una base de datos especializada en almacenar y buscar vectores (embeddings).
"""

import chromadb
from sentence_transformers import SentenceTransformer
import os

# Configuración

# Ruta donde se guarda la base de datos vectorial
CHROMA_PATH = os.path.join(os.path.dirname(__file__), "..", "chroma_db")

# Modelo de embeddings
# 'all-MiniLM-L6-v2' es pequeño, rápido y muy bueno para español e inglés
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# Variables globales
_chroma_client = None
_embedding_model = None


def get_chroma_client():
    """
    Devuelve el cliente de ChromaDB.
    Lo crea solo la primera vez (patrón Singleton).
    """
    global _chroma_client
    if _chroma_client is None:
        _chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
    return _chroma_client


def get_embedding_model():
    """
    Devuelve el modelo de embeddings.
    Lo carga solo la primera vez (tarda unos segundos la primera vez).
    """
    global _embedding_model
    if _embedding_model is None:
        print("⏳ Cargando modelo de embeddings...")
        _embedding_model = SentenceTransformer(EMBEDDING_MODEL)
        print("✅ Modelo de embeddings listo")
    return _embedding_model


def get_collection(session_id: str):
    """
    Devuelve la colección de ChromaDB para un usuario concreto.
    Cada usuario tiene su propia colección de vectores.
    """
    client = get_chroma_client()
    # El nombre de la colección no puede tener ciertos caracteres
    collection_name = f"user_{session_id.replace('-', '_')}"
    return client.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"}  # Usamos similitud coseno
    )


def store_message(session_id: str, message_id: str, text: str, role: str):
    """
    Guarda un mensaje en ChromaDB como vector.

    Args:
        session_id:  ID del usuario
        message_id:  ID único del mensaje
        text:        Texto del mensaje
        role:        "user" o "assistant"
    """
    try:
        model = get_embedding_model()
        collection = get_collection(session_id)

        # Convertir el texto a vector
        embedding = model.encode(text).tolist()

        # Guardar en ChromaDB
        collection.add(
            ids=[message_id],
            embeddings=[embedding],
            documents=[text],
            metadatas=[{"role": role, "session_id": session_id}]
        )
    except Exception as e:
        print(f"Error guardando embedding: {e}")


def search_relevant_messages(session_id: str, query: str, n_results: int = 3) -> list:
    """
    Busca los mensajes más relevantes para una consulta dada.

    Por ejemplo, si el usuario pregunta "¿recuerdas mi equipo favorito?",
    esta función buscará mensajes anteriores que hablen de equipos de fútbol.

    Args:
        session_id: ID del usuario
        query:      Texto de la consulta
        n_results:  Cuántos mensajes relevantes devolver

    Returns:
        Lista de textos relevantes ordenados por similitud
    """
    try:
        model = get_embedding_model()
        collection = get_collection(session_id)

        # Comprobar que hay documentos en la colección
        if collection.count() == 0:
            return []

        # Convertir la consulta a vector y buscar similares
        query_embedding = model.encode(query).tolist()

        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=min(n_results, collection.count()),
            where={"role": "user"}  # Solo buscamos en mensajes del usuario
        )

        return results["documents"][0] if results["documents"] else []

    except Exception as e:
        print(f"Error buscando embeddings: {e}")
        return []


def delete_user_collection(session_id: str):
    """
    Borra todos los vectores de un usuario.
    Se llama cuando el usuario borra su historial.
    """
    try:
        client = get_chroma_client()
        collection_name = f"user_{session_id.replace('-', '_')}"
        client.delete_collection(collection_name)
    except Exception as e:
        print(f"Error borrando colección: {e}")