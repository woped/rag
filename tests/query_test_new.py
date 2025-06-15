import sys
import os
import glob
from chromadb import PersistentClient

# Pfad zur Projektwurzel (damit "app" importiert werden kann)
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app.infrastructure.db.PDFLoader import PDFLoader

# Setup ChromaDB-Client und Collection
client = PersistentClient(path="chroma")
collection = client.get_or_create_collection(name="rag_collection")

# → Schritt 1: Collection leeren
print("→ Lösche bestehende Einträge aus der Collection...")
results = collection.get()
all_ids = results.get("ids", [])

if all_ids:
    collection.delete(ids=all_ids)
    print(f"→ {len(all_ids)} Einträge gelöscht.")
else:
    print("→ Keine Einträge zum Löschen gefunden.")

# → Schritt 2: PDF-Dateien laden, splitten und speichern
loader = PDFLoader(collection)

for pdf_path in glob.glob("PDF/*.pdf"):
    print(f"→ Lade und verarbeite: {pdf_path}")
    
    chunks = loader.load_and_split(pdf_path)
    texts = [chunk.page_content for chunk in chunks]
    metadatas = [chunk.metadata for chunk in chunks]
    ids = [f"{os.path.basename(pdf_path).replace('.pdf','')}_{i}" for i in range(len(texts))]

    try:
        collection.add(documents=texts, metadatas=metadatas, ids=ids)
        print(f"   ✓ {len(texts)} Chunks gespeichert.")
    except Exception as e:
        print(f"   ⚠ Fehler beim Speichern: {e}")

print("\n→ Alle PDFs verarbeitet.")

# → Schritt 3: Inhalte exportieren
results = collection.get()

output_path = "output300.txt"
with open(output_path, "w", encoding="utf-8") as f:
    for i, doc in enumerate(results["documents"]):
        f.write(f"\n→ Dokument {i+1}:\n{doc}\n")

print(f"\n→ Export abgeschlossen. Datei: {output_path}")
