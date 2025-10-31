from fastapi import FastAPI, HTTPException
import uvicorn
from pydantic import BaseModel
import connection_oracle.queries_to_oracle as oracle
from reports.reports import reports


class NewBook(BaseModel):
    title: str
    author: str


class NewUser(BaseModel):
    telegram_id: int
    telegram_name: str


class DeleteUser(BaseModel):
    telegram_id: int


class StrategiesUser(BaseModel):
    chat_id: int


app = FastAPI()


@app.post('/users', tags=['Пользователи'], summary='Довабить пользователя')
async def create_user(new_user: NewUser):
    try:
        result = await oracle.add_user(new_user.telegram_id, new_user.telegram_name)
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
        result = await oracle.delete_user(delete_user.telegram_id)

        return {
            'success': True,
            'id': result,
            'telegram_id': delete_user.telegram_id,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get('/strategies', tags=['Стратегии'], summary='Получить стратегии пользователя')
async def get_strategies_user(telegram_id):
    try:
        user_strategies = reports.get_user_strategies(telegram_id)
        print('fast_api', user_strategies)

        if not user_strategies:
            pass  # здесь будет функция для бд (Достанет все стратегии пользоваля)

        if not user_strategies:
            return {"success": True, "strategies": [], "message": "У вас пока нет активных стратегий."}

        return {
            "success": True,
            "telegram_id": telegram_id,
            "strategies": user_strategies
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post('/strategies', tags=['Стратегии'], summary='Добавить стратегию пользователю')
async def add_strategy_user(telegram_id, strategy, coin, timeframe):
    # TODO написать пакет для добавления стратегий пользователя
    try:
        return {
            'success': True,
            'id': 'id',
            'telegram_id': telegram_id,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
