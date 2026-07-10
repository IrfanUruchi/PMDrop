from __future__ import annotations

import asyncio
import time
import uuid
from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter()

SIGNAL_TTL_SECONDS = 60

signals: list[dict[str, Any]] = []
signals_lock = asyncio.Lock()


class SignalMessage(BaseModel):
    sender: str = Field(min_length=1, max_length=64)
    target: str = Field(min_length=1, max_length=64)
    type: str = Field(min_length=1, max_length=32)
    payload: dict[str, Any] = Field(default_factory=dict)


def remove_expired_signals(now: float) -> None:
    signals[:] = [
        signal
        for signal in signals
        if now - signal["created_at"] <= SIGNAL_TTL_SECONDS
    ]


@router.post("/signal")
async def send_signal(message: SignalMessage):
    now = time.time()

    signal = {
        "id": str(uuid.uuid4()),
        "sender": message.sender,
        "target": message.target,
        "type": message.type,
        "payload": message.payload,
        "created_at": now,
    }

    async with signals_lock:
        remove_expired_signals(now)
        signals.append(signal)

    print(
        f"[SIGNAL SEND] "
        f"{message.sender} -> {message.target} "
        f"type={message.type}"
    )

    return {
        "success": True,
        "signal_id": signal["id"],
    }


@router.get("/signal/{device_name}")
async def get_signals(device_name: str):
    now = time.time()

    async with signals_lock:
        remove_expired_signals(now)

        inbox = [
            signal
            for signal in signals
            if signal["target"] == device_name
        ]

        delivered_ids = {signal["id"] for signal in inbox}

        signals[:] = [
            signal
            for signal in signals
            if signal["id"] not in delivered_ids
        ]

    if inbox:
        signal_types = ", ".join(signal["type"] for signal in inbox)

        print(
            f"[SIGNAL RECEIVE] "
            f"target={device_name} "
            f"count={len(inbox)} "
            f"types={signal_types}"
        )

    return {
        "signals": inbox,
        "count": len(inbox),
    }


@router.get("/signal-debug")
async def signal_debug():
    now = time.time()

    async with signals_lock:
        remove_expired_signals(now)

        queued = [
            {
                "id": signal["id"],
                "sender": signal["sender"],
                "target": signal["target"],
                "type": signal["type"],
                "age_seconds": round(now - signal["created_at"], 2),
            }
            for signal in signals
        ]

    return {
        "queued_count": len(queued),
        "signals": queued,
    }
