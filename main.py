from flask import Flask
from app.presentation.controller.RESTController import rest_bp
import glob, os
from dotenv import load_dotenv
from app.infrastructure.db.PDFLoader import PDFLoader
from chromadb import PersistentClient
from app.presentation.controller.RESTController import rest_bp, db_service
from app.core.dtos.DocumentDTO import DocumentDTO



client      = PersistentClient(path="chroma")
collection   = client.get_or_create_collection("rag_collection")
loader        = PDFLoader(collection)


load_dotenv()

def create_app():
    app = Flask(__name__)
    app.register_blueprint(rest_bp)
    return app

def delete_old_docs_by_prefix(collection, prefix):
    results = collection.get()
    all_ids = results.get("ids", [])
    ids_to_delete = [id_ for id_ in all_ids if id_.startswith(prefix)]
    if ids_to_delete:
        collection.delete(ids=ids_to_delete)
        print(f"→ Gelöscht: {len(ids_to_delete)} alte Chunks mit Prefix '{prefix}'")
    else:
        print(f"→ Keine alten Chunks mit Prefix '{prefix}' gefunden")


if __name__ == "__main__":
    for pdf_path in glob.glob("PDF/*.pdf"):
        print("--> Lade:", pdf_path)
        chunks = loader.load_and_split(pdf_path)
        texts = [c.page_content for c in chunks]
        metadatas = [c.metadata for c in chunks]
        filename_prefix = os.path.basename(pdf_path).replace(".pdf", "")
        ids = [f"{filename_prefix}_{i}" for i in range(len(texts))]

        # Alte Dokumente mit diesem Prefix löschen, ansonsten findet nie eine Aktualisierung der Datenbank bei veränderter Chunk Size in PDFLoader statt.
        delete_old_docs_by_prefix(collection, filename_prefix)

        # Neue Dokumente hinzufügen
        db_service.db.add_docs([
            DocumentDTO(id=i, text=t, metadata=m)
            for i, t, m in zip(ids, texts, metadatas)
        ])

    
    port = int(os.getenv("PORT", 5000))
    app = create_app()
    app.run(debug=True, use_reloader=False, port=port)