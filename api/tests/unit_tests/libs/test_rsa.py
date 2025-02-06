from Crypto.PublicKey import RSA

from libs import gmpy2_pkcs10aep_cipher, rsa


def test_gmpy2_pkcs10aep_cipher() -> None:
    rsa_key_pair = RSA.generate(2048)
    public_key = rsa_key_pair.publickey()
    private_key = rsa_key_pair

    public_cipher_rsa = gmpy2_pkcs10aep_cipher.new(public_key)
    private_cipher_rsa = gmpy2_pkcs10aep_cipher.new(private_key)

    raw_text = "raw_text"
    raw_text_bytes = raw_text.encode()

    # RSA encryption by public key and decryption by private key
    encrypted_by_pub_key = public_cipher_rsa.encrypt(message=raw_text_bytes)
    decrypted_by_pub_key = private_cipher_rsa.decrypt(encrypted_by_pub_key)
    assert decrypted_by_pub_key == raw_text_bytes

    # RSA encryption and decryption by private key
    encrypted_by_private_key = private_cipher_rsa.encrypt(message=raw_text_bytes)
    decrypted_by_private_key = private_cipher_rsa.decrypt(encrypted_by_private_key)
    assert decrypted_by_private_key == raw_text_bytes


def test_encrypt():
    # Generate test key pair
    private_key = RSA.generate(2048)
    public_key = private_key.publickey()

    # Test with public key in PEM format
    public_key_pem = public_key.export_key()
    text = "test message"

    encrypted = rsa.encrypt(text, public_key_pem)
    assert encrypted.startswith(rsa.prefix_hybrid)

    # Test with bytes public key
    encrypted = rsa.encrypt(text, public_key_pem)
    assert encrypted.startswith(rsa.prefix_hybrid)

    # Test with empty text
    encrypted = rsa.encrypt("", public_key_pem)
    assert encrypted.startswith(rsa.prefix_hybrid)

    # Test with special characters
    text_special = "!@#$%^&*()"
    encrypted = rsa.encrypt(text_special, public_key_pem)
    assert encrypted.startswith(rsa.prefix_hybrid)


def test_decrypt_token_with_decoding():
    # Generate test key pair
    private_key = RSA.generate(2048)
    public_key = private_key.publickey()

    # Test text
    text = "test message"

    # Encrypt using public key
    encrypted = rsa.encrypt(text, public_key.export_key())

    # Setup decryption objects
    cipher_rsa = gmpy2_pkcs10aep_cipher.new(private_key)

    # Test hybrid decryption
    decrypted = rsa.decrypt_token_with_decoding(encrypted, private_key, cipher_rsa)
    assert decrypted == text

    # Test decryption of non-hybrid message
    non_hybrid = cipher_rsa.encrypt(text.encode())
    decrypted = rsa.decrypt_token_with_decoding(non_hybrid, private_key, cipher_rsa)
    assert decrypted == text

    # Test empty message
    empty_text = ""
    encrypted_empty = rsa.encrypt(empty_text, public_key.export_key())
    decrypted = rsa.decrypt_token_with_decoding(encrypted_empty, private_key, cipher_rsa)
    assert decrypted == empty_text

    # Test special characters
    special_text = "!@#$%^&*()"
    encrypted_special = rsa.encrypt(special_text, public_key.export_key())
    decrypted = rsa.decrypt_token_with_decoding(encrypted_special, private_key, cipher_rsa)
    assert decrypted == special_text


def test_encrypt_decrypt_cycle():
    # Generate test key pair
    private_key = RSA.generate(2048)
    public_key = private_key.publickey()

    # Test various message types
    test_messages = [
        "Regular text",
        "",  # Empty string
        "!@#$%^&*()",  # Special characters
        "Unicode 你好",  # Unicode characters
        "a" * 1000,  # Long string
    ]

    for message in test_messages:
        # Encrypt
        encrypted = rsa.encrypt(message, public_key.export_key())

        # Setup decryption
        cipher_rsa = gmpy2_pkcs10aep_cipher.new(private_key)

        # Decrypt
        decrypted = rsa.decrypt_token_with_decoding(encrypted, private_key, cipher_rsa)

        # Verify
        assert decrypted == message
