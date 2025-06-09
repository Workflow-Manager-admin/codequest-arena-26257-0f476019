"""
FastAPI router for user authentication (JWT-based).
Handles:
- /auth/register: User registration (demo, in-memory store)
- /auth/login: Login route, returns JWT on success.
- /auth/me: Get current authenticated user.
Implements demo user store, password hashing, JWT helpers.
"""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from ..services.auth_service import (
    DemoUserStore,
    verify_password,
    create_jwt_token,
    decode_jwt_token,
)

router = APIRouter()
user_store = DemoUserStore()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# PUBLIC_INTERFACE


class UserRegisterDTO(BaseModel):
    username: str
    password: str


# PUBLIC_INTERFACE
class UserLoginDTO(BaseModel):
    username: str
    password: str


# PUBLIC_INTERFACE
class UserInfoDTO(BaseModel):
    username: str


# PUBLIC_INTERFACE
class TokenDTO(BaseModel):
    access_token: str
    token_type: str = "bearer"


# Dependency to get current user from token
def get_current_user(token: str = Depends(oauth2_scheme)) -> UserInfoDTO:
    payload = decode_jwt_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    username = payload["sub"]
    if not user_store.user_exists(username):
        raise HTTPException(status_code=401, detail="User not found")
    return UserInfoDTO(username=username)


# PUBLIC_INTERFACE
@router.post("/register", response_model=UserInfoDTO, tags=["Auth"])
def register(data: UserRegisterDTO):
    if user_store.user_exists(data.username):
        raise HTTPException(status_code=409, detail="User already exists")
    user_store.create_user(data.username, data.password)
    return UserInfoDTO(username=data.username)


# PUBLIC_INTERFACE
@router.post("/login", response_model=TokenDTO, tags=["Auth"])
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    username = form_data.username
    password = form_data.password
    if not user_store.user_exists(username):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    user = user_store.get_user(username)
    if not verify_password(password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = create_jwt_token(username)
    return TokenDTO(access_token=access_token)


# PUBLIC_INTERFACE
@router.get("/me", response_model=UserInfoDTO, tags=["Auth"])
def me(current_user: UserInfoDTO = Depends(get_current_user)):
    return current_user
