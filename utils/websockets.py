from fastapi import WebSocket, APIRouter, HTTPException
from typing import List
from db.models import UserPydantic
from services.authService import get_current_user
router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.userData: UserPydantic
    async def connect(self, websocket: WebSocket):
        self.active_connections.append(websocket)
        
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)

manager = ConnectionManager()