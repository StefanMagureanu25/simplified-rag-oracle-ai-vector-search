# Detailed Setup Guide

Follow these steps if you are running this project for the very first time.

## 1. Prerequisites
- **Python 3.9+**
- **Oracle Database 23ai** (e.g., running via the official Oracle 23ai Free Docker image on port 1521).
- A **Google Gemini API Key** (from [Google AI Studio](https://aistudio.google.com/)).

## 2. Set Up the Python Environment
Create a virtual environment and install the required dependencies:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 3. Configure the Oracle Database
Do not use the `SYSTEM` tablespace to store vectors. You need to create a dedicated user for this application.
Execute the `src/setup_user.sql` script as `SYS` or `SYSTEM` to create a user named `raguser`.

## 4. Environment Variables (`.env`)
In the root directory of the project, create a file named `.env`. This file is required to connect to the database and the Gemini API.

**Mock-up `.env` file for reference:**
```env
GOOGLE_API_KEY=your_gemini_api_key_here
ORACLE_USER=raguser
ORACLE_PASSWORD=password123456
ORACLE_DSN=localhost:1521/FREEPDB1
```

## 5. Generate the Corpus
Before you can chat with the AI, you must generate a corpus (a dataset) inside the `data` folder. 
Run the provided scraper script, which will automatically create the `data` directory and download Wikipedia articles to `data/corpus.txt`:
```bash
python src/scraper.py
```

## 6. Run the Application
Start the FastAPI server from the root of the project:
```bash
uvicorn src.app:app --reload
```
Open your web browser and navigate to **[http://localhost:8000](http://localhost:8000)**. Click **"Ingest Corpus"** to embed the `data/corpus.txt` into Oracle.

---

## Troubleshooting: Viewing Data in a SQL Client
If you attempt to view the `corpus_vector_store` table in a tool like **DataGrip** or **DBeaver**, you may encounter a Java JDBC crash (`ORA-17004: Invalid column type`). This happens because older JDBC drivers do not know how to visually render Oracle 23ai `VECTOR` types.

**The Fix:**
Run this query to safely convert the vectors to strings for viewing:
```sql
SELECT 
    id, 
    text, 
    json_serialize(metadata) as metadata, 
    to_char(embedding) as embedding 
FROM corpus_vector_store;
```
