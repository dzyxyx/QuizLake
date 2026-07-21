from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[int, list[WebSocket]] = {}

    async def connect(self, session_id: int, websocket: WebSocket):
        await websocket.accept()
        if session_id not in self.active_connections:
            self.active_connections[session_id] = []
        self.active_connections[session_id].append(websocket)

    def disconnect(self, session_id: int, websocket: WebSocket):
        if session_id in self.active_connections:
            self.active_connections[session_id].remove(websocket)

    async def broadcast(self, session_id: int, message: dict):
        dead_connections = []

        for websocket in self.active_connections.get(session_id, []):
            try:
                await websocket.send_json(message)
            except Exception:
                dead_connections.append(websocket)
        
        for websocket in dead_connections:
            self.disconnect(session_id, websocket)
            

manager = ConnectionManager()