import pytest
import requests

BASE_URL = "http://127.0.0.1:5000"

@pytest.fixture(scope="module", autouse=True)
def clear_database_before_tests():
    res = requests.post(f"{BASE_URL}/rag/clear")
    assert res.status_code == 200

@pytest.fixture(scope="module")
def test_doc():
    return {
        "id": "test-doc-123",
        "text": "A Petri net consists of places and transitions.",
        "metadata": {"source": "test"},
        "query": "What is a Petri net?"
    }

# ➤ Test: POST /rag (Add document to the database)
def test_add_document(test_doc):
    payload = [
        {
            "id": test_doc["id"],
            "text": test_doc["text"],
            "metadata": test_doc["metadata"]
        }
    ]
    res = requests.post(f"{BASE_URL}/rag", json=payload)
    print("ADD:", res.status_code, res.text)
    assert res.status_code in (200, 201)

# ➤ Test: GET /rag/<id> (Fetch document by ID)
def test_get_document(test_doc):
    res = requests.get(f"{BASE_URL}/rag/{test_doc['id']}")
    print("GET:", res.status_code, res.text)
    assert res.status_code == 200
    data = res.json()
    assert data["text"] == test_doc["text"]

# ➤ Test: GET /rag/search?query=... (Run similarity search)
def test_similarity_search(test_doc):
    res = requests.get(f"{BASE_URL}/rag/search", params={
        "query": test_doc["query"],
        "k": 1
    })
    print("SEARCH:", res.status_code, res.text)
    assert res.status_code == 200
    data = res.json()
    assert "results" in data
    assert any(test_doc["text"] in doc["text"] for doc in data["results"])

# ➤ Test: DELETE /rag/<id> (Delete document by ID)
def test_delete_document(test_doc):
    res = requests.delete(f"{BASE_URL}/rag/{test_doc['id']}")
    print("DELETE:", res.status_code, res.text)
    assert res.status_code == 200
