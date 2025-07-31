from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from db.main import init_db
from routes.register import registerR
from routes.login import loginR
from routes.listing import listingR
from routes.auction import auctionR
import uvicorn



@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    print("DB initialized")
    yield
    print("closing server")

app = FastAPI(lifespan=lifespan)
app.include_router(registerR)
app.include_router(loginR)
app.include_router(listingR)
app.include_router(auctionR)

app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_methods=("GET", "POST", "PUT", "DELETE"))

@app.get('/')
def home():
    return {"message":"hey"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=9000)