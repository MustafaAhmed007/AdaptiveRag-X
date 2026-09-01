from adaptive_rag.models import Document
from adaptive_rag.storage import SQLiteDocumentStore


def test_sqlite_round_trip(tmp_path):
    store = SQLiteDocumentStore(str(tmp_path / "docs.db"))
    document = Document(id="1", text="hello", tenant_id="tenant-a")
    store.upsert([document])
    assert store.list("tenant-a")[0].text == "hello"
    assert store.list("tenant-b") == []
    store.delete("1", "tenant-a")
    assert store.list("tenant-a") == []
