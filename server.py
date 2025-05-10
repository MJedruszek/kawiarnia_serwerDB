from fastapi import FastAPI
from fastapi.websockets import WebSocket, WebSocketDisconnect
import asyncio
import json
from cafe_db_setup import get_db, init_db
from contextlib import asynccontextmanager

#poniższy kod stworzy serwer za pomocą websockets i umożliwi połączenie z nim, a także podstawowe interakcje

