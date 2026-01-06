from fastapi import FastAPI, HTTPException
import uvicorn
from pydantic import BaseModel
from contextlib import asynccontextmanager
import connection_oracle.delete_queries as delete_oracle
import connection_oracle.insert_queries as insert_oracle
import connection_oracle.get_queries as get_oracle
from scheduler.scheduler import DynamicSchedulerManager
from connection_okx.aiohttp_get_data import get_data_okx


scheduler = DynamicSchedulerManager()

AVAILABLE_FUNCTIONS = {
    "get_data_okx": get_data_okx
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


class InsertUsingStrategy(BaseModel):
    telegram_id: int
    strategy: str
    ticker: str
    timeframe: str


class DeleteUsingStrategy(BaseModel):
    telegram_id: int
    strategy: str
    ticker: str
    timeframe: str


class DeleteUserAllStrategies(BaseModel):
    telegram_id: int


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


@app.post('/using_strategy', tags=['Используемые стратегии'], summary='Довабить стратегию пользователю')
async def create_using_strategy(add_us: InsertUsingStrategy):
    try:
        result = await insert_oracle.insert_using_strategy(
            add_us.telegram_id, add_us.strategy, add_us.ticker, add_us.timeframe
        )

        return {
            "success": True,
            "telegram_id": add_us.telegram_id,
            "strategy": add_us.strategy,
            "ticker": add_us.ticker,
            "timeframe": add_us.timeframe,
            "strategies": result
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete('/using_strategy', tags=['Используемые стратегии'], summary='Удалить используемую стратегию')
async def delete_using_strategy(remove_strategy: DeleteUsingStrategy):
    try:
        result = await delete_oracle.delete_user_strategy(
            remove_strategy.telegram_id,
            remove_strategy.strategy,
            remove_strategy.ticker,
            remove_strategy.timeframe
        )

        return {
            "success": True,
            "telegram_id": remove_strategy.telegram_id,
            "strategy": remove_strategy.strategy,
            "ticker": remove_strategy.ticker,
            "timeframe": remove_strategy.timeframe,
            "strategies": result
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete('/using_strategy{user}', tags=['Используемые стратегии'], summary='Удалить все стратегии пользователя')
async def delete_all_using_strategy(remove_all_strategy: DeleteUserAllStrategies):
    try:
        result = await delete_oracle.delete_user_all_strategies(remove_all_strategy.telegram_id)

        return {
            "success": True,
            "telegram_id": remove_all_strategy.telegram_id,
            "strategies": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
