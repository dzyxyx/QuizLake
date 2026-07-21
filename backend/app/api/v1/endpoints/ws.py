from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.websockets.manager import manager


router = APIRouter()


@router.websocket("/{session_id}")
async def websocket_endpoint(session_id: int, websocket: WebSocket):
    await manager.connect(session_id, websocket)
    try:
        while True:
            await websocket.receive_json()
    except WebSocketDisconnect:
        manager.disconnect(session_id, websocket)