import os
from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from ldap3 import Server, Connection, ALL, Tls
import ssl

app = FastAPI(
    title="LDAP Authentication API with JWT",
    description="Educational FastAPI + OpenLDAP + JWT Authentication Service with Fail2Ban & TLS Protection",
    version="1.2.0",
)

# Enable CORS for frontend integration (Vue.js, etc.)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Access log middleware for Fail2Ban HTTP Flood detection
@app.middleware("http")
async def fail2ban_access_log_middleware(request: Request, call_next):
    client_ip = request.client.host if request.client else "127.0.0.1"
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        client_ip = forwarded.split(",")[0].strip()

    response = await call_next(request)

    # Standard Apache/Nginx combined log format for Fail2Ban
    log_line = f'{client_ip} - - [{datetime.now().strftime("%d/%b/%Y:%H:%M:%S +0000")}] "{request.method} {request.url.path} HTTP/1.1" {response.status_code}\n'
    try:
        os.makedirs("/var/log/ldap-auth", exist_ok=True)
        with open("/var/log/ldap-auth/access.log", "a") as f:
            f.write(log_line)
    except Exception:
        pass

    return response

LDAP_HOST = os.getenv("LDAP_HOST", "openldap")
LDAP_PORT = int(os.getenv("LDAP_PORT", "389"))
LDAP_BASE_DN = os.getenv("LDAP_BASE_DN", "dc=example,dc=com")
LDAP_USE_TLS = os.getenv("LDAP_USE_TLS", "false").lower() in ("true", "1", "yes") or LDAP_PORT == 636

# JWT Configuration
JWT_SECRET = os.getenv("JWT_SECRET", "super-secret-jwt-key-for-ldap-cybersecurity-lab-2026")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRATION_MINUTES = int(os.getenv("JWT_EXPIRATION_MINUTES", "120"))

security = HTTPBearer(auto_error=False)


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    authenticated: bool
    username: str
    dn: str
    access_token: str
    token_type: str = "bearer"
    expires_in: int


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=JWT_EXPIRATION_MINUTES)
    to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc)})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt


@app.get("/health")
def health():
    return {"status": "ok", "service": "ldap-auth-api"}


@app.post("/login", response_model=TokenResponse)
def login(request: LoginRequest):
    tls_config = None
    if LDAP_USE_TLS:
        tls_config = Tls(validate=ssl.CERT_NONE)

    server = Server(
        LDAP_HOST,
        port=LDAP_PORT,
        use_ssl=LDAP_USE_TLS,
        tls=tls_config,
        get_info=ALL,
    )

    user_dn = (
        f"uid={request.username},"
        f"ou=users,"
        f"{LDAP_BASE_DN}"
    )

    connection = Connection(
        server,
        user=user_dn,
        password=request.password,
        auto_bind=False,
    )

    try:
        if connection.bind():
            # Generate JWT Token for authenticated user
            token_data = {
                "sub": request.username,
                "username": request.username,
                "dn": user_dn,
                "role": "student"
            }
            expires_delta = timedelta(minutes=JWT_EXPIRATION_MINUTES)
            token = create_access_token(data=token_data, expires_delta=expires_delta)

            return {
                "authenticated": True,
                "username": request.username,
                "dn": user_dn,
                "access_token": token,
                "token_type": "bearer",
                "expires_in": JWT_EXPIRATION_MINUTES * 60,
            }

        # Log failed authentication attempts for security tracking
        try:
            with open("/var/log/ldap-auth/ldap_tls.log", "a") as f:
                f.write(f'{datetime.now().strftime("%d/%b/%Y:%H:%M:%S +0000")} - LDAP Auth Failed for user={request.username}\n')
        except Exception:
            pass

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales LDAP inválidas. Verifique usuario o contraseña.",
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error conectando al servidor LDAP: {str(e)}",
        )
    finally:
        try:
            connection.unbind()
        except Exception:
            pass


@app.get("/verify-token")
def verify_token(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se proporcionó Bearer token en el encabezado Authorization",
        )
    token = credentials.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return {"valid": True, "payload": payload}
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="El token JWT ha expirado",
        )
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token JWT inválido: {str(e)}",
        )
