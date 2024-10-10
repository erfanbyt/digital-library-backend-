# Digital Library App

This repo includes the code for creating the backend of a digital library. It has functionalities needed by the backend of a digital library app, like getting the book data from "google book API", adding new books to database, changing the status of the book, and rating it. 

Note: the API key is removed from `server.py` and `create_book_table.py`.

### used services
The backend service uses postgres DB for storing the book data. There is no need to install postgres locally on your machine. The docker-compose file in the repo will create postgres container and will use named volumes to store data in your system. 

## installation 

### step 1:
make sure Docker is installed on your system 

### step 2:
run the following command to create postgres and adminer container. Adminer container provides UI for interacting with the DB. 

```bash 
docker compose up -d
```

Adminer is accessible at `(http://localhost:8080/)`. 

### step 3:
install the requirements for the python env.

```bash 
pip install -r requirements.txt
```

