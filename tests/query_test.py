from chromadb import PersistentClient
# from app.infrastructure.db.PDFLoader import PDFLoader

client = PersistentClient(path="chroma")
collection = client.get_or_create_collection(name="rag_collection")

results = collection.get()

with open("output101.txt", "w", encoding="utf-8") as f:
    for i, doc in enumerate(results["documents"]):
        f.write(f"\n→ Dokument {i+1}:\n{doc}\n")
