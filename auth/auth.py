import jwt
from .schemes import User, UserInDB, UserInfo,UserLogin
from datetime import datetime,timedelta
from database import  get_async_session
from  config import SECRET
from sqlalchemy import select,insert
from sqlalchemy.ext.asyncio import  AsyncSession
from sqlalchemy.exc import NoResultFound
from fastapi import HTTPException,Depends,APIRouter
from dotenv import load_dotenv
from passlib.context import CryptContext
from  models.models import  userdata
from .utils import generate_token,verify_token

load_dotenv()

register_router=APIRouter(tags=['Auth API'])


pwd_context=CryptContext(schemes=['bcrypt'],deprecated='auto')


@register_router.post('/register')
async def register(user:User,session:AsyncSession=Depends(get_async_session)):
    if user.password1==user.password2:
        if not select(userdata).where(userdata.c.username==user.username).exists:
            raise HTTPException(status_code=400,detail="Username already in user")
        if not select(userdata).where(userdata.c.email==user.email).exists:
            raise HTTPException(status_code=400,detail="Email already in user")
        password=pwd_context.hash(user.password1)
        user_in_db=UserInDB(**dict(user),password=password,registered_date=datetime.utcnow())
        query=insert(userdata).values(**dict(user_in_db))
        await session.execute(query)
        await session.commit()
        user_info=UserInfo(**dict(user))
        return dict(user_info)


@register_router.post('/login')
async def login(user:UserLogin,session:AsyncSession=Depends(get_async_session)):
    query=select(userdata).where(userdata.c.username==user.username)
    user_data=await session.execute(query)
    try:
     user_data=user_data.one()
    except NoResultFound:
        raise HTTPException(status_code=404,detail="username or pas is incorrect")
    if pwd_context.verify(user.password,user_data.password):
        token=generate_token(user_data.id,user_data.is_superuser)
        return token
    else:
        raise HTTPException(status_code=404,detail='username or password is incorrect')


@register_router.post('/refresh-token')
async def refresh_token(refresh_token: str):
    try:
        payload = jwt.decode(refresh_token, SECRET, algorithms=['HS256'])
        if payload['type'] != 'refresh':
            raise HTTPException(status_code=401, detail="Invalid token type")

        user_id = payload.get('user_id')
        is_superuser=payload.get('is_superuser')
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")

        new_tokens = generate_token(user_id,is_superuser)
        return new_tokens

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh token is expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")


@register_router.get('/user-info',response_model=UserInfo,summary="Identification of user data using tokens")
async def user_info(token:dict=Depends(verify_token),session:AsyncSession=Depends(get_async_session)):
    if token is None:
        raise HTTPException(status_code=401,detail="Not registered")
    user_id=token.get('user_id')
    query=select(userdata).where(userdata.c.id == user_id)
    user__data=await session.execute(query)
    try:
        user_data=user__data.one()
        return user_data
    except NoResultFound:
        raise HTTPException(status_code=404,detail="user nof found")





