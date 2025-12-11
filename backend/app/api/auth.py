"""Authentication API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional

from app.config import get_settings
from app.models.user import User, UserCreate, UserLogin, Token, UserRole
from app.services import get_database_service

router = APIRouter()
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
settings = get_settings()


def hash_password(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(hours=settings.JWT_EXPIRATION_HOURS))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Dependency to get current user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token = credentials.credentials
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        org_id: str = payload.get("org_id")
        role: str = payload.get("role")
        
        if user_id is None or org_id is None:
            raise credentials_exception
            
        return {
            "user_id": user_id,
            "org_id": org_id,
            "role": role,
            "email": payload.get("email")
        }
    except JWTError:
        raise credentials_exception


def require_role(allowed_roles: list[UserRole]):
    """Dependency factory to require specific roles."""
    async def role_checker(current_user: dict = Depends(get_current_user)):
        if current_user["role"] not in [r.value for r in allowed_roles]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    return role_checker


@router.post("/register", response_model=Token)
async def register(user_data: UserCreate):
    """Register a new user and organization."""
    db = get_database_service()
    
    # Check if user already exists
    existing_user = await db.get_user_by_email(user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create organization if not provided
    if user_data.org_id:
        org = await db.get_organization(user_data.org_id)
        if not org:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found"
            )
        org_id = user_data.org_id
    else:
        # Create new organization
        org = await db.create_organization(name=f"{user_data.email.split('@')[0]}'s Organization")
        org_id = org["id"]
    
    # Create user
    password_hash = hash_password(user_data.password)
    user = await db.create_user(
        org_id=org_id,
        email=user_data.email,
        role=user_data.role.value,
        password_hash=password_hash
    )
    
    # Create token
    access_token = create_access_token(
        data={
            "sub": user["id"],
            "org_id": org_id,
            "role": user["role"],
            "email": user["email"]
        }
    )
    
    return Token(
        access_token=access_token,
        user=User(
            id=user["id"],
            org_id=org_id,
            email=user["email"],
            role=user["role"],
            created_at=user["created_at"]
        )
    )


@router.post("/login", response_model=Token)
async def login(credentials: UserLogin):
    """Login and get access token."""
    db = get_database_service()
    
    user = await db.get_user_by_email(credentials.email)
    if not user or not verify_password(credentials.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    access_token = create_access_token(
        data={
            "sub": user["id"],
            "org_id": user["org_id"],
            "role": user["role"],
            "email": user["email"]
        }
    )
    
    return Token(
        access_token=access_token,
        user=User(
            id=user["id"],
            org_id=user["org_id"],
            email=user["email"],
            role=user["role"],
            created_at=user["created_at"]
        )
    )


@router.get("/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    """Get current user info."""
    return current_user
