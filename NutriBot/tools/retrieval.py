# tools/retrieval.py
from dotenv import load_dotenv
load_dotenv()

from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OpenAIEmbeddings

def get_supplements_by_faiss(symptoms: list[str], k: int = 5):
    query = " ".join(symptoms)

    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.load_local(
        "faiss_index", 
        embeddings,
        allow_dangerous_deserialization=True  # ✅ 이 줄이 핵심!
    )

    results = vectorstore.similarity_search(query, k=k)
    return [doc.metadata for doc in results]