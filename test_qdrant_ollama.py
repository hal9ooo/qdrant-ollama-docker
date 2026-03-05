import os
from dotenv import load_dotenv
import ollama
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import uuid
import time
import sys

# Load environment variables from .env file
load_dotenv()

# --- Configuration ---
# Uses the custom ports we defined in the docker-compose.yml / .env
OLLAMA_HOST = f"http://localhost:{os.getenv('OLLAMA_PORT', '12434')}"
QDRANT_HOST = "localhost"
QDRANT_PORT = int(os.getenv('QDRANT_HTTP_PORT', '7333'))
MODEL_NAME = os.getenv('OLLAMA_MODEL', 'embeddinggemma')
COLLECTION_NAME = "test_collection"

def main():
    print("=============================================")
    print("Testing Qdrant and Ollama Integration")
    print("=============================================\n")
    
    # 1. Initialize Clients
    print(f"[*] Connecting to Ollama at {OLLAMA_HOST}...")
    ollama_client = ollama.Client(host=OLLAMA_HOST)

    print(f"[*] Connecting to Qdrant at {QDRANT_HOST}:{QDRANT_PORT}...")
    try:
        qdrant_client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
        qdrant_client.get_collections() # Test connection
    except Exception as e:
        print(f"\n[!] Error connecting to Qdrant: {e}")
        print("    Ensure the container is running and port 7333 is accessible.")
        sys.exit(1)

    # 2. Check and wait for Ollama model if necessary
    print(f"\n[*] Checking if Ollama model '{MODEL_NAME}' is available...")
    models = [m.model for m in ollama_client.list().models]
    
    if any(MODEL_NAME in m for m in models):
         print(f"    Model '{MODEL_NAME}' is ready!")
    else:
         print(f"\n[!] Model '{MODEL_NAME}' not found. It might still be downloading.")
         print("    The 'ollama-init' container pulls it in the background.")
         print("    Retrying over the next 60 seconds...")
         model_ready = False
         for _ in range(12):
             time.sleep(5)
             models = [m.model for m in ollama_client.list().models]
             if any(MODEL_NAME in m for m in models):
                 print(f"    Model '{MODEL_NAME}' downloaded and ready!")
                 model_ready = True
                 break
         
         if not model_ready:
             print("\n[!] Timeout waiting for the model. Please check the 'ollama-init' container logs.")
             sys.exit(1)

    # 3. Generate embeddings for some sample texts
    texts = [
        "Il gatto dorme tranquillamente sul divano.",
        "Il cane abbaia rumorosamente correndo nel giardino.",
        "La pizza margherita di Napoli è deliziosa.",
        "Ho studiato intelligenza artificiale per sviluppare agenti autonomi."
    ]

    print(f"\n[*] Generating embeddings for {len(texts)} sample documents...")
    embeddings = []
    for text in texts:
        # embeddinggemma generates embeddings
        response = ollama_client.embeddings(model=MODEL_NAME, prompt=text)
        embeddings.append(response["embedding"])

    vector_size = len(embeddings[0])
    print(f"\n    ---> [INFO] La dimensione dei vettori (embedding_size) generati dal modello '{MODEL_NAME}' è: {vector_size} <---")

    # 4. Setup Qdrant collection
    print(f"\n[*] Setting up Qdrant collection '{COLLECTION_NAME}'...")
    if qdrant_client.collection_exists(collection_name=COLLECTION_NAME):
        print(f"    Collection '{COLLECTION_NAME}' already exists. Deleting it to start fresh...")
        qdrant_client.delete_collection(collection_name=COLLECTION_NAME)

    qdrant_client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
    )
    print("    Collection created successfully.")

    # 5. Insert data into Qdrant
    print("\n[*] Inserting vector points into Qdrant...")
    points = [
        PointStruct(
            id=str(uuid.uuid4()),
            vector=embedding,
            payload={"text": text}
        )
        for text, embedding in zip(texts, embeddings)
    ]

    qdrant_client.upsert(
        collection_name=COLLECTION_NAME,
        points=points
    )
    print(f"    Inserted {len(points)} documents successfully.")

    # 6. Perform a Vector Search
    query_text = "Voglio un animale che riposa in casa"
    print(f"\n[*] Performing semantic search for query: '{query_text}'")

    # Embed the query
    query_response = ollama_client.embeddings(model=MODEL_NAME, prompt=query_text)
    query_vector = query_response["embedding"]

    # Search in Qdrant
    search_result = qdrant_client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=2 # Get top 2 results
    ).points

    print("\n=============================================")
    print("Search Results:")
    print("=============================================")
    for i, hit in enumerate(search_result, 1):
        print(f"  {i}. Score: {hit.score:.4f} | Text: {hit.payload['text']}")
    print("=============================================\n")
    print("Test completed successfully! Both Qdrant and Ollama are working together.")

if __name__ == "__main__":
    main()
