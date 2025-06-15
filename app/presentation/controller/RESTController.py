from flask import Blueprint, request, jsonify
from app.core.services.DatabaseService import DatabaseService
from app.infrastructure.db.DatabaseAdapter import DatabaseAdapter
from app.core.dtos.DocumentDTO import DocumentDTO
from app.infrastructure.db.PDFLoader import PDFLoader
import os

rest_bp = Blueprint("rest", __name__)
db_service = DatabaseService(DatabaseAdapter())

# ➤ Add documents (POST)
@rest_bp.route("/rag", methods=["POST"])
def add_docs():
    try:
        data = request.get_json()
        if not isinstance(data, list):
            return jsonify({"error": "Expected a list of documents"}), 400

        for doc in data:
            if "text" not in doc:
                return jsonify({"error": "Missing text in document"}), 400

        document_dtos = [
            DocumentDTO(id=doc.get("id"), text=doc["text"], metadata=doc.get("metadata"))
            for doc in data
        ]
        db_service.add_docs(document_dtos)
        return jsonify({"status": "ok"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ➤ Update a document by ID (PUT)
@rest_bp.route("/rag/<doc_id>", methods=["PUT"])
def update_doc(doc_id):
    data = request.get_json()
    text = data.get("text")
    if not text:
        return jsonify({"error": "No text provided"}), 400

    metadata = data.get("metadata", {})

    try:
        document = DocumentDTO(id=doc_id, text=text, metadata=metadata)
        db_service.update_doc(document)
        return jsonify({"status": "updated"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ➤ Get a document by ID (GET)
@rest_bp.route("/rag/<doc_id>", methods=["GET"])
def get_doc_by_id(doc_id):
    try:
        result = db_service.get_doc_by_id(doc_id)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ➤ Similarity search (GET) -> noch nicht funktional
@rest_bp.route('/rag/search', methods=['GET'])
def search_docs():
    query = request.args.get("query")
    if not query:
        return jsonify({"error": "No query provided"}), 400

    try:
        k = int(request.args.get("k", 3))
        results = db_service.search_docs(query, k)
        return jsonify({"results": results}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ➤ Delete a document by ID (DELETE)
@rest_bp.route("/rag/<doc_id>", methods=["DELETE"])
def delete_doc(doc_id):
    try:
        db_service.delete_doc(doc_id)
        return jsonify({"status": "deleted"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# ➤ Clear the database
@rest_bp.route("/rag/clear", methods=["POST"])
def clear_collection():
    try:
        db_service.clear()
        return jsonify({"status": "cleared"}), 200
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500



@rest_bp.route("/rag/upload_pdf", methods=["POST"])
def upload_pdf():
    file = request.files.get("file")
    if not file:
        return jsonify({"error": "No file uploaded"}), 400

    import tempfile
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        file.save(tmp.name)

    try:
        collection = db_service.adapter.collection
        loader = PDFLoader(collection)
        docs = loader.load_and_split(tmp.name)
        loader.store_chunks(docs, filename_prefix=os.path.basename(tmp.name).replace(".pdf", ""))

        return jsonify({"status": "PDF processed and added"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@rest_bp.route("/rag/debug_dump", methods=["GET"])
def debug_dump():
    try:
        adapter = db_service.db  # Zugriff auf den Adapter (DatabasePort)
        client = adapter.client  # Zugriff auf LangchainClient
        ids = client.collection.get()["ids"]
        return jsonify({"count": len(ids), "ids": ids}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

