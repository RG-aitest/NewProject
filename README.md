🌊 Agentic Environment Intelligence System

📌 Overview
This project uses a LangChain-powered agent to answer environmental and sustainability-related questions. It combines document-based retrieval (RAG), real-time water quality data from the USGS API, and local LLM inference via Ollama. The system is modular, extensible, and fully Dockerized for reproducibility.

---

🧱 Architecture

- Ingestion Pipeline: Embeds environmental documents using SentenceTransformer and stores them in a FAISS vector index.
- LangChain Agent: Uses ZERO_SHOT_REACT_DESCRIPTION to reason and select tools.
- Tools:
  - RAG Retriever: Retrieves relevant document chunks.
  - USGS Water API: Fetches real-time water quality data.
- LLM: Runs locally via OllamaLLM.
- Backend: FastAPI server (backend.py) exposes /ask endpoint.
- UI: Optional Streamlit interface (AIBot_UI.py) for interactive querying.

---

🚀 Setup Instructions

🔧 Local Setup (Optional)
bash
pip install -r requirements.txt
python backend.py
streamlit run AIBot_UI.py

1.Build the Docker Image
docker build -t intelli-agent .

2. Run the Container
docker run -p 8000:8000 intelli-agent

3. Test the API
curl http://localhost:8000/ask?query="What is the nitrate level in California?"

4. Unit Testing
Run unit tests using pytest:
pytest test_agent.py


Project Structure
├── AIBot.py              # LangChain agent logic
├── AIBot_UI.py           # Optional Streamlit UI
├── ingest.py             # Document ingestion and FAISS indexing
├── backend.py            # FastAPI backend
├── test_agent.py         # Unit tests
├── Dockerfile            # Docker setup
├── requirements.txt      # Python dependencies
├── vector_store          # Faiss Vector store
├── data          		  # Contains Files to be ingested.(Pdf, txt)
├── drawio/flow.drawio    # Architecture diagram
├── drawio/design.drawio  # Architecture diagram
├── HLDv1.0.docx          # High-level design document
└── README.md             # Project overview



5. Design Assets
- Ingested Document : "Water-Quality Trends in the Nation’s Rivers and Streams, 1972–2012—Data Preparation, Statistical Methods, and Trend Results"
- Architecture Diagram: flow.drawio , design1.drawio
- Design Document: docs/design.md

6. Sample Bot Questions:
Type					Example question
Pure RAG			“Summarize nitrate trends discussed in the USGS water report.”
API call trigger	“Give me real-time water quality data for Texas rivers.”
Combined			“What are the main pollutants in Texas rivers, according to USGS data and reports?”

7. Future Enhancements
- LLM Response Accuracy.
- Response Optimization. 
- Add support for multi-turn conversations
- Integrate additional environmental APIs

Author
Built by Ravi Gupta — focused on scalable, secure, and production-grade agentic systems.



