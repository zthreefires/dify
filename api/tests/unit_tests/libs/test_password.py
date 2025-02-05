import base64
import binascii

import pytest

from libs.password import compare_password, hash_password, valid_password


def test_valid_password_success():
    # Valid passwords
    assert valid_password("Password123") == "Password123"
    assert valid_password("abc12345") == "abc12345"
    assert valid_password("1234abcd") == "1234abcd"
    assert valid_password("Pass1234!@#$") == "Pass1234!@#$"


def test_valid_password_failure():
    # Invalid passwords
    with pytest.raises(ValueError):
        valid_password("short1")  # Too short

    with pytest.raises(ValueError):
        valid_password("onlyletters")  # No numbers

    with pytest.raises(ValueError):
        valid_password("12345678")  # No letters

    with pytest.raises(ValueError):
        valid_password("")  # Empty string


def test_hash_password():
    password = "TestPass123"
    salt = b"testsalt"

    # Hash should be deterministic for same input
    hash1 = hash_password(password, salt)
    hash2 = hash_password(password, salt)
    assert hash1 == hash2

    # Different passwords should produce different hashes
    hash3 = hash_password("DifferentPass123", salt)
    assert hash1 != hash3

    # Different salts should produce different hashes
    hash4 = hash_password(password, b"differentsalt")
    assert hash1 != hash4

    # Verify output is bytes
    assert isinstance(hash1, bytes)

    # Verify we can decode the output as hex
    try:
        binascii.unhexlify(hash1)
    except binascii.Error:
        pytest.fail("Hash output is not valid hex")


def test_compare_password():
    password = "TestPass123"
    salt = b"testsalt"

    # Generate hash
    hashed = hash_password(password, salt)

    # Convert to base64 for storage format
    hashed_b64 = base64.b64encode(hashed)
    salt_b64 = base64.b64encode(salt)

    # Correct password should match
    assert compare_password(password, hashed_b64, salt_b64)

    # Wrong password should not match
    assert not compare_password("WrongPass123", hashed_b64, salt_b64)

    # Empty password should not match
    assert not compare_password("", hashed_b64, salt_b64)

    # Wrong salt should not match
    wrong_salt = base64.b64encode(b"wrongsalt")
    assert not compare_password(password, hashed_b64, wrong_salt)
