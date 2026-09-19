# Mem0 MCP su Windows (nativo, llama.cpp Vulkan)

Replica lo stack mem0 MCP del PC Linux senza Ollama: gli embedding li serve un'istanza
**llama.cpp** (Vulkan) con il GGUF di EmbeddingGemma, Qdrant gira in Docker, il server MCP
è un venv Python nativo.

Layout atteso: repo clonato in `C:\mem0\qdrant-ollama-docker`, dati in `C:\mem0`.

## 0. Prerequisiti

- Python 3.12 (`py -3.12 --version`)
- Docker Desktop
- llama.cpp build Vulkan già in uso (come per gli altri modelli)
- I due tarball di migrazione dal PC Linux:
  - `qdrant-data-migration-2026-09-18.tar.gz` (memorie in Qdrant)
  - `mem0-history-2026-09-18.tar.gz` (history.db, opzionale)

## 1. Clone ed estrazione dati

```powershell
mkdir C:\mem0
cd C:\mem0
git clone -b feature/deepseek-flash https://github.com/hal9ooo/qdrant-ollama-docker.git
# porta i tarball dal PC Linux (USB/rete) in C:\mem0 e:
tar -xzf qdrant-data-migration-2026-09-18.tar.gz   # -> C:\mem0\.qdrant_data
tar -xzf mem0-history-2026-09-18.tar.gz            # -> C:\mem0\.mem0_data (opzionale)
```

## 2. Setup una tantum

```powershell
cd C:\mem0\qdrant-ollama-docker
powershell -ExecutionPolicy Bypass -File windows\setup.ps1
```

Poi modifica `windows\mem0.env` e inserisci la **DeepSeek API key reale** in `DEEPSEEK_API_KEY`.
Se ripristini history.db, imposta `MEM0_DATA_DIR=C:\mem0\.mem0_data` in `mem0.env`.

## 3. Istanza llama.cpp per le embedding (porta 8084)

Scarica un GGUF (Q8_0) da <https://huggingface.co/ggml-org/embeddinggemma-300M-GGUF> e avvia
un'istanza dedicata, come le altre:

```
llama-server -m embeddinggemma-300M-Q8_0.gguf --embeddings --port 8084 --alias embeddinggemma-300M
```

Verifica: `curl http://127.0.0.1:8084/v1/embeddings -d "{\"model\":\"embeddinggemma-300M\",\"input\":\"test\"}"`
(devono tornare 768 dimensioni).

## 4. Avvio stack

```powershell
powershell -ExecutionPolicy Bypass -File windows\start-all.ps1
```

Lo script: controlla la porta 8084, avvia/crea il container `qdrant_local`
(porte 7333/7334, volume `C:\mem0\.qdrant_data`), poi lancia `mem0\server.py`
in primo piano su `127.0.0.1:8090/mcp`.

## 5. OpenCode

Fondere lo snippet `windows\opencode.jsonc.snippet` in
`%USERPROFILE%\.config\opencode\opencode.json`.

## 6. Avvio automatico (opzionale)

```
schtasks /Create /TN "mem0-stack" /SC ONLOGON /RL LIMITED /TR "powershell.exe -ExecutionPolicy Bypass -WindowStyle Hidden -File C:\mem0\qdrant-ollama-docker\windows\start-all.ps1"
```

(L'istanza llama.cpp va avviata con il metodo già usato per le altre.)

## 7. Test

Con lo stack avviato e opencode in grado di vedere i tool `mem0_*`:

1. `search_memories` con una query sulle memorie esistenti → deve ritrovarle
2. `add_memory` con un fatto nuovo → verifica che DeepSeek estragga il fatto
   (serve la key reale in `windows\mem0.env`)
