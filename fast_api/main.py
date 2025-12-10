from fastapi import FastAPI, HTTPException
import uvicorn
from pydantic import BaseModel
from contextlib import asynccontextmanager
import connection_oracle.delete_queries as delete_oracle
import connection_oracle.insert_queries as insert_oracle
import connection_oracle.get_queries as get_oracle
from scheduler.scheduler import DynamicSchedulerManager
from connection_okx.aiohttp_get_data import get_history_data_okx, get_local_data_okx


scheduler = DynamicSchedulerManager()

AVAILABLE_FUNCTIONS = {
    "get_history_data_okx": get_history_data_okx,
    "get_local_data_okx": get_local_data_okx
}


class NewUser(BaseModel):
    telegram_id: int
    telegram_name: str


class DeleteUser(BaseModel):
    telegram_id: int


class AddJob(BaseModel):
    load_function: str
    ticker: str
    timeframe: str


class RemoveJob(BaseModel):
    job_id: str


class UpdateFunction(BaseModel):
    new_load_function: str
    ticker: str
    timeframe: str


@asynccontextmanager
async def lifespan(app: FastAPI):
    await scheduler.start()
    yield

app = FastAPI(lifespan=lifespan)


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


@app.post('/add_job', tags=['Работа'], summary='Довабить работу планировщику')
async def create_job(add_job: AddJob):
    try:
        if add_job.load_function not in AVAILABLE_FUNCTIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Функция '{add_job.load_function}' не найдена"
            )

        load_function = AVAILABLE_FUNCTIONS[add_job.load_function]
        scheduler.add_job(load_function, add_job.ticker, add_job.timeframe)
        return {
            'success': True,
            'load_function': add_job.load_function,
            'ticker': add_job.ticker,
            'timeframe': add_job.timeframe
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete('/remove_job', tags=['Работа'], summary='Удалить работу планировщику')
async def delete_job(remove_job: RemoveJob):
    try:
        scheduler.remove_job(remove_job.job_id)
        return {
            'success': True,
            'job_id': remove_job.job_id,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put('/change_load_function', tags=['Работа'], summary='Изменить планировщику функцию выгрузки данных')
async def change_load_function(update_function: UpdateFunction):
    try:
        if update_function.new_load_function not in AVAILABLE_FUNCTIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Функция '{update_function.new_load_function}' не найдена"
            )

        new_load_function = AVAILABLE_FUNCTIONS[update_function.new_load_function]
        scheduler.change_load_function(new_load_function, update_function.ticker, update_function.timeframe)

        return {
            'success': True,
            'new_load_function': update_function.new_load_function,
            'ticker': update_function.ticker,
            'timeframe': update_function.timeframe
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
