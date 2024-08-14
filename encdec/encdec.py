from fastapi import FastAPI, HTTPException, Request
from cryptography.fernet import Fernet
import asyncio
from hashlib import sha256

app = FastAPI()


class AsyncMap:
    def __init__(self):
        self._map: dict[str, bytes] = {}
        self._lock = asyncio.Lock()

    async def get(self, key: str) -> bytes:
        async with self._lock:
            return self._map.get(key)

    async def set(self, key: str, value: bytes) -> None:
        async with self._lock:
            self._map[key] = value


# this is just stored in mem, could dump dict to disk if needed to persist shutdown
sha_key_map = AsyncMap()


@app.post("/encrypt")
async def encrypt_bytes(request: Request):
    key = Fernet.generate_key()
    cipher = Fernet(key)

    # Read the input bytes from the request body
    input_bytes = await request.body()

    # Encrypt the bytes
    encrypted_bytes = cipher.encrypt(input_bytes)

    # Store key with sha of encrypted bytes
    await sha_key_map.set(sha256(encrypted_bytes).hexdigest(), key)

    # Return the encrypted bytes as base64-encoded string
    return {"encrypted_data": encrypted_bytes.decode("utf-8")}


@app.post("/decrypt")
async def decrypt_bytes(request: Request):
    # Read the input data from the request body
    input_data = await request.json()
    encrypted_data = input_data.get("encrypted_data")

    if not encrypted_data:
        raise HTTPException(status_code=400, detail="No encrypted data provided")

    encrypted_bytes = encrypted_data.encode("utf-8")

    # Retrieve the key using the sha of encrypted bytes
    key = await sha_key_map.get(sha256(encrypted_bytes).hexdigest())

    if key is None:
        raise HTTPException(status_code=404, detail="Key not found for the provided encrypted data")

    cipher = Fernet(key)
    decrypted_bytes = cipher.decrypt(encrypted_bytes)

    return {"decrypted_data": decrypted_bytes.decode("utf-8")}
