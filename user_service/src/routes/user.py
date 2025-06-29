from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from src.middleware.auth import get_current_user
from passlib.context import CryptContext
from src.middleware.auth import verify_password, create_access_token
from src.models import User
from src.database import SessionLocal
from src.middleware.ratelimit import RateLimiter

# Rate limiter to limit requests to 10 per minute globally
global_limiter = RateLimiter(times=10, seconds=60)

# pwd_context for hashing passwords
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

# Create a router for user-related endpoints
router = APIRouter(prefix="/api/user", tags=["user"])


# This endpoint allows a user to log in and receive a JWT token
@router.post("/login", dependencies=[Depends(global_limiter)])
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    db = SessionLocal()
    user = db.query(User).filter(User.username == form_data.username).first()

    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=403, detail="Invalid credentials")

    token = create_access_token(
        {"sub": user.username, "role": user.is_admin and "admin" or "user"}
    )

    role = "admin" if user.is_admin else "user"
    return {
        "access_token": token,
        "token_type": "bearer",
        "message": f"Login successfully with role {role}",
    }


# This endpoint allows a new user to register
@router.post("/register", dependencies=[Depends(global_limiter)])
def register(form_data: OAuth2PasswordRequestForm = Depends()):
    db = SessionLocal()

    # Check if the username already exists
    existing_user = (
        db.query(User)
        .filter(User.username == form_data.username)
        .first()
    )

    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    hashed_password = pwd_context.hash(form_data.password)
    new_user = User(
        username=form_data.username, password=hashed_password, is_admin=False
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "User registered successfully",
        "username": new_user.username,
    }


# This endpoint retrieves the current user's information
@router.get("/user-info", dependencies=[Depends(global_limiter)])
def get_profile(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "is_admin": current_user.is_admin,
    }
