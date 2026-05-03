import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Check for required environment variables
required_envs = ["GOOGLE_API_KEY", "ORACLE_USER", "ORACLE_PASSWORD", "ORACLE_DSN"]
missing_envs = [env for env in required_envs if not os.getenv(env)]

if missing_envs:
    print(f"Error: Missing required environment variables: {', '.join(missing_envs)}")
    print("Please create a .env file based on the required variables.")
    sys.exit(1)

import oracledb
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_oracledb.vectorstores import OracleVS
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# 1. Connect to Oracle Database
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

# 2. Initialize Models
print("Initializing Gemini Models...")
embedding_model = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-2")
chat_model = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)

# 3. Configure Oracle Vector Store
print("Configuring Oracle Vector Store...")
# OracleVS will automatically create the table if it does not exist
vector_store = OracleVS(
    client=connection,
    embedding_function=embedding_model,
    table_name="corpus_vector_store",
    distance_strategy="COSINE"
)

# 4. Ingest Document (Simple single file chunking)
print("Ingesting corpus.txt...")
try:
    with open("corpus.txt", "r", encoding="utf-8") as f:
        text_content = f.read()
    
    # Very simple manual split by double newlines (paragraphs)
    # For a real app, use RecursiveCharacterTextSplitter
    chunks = [chunk.strip() for chunk in text_content.split("\n\n") if chunk.strip()]
    
    # Generate random IDs or let the store handle it. It's safer to provide metadata and texts.
    vector_store.add_texts(
        texts=chunks,
        metadatas=[{"source": "corpus.txt", "chunk_index": i} for i in range(len(chunks))]
    )
    print(f"Successfully added {len(chunks)} chunks to Oracle Vector Store.")
except Exception as e:
    print(f"Warning: Could not ingest corpus: {e}")

# 5. Perform RAG
print("\n--- Testing RAG Pipeline ---")

# Setup the retriever
retriever = vector_store.as_retriever(search_kwargs={"k": 2})

# Define the RAG prompt template
template = """Answer the question based only on the following context:
{context}

Question: {question}
"""
prompt = PromptTemplate.from_template(template)

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

# Create the RAG chain
rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | chat_model
    | StrOutputParser()
)

# Ask a question
question = "Why is Oracle AI Vector Search useful for RAG?"
print(f"Question: {question}")
print("Thinking...")

answer = rag_chain.invoke(question)
print(f"\nAnswer: {answer}\n")

# Close connection
connection.close()
print("Disconnected from database.")
