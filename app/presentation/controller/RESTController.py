from flask import Blueprint, request, jsonify
from app.core.dtos.DocumentDTO import DocumentDTO
from app.infrastructure.db.PDFLoader import PDFLoader
from app.core.services.DatabaseService import DatabaseService
import app.core.ApplicationService  
import os
import traceback

rest_bp = Blueprint("rest", __name__)

# ➤ Enrich prompt with similarity search and RAG prompt template (POST)
@rest_bp.route("/rag/enrich", methods=["POST"])
def enrich_prompt():
    """
    Enriches the given prompt using similarity search and the RAG prompt template.
    Expects JSON: { "prompt": "...", "question": "..." }
    Returns: { "enriched_prompt": "..." }
    """
    data = request.get_json()
    prompt = data.get("prompt", "")
    question = data.get("question", "")
    k = int(data.get("k", 3))
    # Suche Kontext (Chunks) zu question
    db_service = app.core.services.DatabaseService.db_service
    results = db_service.search_docs(question, k)
    context = [dto for dto, _ in results]
    state = {
        "prompt": prompt,
        "question": question,
        "context": context,
        "answer": ""
    }
    try:
        enriched = app.core.ApplicationService.application_service.answer_with_rag(state)
        print(f"[RAG] Enriched prompt: {enriched}")
        return jsonify({"enriched_prompt": enriched}), 200
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# ➤ Add documents (POST)
@rest_bp.route("/rag", methods=["POST"])
def add_docs():
    """
    Adds a list of documents to the database.
    Expects a JSON list of documents.
    """
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
        db_service = app.core.services.DatabaseService.db_service
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
        db_service = app.core.services.DatabaseService.db_service
        db_service.update_doc(document)
        return jsonify({"status": "updated"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ➤ Get a document by ID (GET)
@rest_bp.route("/rag/<doc_id>", methods=["GET"])
def get_doc_by_id(doc_id):
    try:
        db_service = app.core.services.DatabaseService.db_service
        result = db_service.get_doc_by_id(doc_id)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ➤ Similarity search (GET)
@rest_bp.route('/rag/search', methods=['GET'])
def search_docs():
    query = request.args.get("query")
    if not query:
        return jsonify({"error": "No query provided"}), 400

    try:
        k = int(request.args.get("k", 3))
        db_service = app.core.services.DatabaseService.db_service
        results = db_service.search_docs(query, k)
        # results ist jetzt eine Liste von (DocumentDTO, distance)
        response = [
            {
                "id": dto.id,
                "text": dto.text,
                "metadata": dto.metadata,
                "distance": distance
            }
            for dto, distance in results
        ]
        return jsonify({"results": response}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ➤ Delete a document by ID (DELETE)
@rest_bp.route("/rag/<doc_id>", methods=["DELETE"])
def delete_doc(doc_id):
    try:
        db_service = app.core.services.DatabaseService.db_service
        db_service.delete_doc(doc_id)
        return jsonify({"status": "deleted"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# ➤ Clear the database (POST)
@rest_bp.route("/rag/clear", methods=["POST"])
def clear_collection():
    try:
        db_service = app.core.services.DatabaseService.db_service
        db_service.clear()
        return jsonify({"status": "cleared"}), 200
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# ➤ Upload PDF and add to database (POST)
@rest_bp.route("/rag/upload_pdf", methods=["POST"])
def upload_pdf():
    file = request.files.get("file")
    if not file:
        return jsonify({"error": "No file uploaded"}), 400

    import tempfile
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        file.save(tmp.name)

    try:
        db_service = app.core.services.DatabaseService.db_service
        collection = db_service.adapter.collection
        loader = PDFLoader(collection)
        docs = loader.load_and_split(tmp.name)
        loader.store_chunks(docs, filename_prefix=os.path.basename(tmp.name).replace(".pdf", ""))

        return jsonify({"status": "PDF processed and added"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ➤ Debug: Dump all document IDs (GET)
@rest_bp.route("/rag/debug_dump", methods=["GET"])
def debug_dump():
    try:
        db_service = app.core.services.DatabaseService.db_service
        adapter = db_service.db  # Access the adapter (DatabasePort)
        client = adapter.client  # Access the LangchainClient
        ids = client.collection.get()["ids"]
        return jsonify({"count": len(ids), "ids": ids}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

