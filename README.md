# Qdrant + Ollama Local Docker Setup

Questo repository fornisce un ambiente Docker Compose pronto all'uso per eseguire localmente **Qdrant** (Vector Database) e **Ollama** (Local LLM Server).

La particolarità di questo setup è che scarica automaticamente il modello di embedding (`embeddinggemma` di default) non appena i container vengono avviati ed espone servizi in modo sicuro sulle porte personalizzabili per non entrare in conflitto con altri servizi standard.

## 🚀 Requisiti

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

## 🛠️ Installazione e Avvio Rapido

1.  **Clona il repository (o scarica i file):**

    ```bash
    git clone https://github.com/TUO_NOME_UTENTE/NOME_REPO.git
    cd NOME_REPO
    ```

2.  **Configura l'ambiente:**
    Copia il file di esempio `.env.example` in un nuovo file chiamato `.env`.

    ```bash
    cp .env.example .env
    ```

    Puoi modificare questo file per cambiare le porte predefinite e il modello di embedding.

3.  **Avvia i container:**
    ```bash
    docker compose up -d
    ```

> 💡 **Nota:** Al primo avvio, il container di inizializzazione (`ollama-init`) impiegherà alcuni minuti (in base alla tua connessione internet) per scaricare il modello da Ollama. Puoi controllare lo stato del download con `docker logs -f ollama_model_pull`.

## 🤖 Integrazione con AI IDE (Roo Code / Kilo Code)

Questo setup risulta particolarmente utile per indicizzare un'intera **Codebase** da usare poi come contesto tramite RAG (Retrieval-Augmented Generation) in Assistenti AI integrati negli IDE (come **[Roo Code](https://github.com/RooVetgit/Roo-Code)**, **Kilo Code**, o **Cline**).

Se stai configurando l'indicizzazione della tua codebase su un editor VSCode-like, inserisci i seguenti URL nelle rispettive impostazioni quando richiesto:

- **Ollama (Server Embedding)**: `http://localhost:12434` (o via IP) con il modello configurato (es: `embeddinggemma`).
- **Qdrant (Vector DB)**: `http://localhost:7333` (utilizzato dal plugin per salvare e recuperare al volo enormi porzioni rilevanti del tuo codice).

## 🔌 Endpoint Disponibili

I servizi sono esposti sull'indirizzo `0.0.0.0`, il che significa che sono accessibili sia da `localhost` sia dagli altri PC della stessa rete (sostituendo localhost con l'indirizzo IP del PC host).

Endpoint di default (configurabili nel file `.env`):

- **Ollama (REST API):** `http://localhost:12434`
- **Qdrant (REST API & Dashboard UI):** `http://localhost:7333`
- **Qdrant (gRPC API):** `localhost:7334`

## 🧪 Testare l'ambiente (Script Python)

Abbiamo incluso un semplice script in Python (`test_qdrant_ollama.py`) per dimostrare l'integrazione tra Qdrant e Ollama eseguendo l'embedding tramite LLM e una query semantica (Vector Search).

1. Crea e attiva un ambiente virtuale (Virtual Environment):

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. Installa i pacchetti necessari:

   ```bash
   pip install qdrant-client ollama python-dotenv
   ```

3. Esegui lo script:
   ```bash
   python test_qdrant_ollama.py
   ```

## 🧹 Arrestare e Pulire

Per fermare l'esecuzione dei servizi mantenendo i dati salvati:

```bash
docker compose down
```

### 💾 Storage Persistente e Reset

Per garantire la massima compatibilità e persistenza (specialmente per il Codebase Indexing con Roo Code), tutti i database e i modelli testuali **vengono salvati automaticamente in due cartelle locali** all'interno di questo repository:

- `./.qdrant_data`
- `./.ollama_data`

Per **cancellare tutti i dati salvati** (i modelli scaricati su Ollama e le collezioni presenti su Qdrant) e far ripartire l'ambiente completamente da zero, ti basterà fermare i container ed eliminare fisicamente quelle due cartelle:

```bash
docker compose down
sudo rm -rf .qdrant_data .ollama_data
```

## 📝 Licenza

Questo progetto è distribuito con licenza **MIT**. Consulta il file `LICENSE` per ulteriori informazioni.
