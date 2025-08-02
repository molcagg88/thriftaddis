# Thrift API Backend

Thrift API is a FastAPI-based backend for an e-commerce marketplace, designed to be integrated with a Next.js frontend. It provides user authentication, registration, and CRUD operations for item listings, using PostgreSQL for persistent storage.

---

## 🚀 Features

- User registration and login with hashed passwords
- JWT authentication for secure endpoints
- CRUD operations for item listings
- Asynchronous database access with SQLModel & SQLAlchemy
- Modular architecture (routes, services, models)
- CORS enabled for frontend integration

---

## 🛠️ Tech Stack

- **Python 3.9+**
- **FastAPI**
- **SQLModel** & **SQLAlchemy** (async)
- **PostgreSQL** (asyncpg driver)
- **bcrypt** (password hashing)
- **PyJWT** (token authentication)
- **Pydantic & pydantic-settings** (config & validation)

---

## 📁 Project Structure

```
public_html/
├── main.py                # FastAPI app entrypoint
├── config.py              # Pydantic settings loader
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (DB URL)
├── db/
│   ├── main.py            # DB session, engine, and init
│   └── models.py          # SQLModel & Pydantic models
├── routes/
│   ├── register.py        # Registration endpoints
│   ├── login.py           # Login endpoints
│   └── listing.py         # Listing endpoints
├── services/
│   ├── authService.py     # JWT & auth logic
│   ├── hashPwd.py         # Password hashing/checking
│   ├── registerServices.py# Registration logic
│   ├── loginServices.py   # Login logic
│   ├── listingService.py  # Listing CRUD logic
│   └── userService.py     # User lookup logic
└── index.html             # Placeholder HTML
```

---

## ⚡ Setup & Usage

1. **Clone the repository**

   ```sh
   git clone https://github.com/molcagg88/thriftaddis.git
   cd thriftaddis/public_html
   ```

2. **Install dependencies**

   ```sh
   pip install -r requirements.txt
   ```

3. **Configure environment**

   - Create a `.env` file in `public_html/` with:
     ```env
     DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/thriftdb
     ```

4. **Run the server**
   ```sh
   uvicorn main:app --host 0.0.0.0 --port 9000
   ```

---

## 🔗 API Endpoints

### Authentication & Users

- `POST /register/` — Register a new user
- `POST /login/` — Login and receive JWT token

### Listings

- `GET /listing/` — Get listings for the authenticated user
- `POST /listing/` — Create a new listing
- `PUT /listing/` — Update a listing
- `DELETE /listing/` — Delete a listing

---

## 📝 Environment & Configuration

- All configuration is managed via `.env` and `config.py` using `pydantic-settings`.
- The database URL must be set in `.env`.

---

## 🧩 Integration

- Designed for seamless integration with a Next.js frontend (CORS enabled).
- All endpoints return JSON responses suitable for frontend consumption.

---

## 🛡️ Security

- Passwords are hashed with bcrypt.
- JWT tokens are used for authentication and protected routes.

---

## 🧪 Testing & Development

- You can use [httpie](https://httpie.io/) or [curl](https://curl.se/) to test endpoints.
- Example registration:
  ```sh
  http POST http://localhost:9000/register/ username="user1" password="pass123" email="user1@example.com"
  ```

---

## 🤝 Contributing

Pull requests and issues are welcome! Please open an issue for bugs or feature requests.

---

## 📄 License

MIT
