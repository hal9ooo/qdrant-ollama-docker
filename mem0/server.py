import json
import os

from fastmcp import FastMCP
from mem0 import Memory

OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://ollama:11434")
OLLAMA_CHAT_MODEL = os.environ.get("OLLAMA_CHAT_MODEL", "gemma4:e2b")
OLLAMA_EMBED_MODEL = os.environ.get("OLLAMA_MODEL", "embeddinggemma")
QDRANT_HOST = os.environ.get("QDRANT_HOST", "qdrant")
QDRANT_PORT = int(os.environ.get("QDRANT_PORT", "6333"))
COLLECTION_NAME = os.environ.get("COLLECTION_NAME", "mem0_memories")
DEFAULT_USER_ID = os.environ.get("MEM0_USER_ID", "opencode")

config = {
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "host": QDRANT_HOST,
            "port": QDRANT_PORT,
            "collection_name": COLLECTION_NAME,
            "embedding_model_dims": 768,
        },
    },
    "llm": {
        "provider": "ollama",
        "config": {
            "model": OLLAMA_CHAT_MODEL,
            "ollama_base_url": OLLAMA_BASE_URL,
            "temperature": 0.0,
        },
    },
    "embedder": {
        "provider": "ollama",
        "config": {
            "model": OLLAMA_EMBED_MODEL,
            "ollama_base_url": OLLAMA_BASE_URL,
            "embedding_dims": 768,
        },
    },
    "history_db_path": "/data/history.db",
}

memory = Memory.from_config(config)

mcp = FastMCP("mem0")


def _dump(result) -> str:
    return json.dumps(result, default=str)


@mcp.tool
def add_memory(
    text: str,
    user_id: str = DEFAULT_USER_ID,
    agent_id: str = "",
    run_id: str = "",
    metadata: dict | None = None,
) -> str:
    """Save a fact or preference to long-term memory for a user/agent."""
    params = {"user_id": user_id}
    if agent_id:
        params["agent_id"] = agent_id
    if run_id:
        params["run_id"] = run_id
    if metadata:
        params["metadata"] = metadata
    return _dump(memory.add(text, **params))


@mcp.tool
def search_memories(
    query: str,
    user_id: str = DEFAULT_USER_ID,
    top_k: int = 10,
    threshold: float | None = None,
) -> str:
    """Semantic search across stored memories for a user."""
    params = {"filters": {"user_id": user_id}, "top_k": top_k}
    if threshold is not None:
        params["threshold"] = threshold
    return _dump(memory.search(query, **params))


@mcp.tool
def get_memories(user_id: str = DEFAULT_USER_ID, top_k: int = 100) -> str:
    """List stored memories for a user."""
    return _dump(memory.get_all(filters={"user_id": user_id}, top_k=top_k))


@mcp.tool
def get_memory(memory_id: str) -> str:
    """Retrieve a single memory by its id."""
    return _dump(memory.get(memory_id))


@mcp.tool
def update_memory(memory_id: str, text: str) -> str:
    """Overwrite a memory's text by id."""
    return _dump(memory.update(memory_id=memory_id, data=text))


@mcp.tool
def delete_memory(memory_id: str) -> str:
    """Delete a single memory by id."""
    return _dump(memory.delete(memory_id=memory_id))


@mcp.tool
def delete_all_memories(user_id: str = DEFAULT_USER_ID) -> str:
    """Delete all memories for a user."""
    return _dump(memory.delete_all(user_id=user_id))


if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8000, path="/mcp")
