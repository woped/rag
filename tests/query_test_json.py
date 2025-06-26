import json
from chromadb import PersistentClient

client = PersistentClient(path="chroma")
collection = client.get_or_create_collection(name="rag_collection")

results = collection.get()

def convert_to_serializable(obj):
    if isinstance(obj, dict):
        return {k: convert_to_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_serializable(i) for i in obj]
    elif hasattr(obj, "tolist"):  # z.B. numpy arrays
        return obj.tolist()
    else:
        return obj

# Ergebnislisten aus dem Ergebnis extrahieren
ids = results.get("ids", [])
documents = results.get("documents", [])
metadatas = results.get("metadatas", [])

# Sicherstellen, dass alle Listen die gleiche Länge haben
length = min(len(ids), len(documents), len(metadatas))

# Zusammenbauen der Liste von Objekten
output = []
for i in range(length):
    output.append({
        "id": ids[i],
        "document": documents[i],
        "metadata": convert_to_serializable(metadatas[i])
    })

# Ergebnis in Datei schreiben
with open("output200_1.json", "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)
