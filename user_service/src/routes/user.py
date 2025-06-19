from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from src.core.auth import get_current_user
from passlib.context import CryptContext
from src.core.auth import verify_password, create_access_token
from src.models import User
from src.database import SessionLocal, get_db
from src.utils.redis_client import redis_client

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

router = APIRouter(
    prefix="/api/user",
    tags=["user"]
)

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    db = SessionLocal()
    user = db.query(User).filter(User.username == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=403, detail="Invalid credentials")
    
    token = create_access_token({"sub": user.username, "role": user.is_admin and "admin" or "user"})
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "message": f"Login successfully with role {user.is_admin and 'admin' or 'user'}"
    }

@router.post("/register")
def register(form_data: OAuth2PasswordRequestForm = Depends()):
    db = SessionLocal()
    existing_user = db.query(User).filter(User.username == form_data.username).first()
    
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    hashed_password = pwd_context.hash(form_data.password)
    new_user = User(username=form_data.username, password=hashed_password, is_admin=False)
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {
        "message": "User registered successfully",
        "username": new_user.username
    }

@router.post("/logout")
def logout(token: str = Depends(oauth2_scheme)):
    redis_client.setex(f"blacklist:{token}", 900, "true")
    return {"message": "Log out successfully"}

@router.get("/user-info")
def get_profile(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "is_admin": current_user.is_admin,
    }

@router.get("/current_user")
def current_user(current_user: User = Depends(get_current_user)):
    return current_user

@router.get("/check_admin")
def check_admin(current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Access denied")
    return {"message": "You are an admin user"}
