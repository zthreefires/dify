import pytest

from core.rag.models.document import Document
from core.rag.rerank.entity.weight import KeywordSetting, VectorSetting, Weights
from core.rag.rerank.weight_rerank import WeightRerankRunner


@pytest.fixture
def weight_rerank():
    vector_setting = VectorSetting(
        vector_weight=0.5, embedding_model_name="test_model", embedding_provider_name="test_provider"
    )
    keyword_setting = KeywordSetting(keyword_weight=0.5)
    weights = Weights(vector_setting=vector_setting, keyword_setting=keyword_setting)
    return WeightRerankRunner("test_tenant", weights)


def test_run_with_empty_documents(weight_rerank, mocker):
    mocker.patch.object(WeightRerankRunner, "_calculate_keyword_score", return_value=[])
    mocker.patch.object(WeightRerankRunner, "_calculate_cosine", return_value=[])
    documents = []
    result = weight_rerank.run("test query", documents)
    assert result == []


def test_run_with_score_threshold(weight_rerank, mocker):
    mocker.patch.object(WeightRerankRunner, "_calculate_keyword_score", return_value=[0.5])
    mocker.patch.object(WeightRerankRunner, "_calculate_cosine", return_value=[0.5])

    doc = Document(page_content="test content", metadata={"doc_id": "1"}, vector=[0.1, 0.2, 0.3])

    # Test with score threshold that filters out the document
    result = weight_rerank.run("test query", [doc], score_threshold=0.6)
    assert len(result) == 0

    # Test with score threshold that keeps the document
    result = weight_rerank.run("test query", [doc], score_threshold=0.4)
    assert len(result) == 1
    assert result[0].metadata["score"] == 0.5


def test_run_with_top_n(weight_rerank, mocker):
    mocker.patch.object(WeightRerankRunner, "_calculate_keyword_score", return_value=[0.8, 0.6, 0.4])
    mocker.patch.object(WeightRerankRunner, "_calculate_cosine", return_value=[0.7, 0.5, 0.3])

    docs = [
        Document(page_content="doc1", metadata={"doc_id": "1"}, vector=[0.1]),
        Document(page_content="doc2", metadata={"doc_id": "2"}, vector=[0.2]),
        Document(page_content="doc3", metadata={"doc_id": "3"}, vector=[0.3]),
    ]

    result = weight_rerank.run("test query", docs, top_n=2)
    assert len(result) == 2
    assert result[0].metadata["score"] > result[1].metadata["score"]


def test_run_with_duplicate_documents(weight_rerank, mocker):
    mocker.patch.object(WeightRerankRunner, "_calculate_keyword_score", return_value=[0.5])
    mocker.patch.object(WeightRerankRunner, "_calculate_cosine", return_value=[0.5])

    doc1 = Document(page_content="test content", metadata={"doc_id": "1"}, vector=[0.1])
    doc2 = Document(page_content="test content", metadata={"doc_id": "1"}, vector=[0.1])

    result = weight_rerank.run("test query", [doc1, doc2])
    assert len(result) == 1
    assert result[0].metadata["doc_id"] == "1"


def test_run_with_missing_metadata(weight_rerank, mocker):
    mocker.patch.object(WeightRerankRunner, "_calculate_keyword_score", return_value=[0.5])
    mocker.patch.object(WeightRerankRunner, "_calculate_cosine", return_value=[0.5])

    doc = Document(page_content="test content", metadata={"doc_id": None}, vector=[0.1])
    result = weight_rerank.run("test query", [doc])
    assert len(result) == 1


def test_run_with_none_score_threshold(weight_rerank, mocker):
    mocker.patch.object(WeightRerankRunner, "_calculate_keyword_score", return_value=[0.5])
    mocker.patch.object(WeightRerankRunner, "_calculate_cosine", return_value=[0.5])

    doc = Document(page_content="test content", metadata={"doc_id": "1"}, vector=[0.1])
    result = weight_rerank.run("test query", [doc], score_threshold=None)
    assert len(result) == 1
    assert result[0].metadata["score"] == 0.5


def test_run_with_none_top_n(weight_rerank, mocker):
    mocker.patch.object(WeightRerankRunner, "_calculate_keyword_score", return_value=[0.5, 0.3])
    mocker.patch.object(WeightRerankRunner, "_calculate_cosine", return_value=[0.5, 0.3])

    docs = [
        Document(page_content="doc1", metadata={"doc_id": "1"}, vector=[0.1]),
        Document(page_content="doc2", metadata={"doc_id": "2"}, vector=[0.2]),
    ]

    result = weight_rerank.run("test query", docs, top_n=None)
    assert len(result) == 2
