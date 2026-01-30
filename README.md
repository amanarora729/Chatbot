# Humanli.ai - AI/ML Engineer Assignment
## Website-Based Chatbot Using Embeddings

### 1. Overview
This project is an AI-powered retrieval and question-answering system. It accepts a website URL, crawls its content, creates embeddings, and stores them in a vector database. Users can then ask natural language questions grounded strictly in the website's content.

### 2. Architecture
The system is built with a decoupled client-server architecture:
- **Backend (FastAPI)**: Handles core logic including crawling, embedding, vector storage, and the RAG (Retrieval-Augmented Generation) pipeline.
- **Frontend (Streamlit)**: Provides an interactive UI for users to input URLs and chat with the bot.

**Key Components:**
- **Crawler Service**: Fetches HTML, cleans irrelevant tags (ads, nav, footer), and chunks text. Robustly handles errors (404, invalid URLs).
- **Knowledge Service**: Manages `LanceDB` storage and `Agno` knowledge base integration.
- **Agent**: An `Agno` Agent configured with `Gemini` to answer questions based *only* on retrieved context.
- **Memory**: Persistent short-term session memory using `SQLite` (`agno.db.sqlite.SqliteDb`).

### 3. Frameworks & Technologies
- **Agno (formerly Phidata)**: Chosen for its robust Agentic RAG capabilities and easy integration with Vector DBs and LLMs.
- **FastAPI**: For a high-performance, asynchronous REST API.
- **Streamlit**: For rapid development of a user-friendly data application.
- **LanceDB**: A serverless, embedded vector database.
- **Google Gemini**: State-of-the-art multimodal LLM.
- **SQLite**: Lightweight, file-based database for session persistence.

### 4. Design Decisions

#### LLM Model: Google Gemini (via `gemini-2.5-flash`)
- **Reasoning**: Gemini 1.5 Flash offers an excellent balance of speed and reasoning capability, crucial for a responsive chatbot. It has a large context window which helps in processing retrieved chunks effectively.

#### Vector Database: LanceDB
- **Reasoning**: LanceDB is an embedded, serverless vector database that stores data in standard file formats (Lance). It does not require a separate Docker container or cloud instance, making the setup extremely simple and portable for this assignment.

#### Embedding Strategy
- **Model**: `text-embedding-004` (Google Gemini Embeddings).
- **Chunking**: Content is split into 1000-character chunks with 200-character overlap. This ensures that context (like sentence boundaries) is preserved across chunks, improving retrieval accuracy.

#### Session Memory
- **Implementation**: `agno.db.sqlite.SqliteDb`
- **Reasoning**: SQLite provides persistence across server restarts without the overhead of setting up a Redis server. It fits perfectly with the "embedded" philosophy of this project (alongside LanceDB).

### 5. Setup & Run Instructions

**Prerequisites:**
- Python 3.10+
- Google API Key (Get one from AI Studio)

**Steps:**
1.  **Clone the repository:**
    ```bash
    git clone <repo-url>
    cd chatbot_project
    ```

2.  **Create Virtual Environment (recommended with uv):**
    ```bash
    uv venv
    .venv\Scripts\activate  # Windows
    # source .venv/bin/activate  # Mac/Linux
    uv pip install -r requirements.txt
    # Install additional required packages
    uv pip install google-genai tantivy pylance sqlalchemy
    ```

3.  **Configure Environment:**
    - Create a `.env` file in the root directory.
    - Add your Google API Key:
      ```
      GOOGLE_API_KEY=AIzaSy...
      ```

4.  **Run the Application:**

    You need to run the backend and frontend in separate terminals.

    **Terminal 1 (Backend):**
    ```bash
    # Ensure venv is activated
    python run_backend.py
    ```
    - API will run at `http://localhost:8000`

    **Terminal 2 (Frontend):**
    ```bash
    # Ensure venv is activated
    python run_frontend.py
    ```
    - Streamlit UI will open at `http://localhost:8501`

### 6. Assumptions & Limitations
- **Single Page Crawl**: To ensure quality and avoid infinite loops in a short timeframe, the crawler currently processes only the provided URL, not the entire domain.
- **Cleanliness**: Heuristic-based HTML cleaning (removing `<nav>`, `<footer>`) is effective but may miss edge cases on complex dynamic JS-heavy sites (SPA).

### 7. Future Improvements
- **Deep Crawling**: Implement recursive crawling with depth control.
- **Headless Browser**: Use Playwright/Selenium for JS-rendered content.
- **Citations**: Return exact source snippets/links with the answer.