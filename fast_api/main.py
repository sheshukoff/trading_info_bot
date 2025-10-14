from fastapi import FastAPI, HTTPException
import uvicorn
from pydantic import BaseModel
from connection_oracle.queries_to_oracle import add_user


class NewBook(BaseModel):
    title: str
    author: str


class NewUser(BaseModel):
    telegram_id: int
    telegram_name: str


app = FastAPI()

books = [
    {
        'id': 1,
        'title': 'Солнце мертвых',
        'author': 'И. Шмелёв',
    },
    {
        'id': 2,
        'title': 'Вишневый сад',
        'author': 'А. Чехов',
    }
]


@app.get('/books', tags=['Книги'], summary='Получить все книги')
def read_books():
    return books


@app.get('/books{book_id}', tags=['Книги'], summary='Получить одну книгу')
def get_book(book_id: int):
    for book in books:
        if book['id'] == book_id:
            return book
        raise HTTPException(status_code=404, detail='Книга не найдена')


@app.get('/new_books', tags=['Книги'], summary='Получить все книги')
def new_read_books():
    return books


@app.post('/new_book', tags=['Книги'])
def create_book(new_book: NewBook):
    books.append({
        'id': len(books) + 1,
        'title': new_book.title,
        'author': new_book.author
    })
    # add_user(8343423342, 'telegram_name')
    return {'success': True, 'message': 'Пользователь успешно добавлен'}


# @app.delete('/delete_users{telegram_id}')
# async def delete_user(new_user: NewUser):
#     try:
#         result = await delete_user(new_user.telegram_id)
#         return {'success': True, 'message': result}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


@app.post('/users{add_user}', tags=['Пользователи'], summary='Довабить пользователя')
async def create_user(new_user: NewUser):
    try:
        result = await add_user(new_user.telegram_id, new_user.telegram_name)
        return {'success': True, 'message': result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)

    # books.append({
    #     'id': len(books) + 1,
    #     'title': new_book.title,
    #     'author': new_book.author
    # })
