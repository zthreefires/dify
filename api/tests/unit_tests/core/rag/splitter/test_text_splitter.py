from core.rag.models.document import Document
from core.rag.splitter.text_splitter import (
    CharacterTextSplitter,
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter,
    TokenTextSplitter,
)


def test_create_documents_with_metadata():
    splitter = CharacterTextSplitter(chunk_size=10, chunk_overlap=0)
    texts = ["Hello world", "Test document"]
    metadatas = [{"source": "test1"}, {"source": "test2"}]

    docs = splitter.create_documents(texts, metadatas)

    assert len(docs) == 2
    assert docs[0].metadata == {"source": "test1"}
    assert docs[0].page_content == "Hello world"
    assert docs[1].metadata == {"source": "test2"}
    assert docs[1].page_content == "Test document"


def test_create_documents_with_start_index():
    splitter = CharacterTextSplitter(chunk_size=10, chunk_overlap=0, add_start_index=True)
    texts = ["Hello world"]
    docs = splitter.create_documents(texts)

    assert len(docs) == 1
    assert docs[0].metadata["start_index"] == 0
    assert docs[0].page_content == "Hello world"


def test_split_documents():
    splitter = CharacterTextSplitter(chunk_size=10, chunk_overlap=0)
    docs = [
        Document(page_content="Hello world", metadata={"source": "test1"}),
        Document(page_content="Test document", metadata={"source": "test2"}),
    ]

    split_docs = splitter.split_documents(docs)

    assert len(split_docs) == 2
    assert split_docs[0].metadata == {"source": "test1"}
    assert split_docs[0].page_content == "Hello world"
    assert split_docs[1].metadata == {"source": "test2"}
    assert split_docs[1].page_content == "Test document"


def test_markdown_header_splitter():
    markdown_text = """# Header 1
Content 1
## Header 2
Content 2
### Header 3
Content 3"""

    headers_to_split_on = [("#", "Header 1"), ("##", "Header 2"), ("###", "Header 3")]
    splitter = MarkdownHeaderTextSplitter(headers_to_split_on)

    docs = splitter.split_text(markdown_text)

    assert len(docs) == 3
    assert docs[0].metadata == {"Header 1": "Header 1"}
    assert "Content 1" in docs[0].page_content
    assert docs[1].metadata == {"Header 1": "Header 1", "Header 2": "Header 2"}
    assert "Content 2" in docs[1].page_content
    assert docs[2].metadata == {"Header 1": "Header 1", "Header 2": "Header 2", "Header 3": "Header 3"}
    assert "Content 3" in docs[2].page_content


def test_markdown_header_splitter_line_by_line():
    markdown_text = """# Header 1
Content 1
## Header 2
Content 2"""

    headers_to_split_on = [("#", "Header 1"), ("##", "Header 2")]
    splitter = MarkdownHeaderTextSplitter(headers_to_split_on, return_each_line=True)

    docs = splitter.split_text(markdown_text)

    assert len(docs) == 2
    assert docs[0].metadata == {"Header 1": "Header 1"}
    assert docs[1].metadata == {"Header 1": "Header 1", "Header 2": "Header 2"}


def test_aggregate_lines_to_chunks():
    lines = [
        {"content": "Line 1", "metadata": {"header": "h1"}},
        {"content": "Line 2", "metadata": {"header": "h1"}},
        {"content": "Line 3", "metadata": {"header": "h2"}},
    ]

    splitter = MarkdownHeaderTextSplitter([("#", "h1")])
    chunks = splitter.aggregate_lines_to_chunks(lines)

    assert len(chunks) == 2
    assert chunks[0].page_content == "Line 1  \nLine 2"
    assert chunks[0].metadata == {"header": "h1"}
    assert chunks[1].page_content == "Line 3"
    assert chunks[1].metadata == {"header": "h2"}


def test_recursive_character_splitter():
    text = """First paragraph.
    Second paragraph.

    Third paragraph.
    Fourth paragraph.

    Final paragraph."""

    splitter = RecursiveCharacterTextSplitter(chunk_size=30, chunk_overlap=0)
    chunks = splitter.split_text(text)

    assert len(chunks) > 1
    assert all(len(chunk) <= 30 for chunk in chunks)
    assert any("First" in chunk for chunk in chunks)
    assert any("Final" in chunk for chunk in chunks)


def test_token_text_splitter():
    text = "This is a test text that needs to be split into tokens."
    splitter = TokenTextSplitter(chunk_size=10, chunk_overlap=0)

    chunks = splitter.split_text(text)

    assert len(chunks) > 1
    assert all(len(chunk.split()) <= 10 for chunk in chunks)


def test_character_splitter_empty_text():
    splitter = CharacterTextSplitter(chunk_size=10, chunk_overlap=0)
    text = ""
    chunks = splitter.split_text(text)
    assert len(chunks) == 0


def test_markdown_splitter_no_headers():
    text = "Just some text\nwithout headers"
    splitter = MarkdownHeaderTextSplitter([("#", "h1")])
    docs = splitter.split_text(text)
    assert len(docs) == 1
    assert docs[0].page_content == text


def test_recursive_splitter_single_char():
    splitter = RecursiveCharacterTextSplitter(chunk_size=1, chunk_overlap=0)
    text = "abc"
    chunks = splitter.split_text(text)
    assert chunks == ["a", "b", "c"]


def test_markdown_splitter_hierarchical_headers():
    markdown_text = """# Main Header
## Sub Header 1
Content 1
## Sub Header 2
Content 2
### Sub Sub Header
Content 3"""

    headers_to_split_on = [("#", "h1"), ("##", "h2"), ("###", "h3")]
    splitter = MarkdownHeaderTextSplitter(headers_to_split_on)
    docs = splitter.split_text(markdown_text)

    assert len(docs) == 3
    assert "Main Header" in docs[0].metadata["h1"]
    assert "Sub Header 1" in docs[0].metadata.get("h2", "")
    assert "Content 1" in docs[0].page_content
    assert "Sub Sub Header" in docs[2].metadata.get("h3", "")
