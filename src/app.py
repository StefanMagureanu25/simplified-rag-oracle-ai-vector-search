import os
import asyncio
import sys
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import oracledb
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_oracledb.vectorstores import OracleVS
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CORPUS_PATH = os.path.join(BASE_DIR, "data", "corpus.txt")
STATIC_PATH = os.path.join(BASE_DIR, "static")

# 1. Initialization and Environment Check
load_dotenv()
required_envs = ["GOOGLE_API_KEY", "ORACLE_USER", "ORACLE_PASSWORD", "ORACLE_DSN"]
missing_envs = [env for env in required_envs if not os.getenv(env)]

if missing_envs:
    print(f"Error: Missing required environment variables: {', '.join(missing_envs)}")
    sys.exit(1)

app = FastAPI(title="Oracle RAG API")

connection, rag_chain, vector_store = None, None, None

@app.on_event("startup")
def startup_event():
    global connection, rag_chain, vector_store
    print("Connecting to Oracle Database...")
    try:
        connection = oracledb.connect(
            user=os.getenv("ORACLE_USER"),
            password=os.getenv("ORACLE_PASSWORD"),
            dsn=os.getenv("ORACLE_DSN")
        )
        print("Successfully connected to Oracle Database 23ai.")
    except Exception as e:
        print(f"Failed to connect to Oracle Database: {e}")
        sys.exit(1)

    print("Initializing Gemini Models...")
    embedding_model = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-2")
    chat_model = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)

    print("Configuring Oracle Vector Store...")
    vector_store = OracleVS(
        client=connection,
        embedding_function=embedding_model,
        table_name="corpus_vector_store",
        distance_strategy="COSINE"
    )

    print("Setting up RAG Chain...")
    retriever = vector_store.as_retriever(search_kwargs={"k": 2})
    template = """Answer the question based only on the following context:
{context}

Question: {question}
"""
    prompt = PromptTemplate.from_template(template)
    
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | chat_model
        | StrOutputParser()
    )
    print("Startup complete. Ready to serve requests!")

@app.on_event("shutdown")
def shutdown_event():
    global connection
    if connection:
        connection.close()
        print("Disconnected from Oracle Database.")

class ChatRequest(BaseModel):
    prompt: str

class ChatResponse(BaseModel):
    answer: str

class IngestResponse(BaseModel):
    message: str

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    if not rag_chain:
        raise HTTPException(status_code=500, detail="RAG Chain is not initialized.")
    
    try:
        answer = rag_chain.invoke(request.prompt)
        return ChatResponse(answer=answer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ingest", response_model=IngestResponse)
async def ingest_endpoint():
    if not vector_store:
        raise HTTPException(status_code=500, detail="Vector Store is not initialized.")
    
    try:
        with open(CORPUS_PATH, "r", encoding="utf-8") as f:
            text_content = f.read()
            
        chunks = [chunk.strip() for chunk in text_content.split("\n\n") if chunk.strip()]
        
        batch_size = 50
        total_batches = (len(chunks) - 1) // batch_size + 1
        
        for i in range(0, len(chunks), batch_size):
            batch_chunks = chunks[i:i + batch_size]
            
            max_retries = 5
            for attempt in range(max_retries):
                batch_metadatas = [{"source": CORPUS_PATH, "chunk_index": j} for j in range(i, i + len(batch_chunks))]
                
                try:
                    vector_store.add_texts(texts=batch_chunks, metadatas=batch_metadatas)
                    break
                except Exception as e:
                    if attempt < max_retries - 1:
                        wait = 15 * (attempt + 1)
                        print(f"Rate limited on batch {i//batch_size + 1}, retrying in {wait}s...")
                        await asyncio.sleep(wait)
                    else:
                        raise
            
            print(f"Ingested batch {i//batch_size + 1}/{total_batches}")
            
            if i + batch_size < len(chunks):
                await asyncio.sleep(8)
                
        return IngestResponse(message=f"Successfully added {len(chunks)} chunks to Oracle Vector Store.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

import os as _os
if not _os.path.exists(STATIC_PATH):
    _os.makedirs(STATIC_PATH)
    
app.mount("/static", StaticFiles(directory=STATIC_PATH), name="static")

@app.get("/")
async def serve_frontend():
    return FileResponse(_os.path.join(STATIC_PATH, "index.html"))
