from unittest.mock import MagicMock, patch

import pytest
import rsa as pyrsa
from Crypto.PublicKey import RSA

from libs import gmpy2_pkcs10aep_cipher, rsa


def test_gmpy2_pkcs10aep_cipher() -> None:
    rsa_key_pair = pyrsa.newkeys(2048)
    public_key = rsa_key_pair[0].save_pkcs1()
    private_key = rsa_key_pair[1].save_pkcs1()

    public_rsa_key = RSA.import_key(public_key)
    public_cipher_rsa2 = gmpy2_pkcs10aep_cipher.new(public_rsa_key)

    private_rsa_key = RSA.import_key(private_key)
    private_cipher_rsa = gmpy2_pkcs10aep_cipher.new(private_rsa_key)

    raw_text = "raw_text"
    raw_text_bytes = raw_text.encode()

    # RSA encryption by public key and decryption by private key
    encrypted_by_pub_key = public_cipher_rsa2.encrypt(message=raw_text_bytes)
    decrypted_by_pub_key = private_cipher_rsa.decrypt(encrypted_by_pub_key)
    assert decrypted_by_pub_key == raw_text_bytes

    # RSA encryption and decryption by private key
    encrypted_by_private_key = private_cipher_rsa.encrypt(message=raw_text_bytes)
    decrypted_by_private_key = private_cipher_rsa.decrypt(encrypted_by_private_key)
    assert decrypted_by_private_key == raw_text_bytes


def test_encrypt():
    # Generate test RSA key pair
    key = RSA.generate(2048)
    public_key = key.publickey().export_key().decode()
    text = "test text"

    # Mock dependencies
    mock_cipher_rsa = MagicMock()
    mock_cipher_rsa.encrypt.return_value = b"encrypted_aes_key"

    mock_aes = MagicMock()
    mock_aes.nonce = b"nonce"
    mock_aes.encrypt_and_digest.return_value = (b"ciphertext", b"tag")

    with patch("Crypto.Random.get_random_bytes", return_value=b"aes_key"), \
         patch("Crypto.Cipher.AES.new", return_value=mock_aes), \
         patch("libs.gmpy2_pkcs10aep_cipher.new", return_value=mock_cipher_rsa):

        # Test with string public key
        encrypted = rsa.encrypt(text, public_key)
        assert encrypted.startswith(rsa.prefix_hybrid)
        assert b"encrypted_aes_key" in encrypted
        assert b"nonce" in encrypted
        assert b"tag" in encrypted
        assert b"ciphertext" in encrypted

        # Test with bytes public key
        encrypted = rsa.encrypt(text, public_key.encode())
        assert encrypted.startswith(rsa.prefix_hybrid)


def test_decrypt_token_with_decoding():
    # Setup test data
    rsa_key = MagicMock()
    rsa_key.size_in_bytes.return_value = 256
    cipher_rsa = MagicMock()
    cipher_rsa.decrypt.return_value = b"decrypted_aes_key"

    mock_aes = MagicMock()
    mock_aes.decrypt_and_verify.return_value = b"decrypted text"

    # Test hybrid encryption
    encrypted_text = rsa.prefix_hybrid + b"encrypted_data" * 100

    with patch("Crypto.Cipher.AES.new", return_value=mock_aes):
        result = rsa.decrypt_token_with_decoding(encrypted_text, rsa_key, cipher_rsa)
        assert result == "decrypted text"

        # Verify AES decryption called correctly
        mock_aes.decrypt_and_verify.assert_called_once()

    # Test non-hybrid encryption
    encrypted_text = b"encrypted_data"
    cipher_rsa.decrypt.return_value = b"decrypted text"
    result = rsa.decrypt_token_with_decoding(encrypted_text, rsa_key, cipher_rsa)
    assert result == "decrypted text"


def test_encrypt_decrypt_integration():
    # Generate real RSA key pair
    rsa_key_pair = pyrsa.newkeys(2048)
    public_key = rsa_key_pair[0].save_pkcs1()
    private_key = rsa_key_pair[1].save_pkcs1()

    test_text = "test message"
    redis_mock = MagicMock()
    redis_mock.get.return_value = None

    # Encrypt with public key
    encrypted = rsa.encrypt(test_text, public_key)

    # Setup mocks for decryption
    with patch('libs.rsa.storage.load', return_value=private_key), \
         patch('libs.rsa.redis_client', redis_mock):

        decrypted = rsa.decrypt(encrypted, "test_tenant")
        assert decrypted == test_text

        # Verify redis caching
        redis_mock.setex.assert_called_once()

        # Test redis cache hit
        redis_mock.get.return_value = private_key
        decrypted = rsa.decrypt(encrypted, "test_tenant")
        assert decrypted == test_text


def test_decrypt_with_invalid_tenant():
    redis_mock = MagicMock()
    redis_mock.get.return_value = None

    with patch('libs.rsa.storage.load', side_effect=FileNotFoundError()), \
         patch('libs.rsa.redis_client', redis_mock):
        with pytest.raises(rsa.PrivkeyNotFoundError) as exc_info:
            rsa.decrypt(b"test", "invalid_tenant")

    assert "Private key not found" in str(exc_info.value)
