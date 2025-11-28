from fastapi import FastAPI, HTTPException
import uvicorn
from pydantic import BaseModel
import connection_oracle.delete_queries as delete_oracle
import connection_oracle.insert_queries as insert_oracle
import connection_oracle.get_queries as get_oracle
from telegram.handlers import reports


class NewBook(BaseModel):
    title: str
    author: str


class NewUser(BaseModel):
    telegram_id: int
    telegram_name: str


class DeleteUser(BaseModel):
    telegram_id: int


app = FastAPI()


@app.post('/users', tags=['Пользователи'], summary='Довабить пользователя')
async def create_user(new_user: NewUser):
    try:
        result = await insert_oracle.insert_user(new_user.telegram_id, new_user.telegram_name)
        return {
            'success': True,
            'id': result,
            'telegram_id': new_user.telegram_id,
            'telegram_name': new_user.telegram_name
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete('/users', tags=['Пользователи'], summary='Удалить пользователя')
async def delete_user(delete_user: DeleteUser):
    try:
        result = await delete_oracle.delete_user(delete_user.telegram_id)

        return {
            'success': True,
            'id': result,
            'telegram_id': delete_user.telegram_id,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get('/strategies', tags=['Стратегии'], summary='Получить стратегии пользователя')
async def get_strategies_user(telegram_id: int):
    try:
        result = await get_oracle.get_user_strategies(telegram_id)

        if not result:
            return {"success": False, "strategies": [], "message": "У вас пока нет активных стратегий."}

        return {
            "success": True,
            "telegram_id": telegram_id,
            "strategies": result
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
