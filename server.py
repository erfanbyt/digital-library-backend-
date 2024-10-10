import psycopg2
from typing import List, Tuple
from pydantic import BaseModel
import uvicorn
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
import requests
from create_book_table import extract_book_data_from_URL


API_KEY = "AIzaSyBVzyNN5zRjluikDh1EfaN5XRT7c0oCz4g"


# this will enforce certain types for the book-related data
class Book(BaseModel):
    id: int = None
    volume_id: str
    title: str
    authors: str=None
    thumbnail: str=None
    state: int=None  # 0: complete 1: unfinished 2: wishlist
    rating: int=None    


class UpdateRatingReqeustBody(BaseModel):
      volume_id: str
      new_rating: int


class UpdateStateRequestBody(BaseModel):
      volume_id: str
      new_state: int


app = FastAPI(debug=True)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/status")
async def check_status():
    return "hello world"


@app.get("/books", response_model=List[Book], status_code=status.HTTP_200_OK)
async def get_books():
        conn = psycopg2.connect(
            database="digital_lib_db",
            user="postgres",
            password="13771377",
            host="0.0.0.0")
        
        cur = conn.cursor()
        cur.execute("SELECT * FROM books ORDER BY id DESC")
        rows = cur.fetchall()

        books = []
        for row in rows:
            book = Book(
                id=row[0],
                volume_id=row[1],
                title=row[2],
                authors=row[3],
                thumbnail=row[4],
                state=row[5],
                rating=row[6]
            )
            books.append(book)


        cur.close()
        conn.close()

        return books

"""
improvements here:
1. add a function to get names of all the existing books and add the book if the book doesn't already exist
"""

@app.post("/books-ISBN", status_code=status.HTTP_201_CREATED)
async def get_book_info_from_googleBooks_ISBN(isbn):
        url = f'https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}&key={API_KEY}'
        book_data = extract_book_data_from_URL(url)

        conn = psycopg2.connect(
            database="digital_lib_db",
            user="postgres",
            password="13771377",
            host="0.0.0.0")
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO BOOKS 
            (volume_id, title, authors, thumbnail)
            VALUES (%s, %s, %s, %s)
            """, 
            (book_data["volume_id"], book_data["title"], book_data["authors"], book_data["thumbnail"])
            )

        conn.commit()
        cur.close()
        conn.close()
        
        return 


@app.post("/books", status_code=status.HTTP_201_CREATED)
async def new_books(book: Book):
        conn = psycopg2.connect(
            database="digital_lib_db",
            user="postgres",
            password="13771377",
            host="0.0.0.0")
        cur = conn.cursor()
        cur.execute(f"INSERT INTO books (volume_id, title, authors, thumbnail, state) VALUES ('{book.volume_id}', '{book.title}', '{book.authors}', '{book.thumbnail}', '{book.state}')")
        
        conn.commit()
        cur.close()
        conn.close()

        return

@app.put("/books/update_rating", status_code=status.HTTP_200_OK)
async def update_rating(update_rating_body: UpdateRatingReqeustBody):
        conn = psycopg2.connect(
            database="digital_lib_db",
            user="postgres",
            password="13771377",
            host="0.0.0.0")
        cur = conn.cursor()

        cur.execute(f"UPDATE books SET rating={update_rating_body.new_rating} WHERE volume_id='{update_rating_body.volume_id}'")
        conn.commit()
        cur.close()
        conn.close()

        return 


@app.put("/books/update_book_state", status_code=status.HTTP_200_OK)
async def update_book_state(update_state_request_body: UpdateStateRequestBody):
        conn = psycopg2.connect(
            database="digital_lib_db",
            user="postgres",
            password="13771377",
            host="0.0.0.0")
        cur = conn.cursor()

        cur.execute(f"UPDATE books SET state={update_state_request_body.new_state} WHERE volume_id='{update_state_request_body.volume_id}'")
        conn.commit()
        cur.close()
        conn.close()

        return 


if __name__ == "__main__":

    uvicorn.run(app, host="0.0.0.0", port=8000)