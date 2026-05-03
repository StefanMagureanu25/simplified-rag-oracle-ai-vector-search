# Simplified RAG with Oracle 23ai Vector Search

This is a minimal Retrieval-Augmented Generation (RAG) application demonstrating the integration of **Google Gemini** with **Oracle Database 23ai** using native `VECTOR` datatypes.

## Quick Start Overview

To get this project running, you will generally need to:
1. **Install Dependencies**: `pip install -r requirements.txt`
2. **Configure the Environment**: Set up your Oracle 23ai database, `.env` file, and generate the `data/corpus.txt` dataset.
3. **Start the Application**: Run the FastAPI server.
   ```bash
   uvicorn src.app:app --reload
   ```
4. **Access the UI**: Navigate to `http://localhost:8000`, ingest your data, and start chatting.

> [!IMPORTANT]
> **For detailed, step-by-step instructions on setting up the database, environment variables, and generating your initial corpus, please read the [SETUP.md](SETUP.md) file!**