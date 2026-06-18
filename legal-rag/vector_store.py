import chromadb
from sentence_transformers import SentenceTransformer

client = chromadb.Client()

embedding_model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

collection = client.get_or_create_collection(
    name="contracts"
)


def store_chunks(chunks):
    global collection
    try:
        client.delete_collection("contracts")
    except:
        pass

    collection = client.get_or_create_collection(
        name="contracts"
    )

    for index, chunk in enumerate(chunks):
        embedding = embedding_model.encode(
            chunk["text"]
        )

        collection.add(
            ids=[f"chunk_{index}"],
            embeddings=[embedding.tolist()],
            documents=[chunk["text"]],
            metadatas=[
                {
                    "page": chunk["page"]
                }
            ]
        )

    print("Chunks stored successfully")

def retrieve_chunks(question):

    question_embedding = embedding_model.encode(
        question
    )

    results = collection.query(
        query_embeddings=[
            question_embedding.tolist()
        ],
        n_results=3
    )

    return results
