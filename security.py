import database
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, Depends
from datetime import datetime, timedelta
from fastapi.security.oauth2 import OAuth2PasswordBearer

SECRET_KEY = "3d51a64b26ea1db3b5b725e1cb8d8g1248ea0780a6c7591b4e1a2a5f942171dd"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
validate_password = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return validate_password.verify(plain_password, hashed_password)

def hash_password(password):
    return validate_password.hash(password)

def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_tkn = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_tkn

async def login(username: str, password: str):
    user_db = await database.get_user(username, password)
    if not user_db:
        raise HTTPException(
            status_code=401,
            detail="Wrong username or password",
            headers={"Autentication": "not successfull"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token_data = {"sub": user_db.username}
    access_token = create_access_token(access_token_data, access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

async def authentication(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = await database.get_user(username)
    if user is None:
        raise credentials_exception
    return user

def active_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise credentials_exception
