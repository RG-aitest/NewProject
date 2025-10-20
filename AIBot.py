import os
import json
import requests
import faiss
import numpy as np
from PyPDF2 import PdfReader
from sentence_transformers import SentenceTransformer

from langchain_ollama import OllamaLLM
from langchain.agents import initialize_agent, AgentType
from langchain.agents import tool, create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate

# ========== Load Config ==========
with open("config.json", "r") as f:
    config = json.load(f)

VECTOR_DB_PATH = config["VectorDBPath"]
EMBED_MODEL = config["EmbeddingModel"]
LLM_OPTION = config["ModelOption"]
LLM_MAP = config["ModelMap"]
TOP_K = 3
CHUNK_SIZE = config["ChunkSize"]
CHUNK_OVERLAP = config["ChunkOverlap"]
DATA_FOLDER = config["DataFolder"]

# ========== Load FAISS Index ==========
index = faiss.read_index(VECTOR_DB_PATH)
embed_model = SentenceTransformer(EMBED_MODEL)

# ========== Load Chunks ==========
def load_all_chunks(folder_path):
    chunks = []
    for file in os.listdir(folder_path):
        path = os.path.join(folder_path, file)
        text = ""
        if file.endswith(".txt"):
            with open(path, "r", encoding="utf-8") as f:
                text = f.read()
        elif file.endswith(".pdf"):
            reader = PdfReader(path)
            for page in reader.pages:
                text += page.extract_text() or ""
        start = 0
        while start < len(text):
            end = start + CHUNK_SIZE
            chunks.append(text[start:end])
            start += CHUNK_SIZE - CHUNK_OVERLAP
    return chunks

all_chunks = load_all_chunks(DATA_FOLDER)

# ========== Dynamic Public API Tools ==========
#tool_list = [retrieve_context]

for api in config.get("PublicAPIs", []):
    def make_api_tool(api_info):
        @tool
        def dynamic_api(query: str) -> str:
            """Calls a public API using input like 'param1=value1, param2=value2'."""
            try:
                parts = dict(part.strip().split("=") for part in query.split(","))
                url = api_info["url_template"].format(**parts)
                resp = requests.get(url, timeout=10)
                if resp.status_code == 200:
                    return str(resp.json())[:1000]
            except Exception as e:
                return f"API call error: {e}"
            return "No data found"

        dynamic_api.__name__ = api_info["name"].replace(" ", "_")
        dynamic_api.description = api_info["description"]
        return dynamic_api
#    tool_list.append(make_api_tool(api))

from langchain.tools import Tool

# ========== RAG Tool ==========
def rag_tool(query: str) -> str:
    query_emb = embed_model.encode([query], convert_to_numpy=True).astype("float32")
    D, I = index.search(query_emb, TOP_K)
    return "\n\n".join([all_chunks[i] for i in I[0]])

# ========== USGS API Tool ==========
def usgs_tool(query: str) -> str:
    """Input format: 'state=CA, parameter_code=00618'"""
    try:
        parts = dict(part.strip().split("=") for part in query.split(","))
        state = parts.get("state", "CA")
        parameter_code = parts.get("parameter_code", "00618")
        url = f"https://www.waterqualitydata.us/data/Result/search?statecode=US:{state}&pCode={parameter_code}&mimeType=json"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return str(response.json())[:1000]
        return "No data found"
    except Exception as e:
        return f"API call error: {e}"

# ========== Tool List ==========

tool_list = [
    Tool(
        name="RAG Retriever",
        func=rag_tool,
        description="""Use this tool to retrieve context from environmental documents.

When using this tool, format your response exactly as:
Thought: I need to retrieve context from documents.
Action: RAG Retriever
Action Input: [your query]

After receiving the Observation, you may continue reasoning. However:
- If you've already used this tool twice, stop.
- If you still don't have a complete answer, summarize the most relevant Observation.
- Then respond with:
Thought: I now know the partial answer.
Final Answer: [summary based on Observation]

Do not exceed two tool calls. Do not wait for perfect information. Prioritize clarity and conciseness."""
    ),
    Tool(
        name="USGS Water API",
        func=usgs_tool,
        description="""Use this tool to fetch water quality data from the USGS API.

When using this tool, format your response exactly as:
Thought: I need to fetch water quality data.
Action: USGS Water API
Action Input: state=CA, parameter_code=00618

Do not modify the tool name. Use 'USGS Water API' exactly as shown."""
    )
]

# ========== LLM & Agent Setup ==========
llm = OllamaLLM(model="tinyllama")

prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a sustainability agent that answers questions using tools.

When responding, always follow this format:
Thought: [your reasoning]
Action: [tool name from the list]
Action Input: [input string for the tool]

Only use tools from the provided list. Do not make up tool names or skip the format."""),
    ("human", "{input}")
])

agent_executor = initialize_agent(
    tools=tool_list,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    max_iterations=3,
    handle_parsing_errors=True
)


# ========== Run Agent ==========
def run_agent(question: str) -> str:
    print("User Query:", question)
    response = agent_executor.invoke({"input": question})
    return response["output"]

# ========== CLI Chat Loop ==========
def chat():
    print(f"🤖 Using model: {LLM_MAP[str(LLM_OPTION)]}")
    print("Type 'exit' to quit.\n")
    while True:
        query = input("You: ")
        if query.lower() in ["exit", "quit"]:
            break
        answer = run_agent(query)
        print(f"\nAgent: {answer}\n")

if __name__ == "__main__":
    chat()