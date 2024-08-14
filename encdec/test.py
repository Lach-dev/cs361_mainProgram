from fastapi.testclient import TestClient
from app import app

client = TestClient(app)


def test_encrypt_decrypt():
    # Define the data to be encrypted
    original_data = b"Test data for encryption"

    # Encrypt the data
    response = client.post("/encrypt", data=original_data)
    assert response.status_code == 200
    encrypted_data = response.json()["encrypted_data"]

    # Decrypt the data
    response = client.post("/decrypt", json={"encrypted_data": encrypted_data})
    assert response.status_code == 200
    decrypted_data = response.json()["decrypted_data"]

    # Verify the decrypted data matches the original data
    assert decrypted_data == original_data.decode("utf-8")


def test_encrypt_decrypt_file():
    # read requirements file and encrypt it
    original_data = open("requirements.txt", "rb").read()

    # Encrypt the data
    response = client.post("/encrypt", data=original_data)
    assert response.status_code == 200
    encrypted_data = response.json()["encrypted_data"]

    # Decrypt the data
    response = client.post("/decrypt", json={"encrypted_data": encrypted_data})
    assert response.status_code == 200
    decrypted_data = response.json()["decrypted_data"]

    # Verify the decrypted data matches the original data
    assert decrypted_data == original_data.decode("utf-8")


def test_decrypt_never_seen():
    # Attempt to decrypt with invalid data
    response = client.post("/decrypt", json={"encrypted_data": "new_data"})
    assert response.status_code == 404


def test_decrypt_empty_data_field():
    # Attempt to decrypt with invalid data
    response = client.post("/decrypt", json={"encrypted_data": ""})
    assert response.status_code == 400


def test_encrypt_empty_body():
    # Attempt to encrypt with an empty body
    response = client.post("/encrypt", data=b"")
    assert response.status_code == 200
    encrypted_data = response.json()["encrypted_data"]
    assert encrypted_data != ""


def test_decrypt_no_data():
    # Attempt to decrypt without providing encrypted_data
    response = client.post("/decrypt", json={})
    assert response.status_code == 400