import requests
import psycopg2
import psycopg2.extras
from psycopg2 import sql

API_KEY = "AIzaSyBVzyNN5zRjluikDh1EfaN5XRT7c0oCz4g"
books_dict = {"Atomic habits": 1473537800,
         "Rich Dad Poor Dad":9780759521438,
         "Rich Dad's Guide to Investing": 9780446677462,
         "Fundamentals of Data Engineering": 9781098108274,
         "Zero to One": 9780804139298,
         "Microservices: Up and Running": 9781492075400
        }



def get_existing_tables():
    # getting all existing tables in DB
    conn = psycopg2.connect(
        database="digital_lib_db",
        user="postgres",
        password="13771377",
        host="0.0.0.0")
    
    cur = conn.cursor()
    cur.execute("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                """)
    
    existing_tables = [table[0] for table in cur.fetchall()]

    cur.close()
    conn.close()

    return existing_tables

def create_table(existing_tables):
    if "books" not in existing_tables:
        print("'books' table not found ..., creating a new one!")

        conn = psycopg2.connect(
            database="digital_lib_db",
            user="postgres",
            password="13771377",
            host="0.0.0.0")
        
        cur = conn.cursor()

        cur.execute("""
                    CREATE TABLE books (
                    ID SERIAL not null,
                    volume_ID varchar(255) not null UNIQUE,
                    title varchar(255) not null,
                    authors varchar(255),
                    thumbnail varchar(255),
                    state int DEFAULT 0,
                    rating int DEFAULT 0);
                    """)
        
        conn.commit()
        
        cur.close()
        conn.close()

    else:
        print("'books' table already exists in the database")

def extract_book_data_from_URL(url):
    response = requests.get(url)
    data = response.json()
    book_info = data['items'][0]["volumeInfo"]
    volume_id = data["items"][0]["id"]
    title = book_info["title"]
    authors = ', '.join(book_info["authors"])
    thumbnail = book_info.get("imageLinks", None).get("thumbnail", None)
    rating = book_info.get("averageRating", 0)

    dict_data = {"volume_id": volume_id,
                 "title": title,
                 "authors": authors,
                 "thumbnail": thumbnail,
                 "rating": rating}
    
    return dict_data

def collect_book_data(books_dict):
    """
    collecting data of books in books_dict from google book API
    """
    book_data_list = []
    for book in books_dict.keys():
        isbn = books_dict[book]
        url = f'https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}&key={API_KEY}'
        book_data = extract_book_data_from_URL(url)
        book_data_list.append(tuple(data for data in book_data.values()))

    return book_data_list


def write_to_database(books_data_list):
    conn = psycopg2.connect(
        database="digital_lib_db",
        user="postgres",
        password="13771377",
        host="0.0.0.0")
    
    cur = conn.cursor()
    query = """INSERT INTO books (volume_id, title, authors, thumbnail, rating)
            VALUES %s
            ON CONFLICT (volume_id) DO NOTHING
            """
    psycopg2.extras.execute_values(cur, query, books_data_list)

    conn.commit()
    
    cur.close()
    conn.close()

def read_books_from_DB():
    conn = psycopg2.connect(
        database="digital_lib_db",
        user="postgres",
        password="13771377",
        host="0.0.0.0")
    
    cur = conn.cursor()
    cur.execute("SELECT * FROM books ORDER BY id DESC")
    rows = cur.fetchall()

    for row in rows:
        print((row))



if __name__ == "__main__":
    tables = get_existing_tables()
    create_table(tables)

    book_list = collect_book_data(books_dict)
    # write_to_database(book_list)
    read_books_from_DB()




