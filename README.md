# Thrift API

A FastAPI-based backend for a marketplace application, supporting user registration, login, and item listings. Uses PostgreSQL (async) for storage.

## Features

- User registration and login with hashed passwords
- JWT-ready structure (authentication logic can be extended)
- CRUD operations for item listings
- Asynchronous SQLModel/SQLAlchemy integration
- Modular service and route structure

## Project Structure

```
.
├── main.py                # FastAPI app entrypoint
├── config.py              # Pydantic settings (loads .env)
├── .env                   # Environment variables (DB URL)
├── db/
│   ├── main.py            # DB session and initialization
│   └── models.py          # SQLModel and Pydantic models
├── routes/
│   ├── register.py        # Registration endpoints
│   ├── login.py           # Login endpoints
│   └── listing.py         # Item listing endpoints
├── services/
│   ├── hashPwd.py         # Password hashing/checking
│   ├── registerServices.py# Registration logic
│   ├── loginServices.py   # Login logic
│   └── listingService.py  # Listing CRUD logic
└── index.html             # Placeholder HTML
```

## Setup

1. **Clone the repo**
2. **Install dependencies**
    ```sh
    pip install -r requirements.txt
    ```
    *(You may need to create this file with FastAPI, SQLModel, asyncpg, bcrypt, etc.)*

3. **Configure environment**
    - Edit `.env` with your PostgreSQL connection string.

4. **Run the server**
    ```sh
    uvicorn main:app --host 0.0.0.0 --port 9000
    ```

## API Endpoints

- `POST /register/` — Register a new user
- `POST /login/` — Login with username and password
- `GET /listing/?user_id=...` — Get listings for a user
- `POST /listing/` — Create a new listing
- `PUT /listing/` — Update a listing
- `DELETE /listing/` — Delete a listing

## Notes

- Passwords are hashed using bcrypt ([`services/hashPwd.py`](services/hashPwd.py)).
- Database models are in [`db/models.py`](db/models.py).
- The project uses async SQLModel and FastAPI for high performance.

## License

MIT 
