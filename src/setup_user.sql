CREATE USER raguser IDENTIFIED BY "password123456" DEFAULT TABLESPACE users QUOTA UNLIMITED ON users;

GRANT CONNECT, RESOURCE TO raguser;


-- query for displaying information embeddings stored in the vector store
SELECT
    id,
    text,
    json_serialize(metadata) AS metadata,
    vector_serialize(embedding RETURNING CLOB) AS embedding
FROM "corpus_vector_store";