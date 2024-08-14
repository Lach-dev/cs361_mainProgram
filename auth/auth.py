from fastapi import FastAPI, HTTPException, status, Depends
from pydantic import BaseModel
from passlib.context import CryptContext

app = FastAPI()

# In-memory user storage
users = {}

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


class User(BaseModel):
    username: str
    password: str


class UserInDB(User):
    hashed_password: str


@app.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user: User):
    if user.username in users:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists.")
    hashed_password = get_password_hash(user.password)
    users[user.username] = UserInDB(username=user.username, hashed_password=hashed_password)
    return {"message": "Registration successful."}


@app.post("/login")
async def login(user: User):
    user_in_db = users.get(user.username)
    if not user_in_db or not verify_password(user.password, user_in_db.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password.")
    return {"message": "Login successful."}
