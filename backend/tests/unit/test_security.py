"""
Unit tests for security utilities.
"""
import pytest
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_access_token,
    decode_refresh_token,
    encrypt_credential,
    decrypt_credential,
    hash_password,
    verify_password,
)
from jose import JWTError


class TestPasswordHashing:
    def test_hash_and_verify(self):
        password = "StrongPassword123!"
        hashed = hash_password(password)
        assert hashed != password
        assert verify_password(password, hashed)

    def test_wrong_password_fails(self):
        hashed = hash_password("correct_password")
        assert not verify_password("wrong_password", hashed)

    def test_hash_is_unique(self):
        h1 = hash_password("same_password")
        h2 = hash_password("same_password")
        assert h1 != h2  # bcrypt salts are different


class TestJWT:
    def test_access_token_round_trip(self):
        user_id = "test-user-123"
        token = create_access_token(user_id)
        decoded_id = decode_access_token(token)
        assert decoded_id == user_id

    def test_refresh_token_round_trip(self):
        user_id = "user-456"
        token = create_refresh_token(user_id)
        decoded_id = decode_refresh_token(token)
        assert decoded_id == user_id

    def test_access_token_wrong_type_rejected(self):
        """A refresh token should not be accepted as an access token."""
        user_id = "user-789"
        refresh = create_refresh_token(user_id)
        with pytest.raises(JWTError):
            decode_access_token(refresh)

    def test_invalid_token_raises(self):
        with pytest.raises(JWTError):
            decode_access_token("not.a.valid.jwt")


class TestCredentialEncryption:
    def test_encrypt_decrypt_round_trip(self):
        original = "super_secret_oauth_token"
        encrypted = encrypt_credential(original)
        assert encrypted != original
        decrypted = decrypt_credential(encrypted)
        assert decrypted == original

    def test_different_values_produce_different_ciphertext(self):
        enc1 = encrypt_credential("value_one")
        enc2 = encrypt_credential("value_two")
        assert enc1 != enc2
