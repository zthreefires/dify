import base64

import pytest

from libs.password import compare_password, hash_password, valid_password


def test_valid_password_success():
    # Test valid passwords
    assert valid_password("Password123") == "Password123"
    assert valid_password("abcd1234") == "abcd1234"
    assert valid_password("LongPassword12345") == "LongPassword12345"
    assert valid_password("p@ssw0rd") == "p@ssw0rd"
    assert valid_password("12345abc") == "12345abc"


def test_valid_password_failure():
    # Test invalid passwords
    with pytest.raises(ValueError) as exc:
        valid_password("short1")
    assert str(exc.value) == "Password must contain letters and numbers, and the length must be greater than 8."

    with pytest.raises(ValueError):
        valid_password("onlyletters")

    with pytest.raises(ValueError):
        valid_password("12345678")

    with pytest.raises(ValueError):
        valid_password("!@#$%^&*()")

    with pytest.raises(ValueError):
        valid_password("")

    with pytest.raises(ValueError):
        valid_password(" ")


def test_hash_password():
    # Test password hashing
    password = "TestPass123"
    salt = b"testsalt"

    hashed = hash_password(password, salt)

    # Verify hash is hex encoded
    assert isinstance(hashed, bytes)
    assert len(hashed) == 64  # SHA256 produces 32 bytes, hex encoded is 64 chars

    # Same password + salt should produce same hash
    assert hash_password(password, salt) == hashed

    # Different password should produce different hash
    assert hash_password("DifferentPass123", salt) != hashed

    # Different salt should produce different hash
    assert hash_password(password, b"othersalt") != hashed

    # Test empty password
    empty_hash = hash_password("", salt)
    assert isinstance(empty_hash, bytes)
    assert len(empty_hash) == 64

    # Test empty salt
    empty_salt_hash = hash_password(password, b"")
    assert isinstance(empty_salt_hash, bytes)
    assert len(empty_salt_hash) == 64


def test_compare_password():
    # Test password comparison
    password = "TestPass123"
    salt = b"testsalt"

    # Generate hash
    hashed = hash_password(password, salt)

    # Convert to base64 for comparison
    salt_b64 = base64.b64encode(salt)
    hash_b64 = base64.b64encode(hashed)

    # Test correct password
    assert compare_password(password, hash_b64, salt_b64) is True

    # Test incorrect password
    assert compare_password("WrongPass123", hash_b64, salt_b64) is False

    # Test empty password
    assert compare_password("", hash_b64, salt_b64) is False

    # Test empty salt
    empty_salt_b64 = base64.b64encode(b"")
    assert compare_password(password, hash_b64, empty_salt_b64) is False
