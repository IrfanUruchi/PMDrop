from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, Dict, Any
import time

router = APIRouter()

signals = []


class SignalMessage(BaseModel):
    sender: str
    target: str
    type: str
    payload: Dict[str, Any]


@router.post("/signal")
async def send_signal(message: SignalMessage):
    signals.append({
        "sender": message.sender,
        "target": message.target,
        "type": message.type,
        "payload": message.payload,
        "created_at": int(time.time())
    })

    return {"success": True}


@router.get("/signal/{device_name}")
async def get_signals(device_name: str):
    inbox = [s for s in signals if s["target"] == device_name]

    signals[:] = [s for s in signals if s["target"] != device_name]

    return {"signals": inbox}
