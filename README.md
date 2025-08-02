# ThriftAddis API

ThriftAddis is a FastAPI-powered backend for an e-commerce marketplace, designed for seamless integration with a Next.js frontend. It provides secure user authentication, auction and listing management, and robust database operations using async SQLModel and PostgreSQL.

---

## 🚀 Features

- User registration and login with hashed passwords
- JWT-based authentication (ready for extension)
- CRUD operations for item listings and auctions
- Asynchronous database access (SQLModel, SQLAlchemy, asyncpg)
- Modular architecture: routes, services, utils, tasks
- Auction status auto-updates via background tasks
- CORS support for frontend integration

---

## 🗂️ Project Structure

```
.
├── main.py                # FastAPI app entrypoint & lifespan events
├── config.py              # Pydantic settings loader (.env)
├── requirements.txt       # Python dependencies
├── db/
│   ├── main.py            # DB session, engine, and init
│   └── models.py          # SQLModel/Pydantic models
├── routes/
│   ├── auction.py         # Auction endpoints
│   ├── listing.py         # Listing endpoints
│   ├── login.py           # Login endpoints
│   └── register.py        # Registration endpoints
├── services/
│   ├── auctionService.py  # Auction business logic
│   ├── authService.py     # Auth/JWT logic
│   ├── hashPwd.py         # Password hashing/checking
│   ├── listingService.py  # Listing business logic
│   ├── loginServices.py   # Login logic
│   ├── registerServices.py# Registration logic
│   └── userService.py     # User queries
├── tasks/
│   └── auction_status.py  # Background auction status updater
├── utils/
│   └── auctionUtil.py     # Auction utilities
├── index.html             # Placeholder HTML
├── .env                   # Environment variables (DB URL)
└── README.md              # Project documentation
```

---

## ⚙️ Setup & Installation

1. **Clone the repository**
   ```sh
   git clone https://github.com/molcagg88/thriftaddis.git
   cd thriftaddis
   ```
2. **Create and activate a Python virtual environment**
   ```sh
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```
3. **Install dependencies**
   ```sh
   pip install -r requirements.txt
   ```
4. **Configure environment variables**
   - Copy `.env.example` to `.env` and set your `DATABASE_URL` (PostgreSQL connection string).
5. **Run the server**
   ```sh
   uvicorn main:app --host 0.0.0.0 --port 9000
   ```

---

## 🛠️ Usage

Once running, the API is available at `http://localhost:9000`. You can interact with the OpenAPI docs at `http://localhost:9000/docs`.

---

## 📚 API Endpoints (Summary)

### Authentication & Users

- `POST /register/` — Register a new user
- `POST /login/` — Login and receive JWT token

### Listings

- `GET /listing/` — Get listings for the authenticated user
- `POST /listing/` — Create a new listing
- `PUT /listing/` — Update a listing
- `DELETE /listing/` — Delete a listing

### Auctions

- `GET /auction/` — Get auction details
- `POST /auction/` — Create a new auction
- `PUT /auction/` — Update auction info
- `DELETE /auction/` — Delete an auction

---

## 🧰 Tech Stack

- Python 3.9+
- FastAPI
- SQLModel & SQLAlchemy
- asyncpg
- bcrypt
- PyJWT
- Pydantic
- Uvicorn

---

## 📝 Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

---

## 📄 License

This project is licensed under the MIT License.
