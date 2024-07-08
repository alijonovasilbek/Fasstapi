import secrets
from datetime import datetime,timedelta
import jwt
from fastapi import Depends,HTTPException
from config import SECRET
from fastapi.security import HTTPBearer,HTTPAuthorizationCredentials


security=HTTPBearer()


def generate_token(use_id:int,is_superuser:bool):
    jti_access=str(secrets.token_urlsafe(32))
    jti_refresh=str(secrets.token_urlsafe(32))

    payload_access={
        'type':"access",
        'exp':datetime.utcnow()+timedelta(minutes=30),
        'user_id':use_id,
        'is_superuser': is_superuser,
        'jti':jti_access
    }

    payload_refresh = {
        'type': "refresh",
        'exp': datetime.utcnow() + timedelta(days=1),
        'user_id': use_id,
        'is_superuser': is_superuser,
        'jti': jti_refresh
    }
    access_token=jwt.encode(payload_access,SECRET,algorithm='HS256')
    refresh_token=jwt.encode(payload_refresh,SECRET,algorithm='HS256')

    return {
        'access':access_token,
        'refresh':refresh_token
    }


def verify_token(credentials:HTTPAuthorizationCredentials=Depends(security)):
    try:
     token=credentials.credentials
     payload=jwt.decode(token,SECRET,algorithms=['HS256'])
     return payload

    except  jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401,detail="Token is expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401,detail="token is invalid")

