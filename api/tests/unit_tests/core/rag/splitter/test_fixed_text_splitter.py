import pytest

from core.rag.splitter.fixed_text_splitter import FixedRecursiveCharacterTextSplitter


@pytest.fixture
def text_splitter():
    return FixedRecursiveCharacterTextSplitter(chunk_size=10, chunk_overlap=5)


def test_split_text_with_fixed_separator(text_splitter):
    text = "Hello\n\nWorld\n\nTest"
    result = text_splitter.split_text(text)
    assert result == ["Hello", "World", "Test"]


def test_split_text_without_fixed_separator():
    splitter = FixedRecursiveCharacterTextSplitter(fixed_separator="", chunk_size=10, chunk_overlap=5)
    text = "Hello World Test"
    result = splitter.split_text(text)
    assert len(result) > 0
    assert all(len(chunk) <= 10 for chunk in result)


def test_split_text_empty_string(text_splitter):
    result = text_splitter.split_text("")
    assert result == [""]


def test_split_text_large_chunk(text_splitter):
    text = "This is a very long text that needs to be split into smaller chunks"
    result = text_splitter.split_text(text)
    assert len(result) > 1
    assert all(len(chunk) <= text_splitter._chunk_size for chunk in result)


def test_recursive_split_text_with_different_separators():
    splitter = FixedRecursiveCharacterTextSplitter(
        fixed_separator="", separators=["\n\n", "\n", " "], chunk_size=10, chunk_overlap=5
    )
    text = "Hello\n\nWorld\nTest More"
    result = splitter.recursive_split_text(text)
    assert len(result) > 0
    assert all(len(chunk) <= splitter._chunk_size for chunk in result)


def test_recursive_split_text_with_no_separators():
    splitter = FixedRecursiveCharacterTextSplitter(fixed_separator="", separators=[""], chunk_size=5, chunk_overlap=2)
    text = "HelloWorld"
    result = splitter.recursive_split_text(text)
    assert len(result) > 1
    assert all(len(chunk) <= splitter._chunk_size for chunk in result)


def test_recursive_split_text_with_small_chunks():
    splitter = FixedRecursiveCharacterTextSplitter(chunk_size=3, chunk_overlap=1)
    text = "Hello World"
    result = splitter.recursive_split_text(text)
    assert len(result) > 2
    assert all(len(chunk) <= splitter._chunk_size for chunk in result)


def test_recursive_split_text_empty_string(text_splitter):
    result = text_splitter.recursive_split_text("")
    assert result == []


def test_split_text_with_custom_separator():
    splitter = FixedRecursiveCharacterTextSplitter(fixed_separator="|", chunk_size=10, chunk_overlap=5)
    text = "Hello|World|Test"
    result = splitter.split_text(text)
    assert result == ["Hello", "World", "Test"]


def test_recursive_split_text_with_overlap():
    splitter = FixedRecursiveCharacterTextSplitter(chunk_size=10, chunk_overlap=5, separators=[" "])
    text = "one two three four five"
    result = splitter.recursive_split_text(text)
    assert len(result) > 1
    for i in range(len(result) - 1):
        common_words = set(result[i].split()).intersection(set(result[i + 1].split()))
        assert len(common_words) > 0


def test_split_text_with_single_chunk():
    splitter = FixedRecursiveCharacterTextSplitter(chunk_size=100, chunk_overlap=10)
    text = "Short text"
    result = splitter.split_text(text)
    assert len(result) == 1
    assert result[0] == text


def test_recursive_split_text_with_multiple_separators():
    splitter = FixedRecursiveCharacterTextSplitter(
        fixed_separator="", separators=["\n", ".", " "], chunk_size=10, chunk_overlap=2
    )
    text = "Hello.\nWorld Test"
    result = splitter.recursive_split_text(text)
    assert len(result) > 1
    assert all(len(chunk) <= splitter._chunk_size for chunk in result)


def test_split_text_with_large_chunk_size():
    splitter = FixedRecursiveCharacterTextSplitter(chunk_size=20, chunk_overlap=5, separators=[" "])
    text = "This is a test of splitting text with larger chunks"
    result = splitter.split_text(text)
    assert len(result) > 0
    assert all(len(chunk) <= 20 for chunk in result)


def test_recursive_split_text_with_mixed_separators():
    splitter = FixedRecursiveCharacterTextSplitter(chunk_size=15, chunk_overlap=3, separators=["\n", " ", "-"])
    text = "Hello world\nThis-is-a-test"
    result = splitter.recursive_split_text(text)
    assert len(result) > 0
    assert all(len(chunk) <= 15 for chunk in result)
