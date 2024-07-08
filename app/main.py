from fastapi import FastAPI,Depends,HTTPException,APIRouter
from schemes import TodoPost,Todo
from auth.utils import verify_token
from database import get_async_session
from sqlalchemy import insert,select,update,and_,delete
from models.models import todo
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from auth.auth import register_router


app=FastAPI(
    title="API for user todo",
    description="This is an API for managing user todos.",
    version="0.1.0"
)
router=APIRouter(tags=["USER Api"])
router_all=APIRouter(tags=["Superuser API"])


@router.post('/todos', response_model=Todo,summary="Create a post")
async def create_blog(new_blog: TodoPost, token: dict = Depends(verify_token), session: AsyncSession = Depends(get_async_session)):
    if token is None:
        raise HTTPException(status_code=401, detail="Not registered")
    user_id = token.get('user_id')
    new_blog_data = dict(new_blog)
    new_blog_data['user_id'] = user_id
    query = insert(todo).values(**new_blog_data).returning(todo)
    result = await session.execute(query)
    created_blog = result.fetchone()
    await session.commit()
    return created_blog


@router_all.get('/todos',response_model=List[Todo])
async def get_blog(token: dict = Depends(verify_token),session:AsyncSession=Depends(get_async_session)):
    print(token.get('is_superuser'))
    if token.get('is_superuser') is not True:
        raise HTTPException(status_code=403, detail="You do not have permission to access this resource")
    query=select(todo)
    blog_data=await session.execute(query)
    blog_data=blog_data.all()
    return blog_data


@router_all.get('/todos/{todo_id}', response_model=Todo)
async def blog_detail(todo_id: int, token:dict=Depends(verify_token),session: AsyncSession = Depends(get_async_session)):
    if token.get('is_superuser') is not True:
        raise HTTPException(status_code=403, detail="You do not have permission to access this resource")
    query = select(todo).where(todo.c.id == todo_id)
    result = await session.execute(query)
    todo_data = result.first()
    if not todo_data:
        raise HTTPException(status_code=404, detail="Todo not found")


    await session.commit()

    return todo_data


@router_all.delete('/todos/{todo_id}', response_model=Todo, summary="Delete any todo")
async def delete_any_todo(todo_id: int, token: dict = Depends(verify_token),
                          session: AsyncSession = Depends(get_async_session)):
    if token.get('is_superuser') is not True:
        raise HTTPException(status_code=403, detail="You do not have permission to delete this resource")

    query_delete = delete(todo).where(todo.c.id == todo_id).returning(todo)
    result_delete = await session.execute(query_delete)
    deleted_todo_data = result_delete.fetchone()

    if not deleted_todo_data:
        raise HTTPException(status_code=404, detail="Todo not found")

    await session.commit()
    return deleted_todo_data


@router.get('/user-todos', response_model=List[Todo],summary="Get user todos")
async def get_user_blogs(token: dict = Depends(verify_token), session: AsyncSession = Depends(get_async_session)):
    if token is None:
        raise HTTPException(status_code=401, detail="Not registered")

    user_id = token.get('user_id')

    query = select(todo).where(todo.c.user_id == user_id)
    result = await session.execute(query)
    user_todos = result.fetchall()

    return user_todos


@router.delete('/todo/{todo_id}', response_model=Todo, summary="Delete user todo")
async def delete_todo(todo_id: int, token: dict = Depends(verify_token), session: AsyncSession = Depends(get_async_session)):
    if token is None:
        raise HTTPException(status_code=401, detail="Not registered")
    user_id = token.get('user_id')
    query_check_owner = select(todo).where(and_(todo.c.user_id == user_id, todo.c.id == todo_id))
    result_check_owner = await session.execute(query_check_owner)
    todo_data = result_check_owner.fetchone()
    if not todo_data:
        raise HTTPException(status_code=404, detail="Todo not found or you are not authorized to delete it")
    query_delete = delete(todo).where(todo.c.id == todo_id).returning(todo)
    result_delete = await session.execute(query_delete)
    deleted_todo_data = result_delete.fetchone()
    await session.commit()
    return deleted_todo_data


@router.put('/todo/{todo_id}', response_model=Todo, summary="Updating user todos")
async def update_todo(todo_id: int, updated_todo: TodoPost, token: dict = Depends(verify_token), session: AsyncSession = Depends(get_async_session)):
    if token is None:
        raise HTTPException(status_code=401, detail="Not registered")
    user_id = token.get('user_id')
    query_check_owner = select(todo).where(and_(todo.c.user_id == user_id, todo.c.id == todo_id))
    result_check_owner = await session.execute(query_check_owner)
    todo_data = result_check_owner.fetchone()
    if not todo_data:
        raise HTTPException(status_code=404, detail="Blog not found or you are not authorized to update it")
    query_update = update(todo).where(todo.c.id == todo_id).values(
        plan=updated_todo.plan,
        description=updated_todo.description,
        status=updated_todo.status
    ).returning(todo)
    result_update = await session.execute(query_update)
    updated_todo_data = result_update.fetchone()
    await session.commit()
    return updated_todo_data






app.include_router(router)
app.include_router(router_all)
app.include_router(register_router)
