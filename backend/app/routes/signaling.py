from __future__ import annotations

import asyncio
import time
import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter()

SIGNAL_TTL_SECONDS = 300

signals: list[dict[str, Any]] = []
signals_lock = asyncio.Lock()


class SignalMessage(BaseModel):
    sender: str = Field(min_length=1, max_length=64)
    target: str = Field(min_length=1, max_length=64)
    type: str = Field(min_length=1, max_length=32)
    payload: dict[str, Any] = Field(default_factory=dict)


class SignalAck(BaseModel):
    signal_id: str = Field(min_length=1)
    device_name: str = Field(min_length=1, max_length=64)


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
        "delivered": False,
    }

    async with signals_lock:
        remove_expired_signals(now)
        signals.append(signal)

    print(
        f"[SIGNAL SEND] {message.sender} -> {message.target} "
        f"type={message.type} id={signal['id']}"
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

        inbox: list[dict[str, Any]] = []
        removable_ids: set[str] = set()

        for signal in signals:
            if signal["target"] != device_name:
                continue

            inbox.append(signal.copy())

            # Transfer requests remain queued until explicit ACK.
            if signal["type"] == "transfer_request":
                signal["delivered"] = True
            else:
                removable_ids.add(signal["id"])

        if removable_ids:
            signals[:] = [
                signal
                for signal in signals
                if signal["id"] not in removable_ids
            ]

    if inbox:
        print(
            f"[SIGNAL RECEIVE] target={device_name} "
            f"count={len(inbox)} "
            f"types={','.join(item['type'] for item in inbox)}"
        )

    return {
        "signals": inbox,
        "count": len(inbox),
    }


@router.post("/signal/ack")
async def acknowledge_signal(ack: SignalAck):
    async with signals_lock:
        matching = next(
            (
                signal
                for signal in signals
                if signal["id"] == ack.signal_id
                and signal["target"] == ack.device_name
            ),
            None,
        )

        if matching is None:
            raise HTTPException(status_code=404, detail="Signal not found")

        signals.remove(matching)

    print(
        f"[SIGNAL ACK] target={ack.device_name} "
        f"type={matching['type']} id={ack.signal_id}"
    )

    return {"success": True}


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
                "delivered": signal["delivered"],
                "age_seconds": round(now - signal["created_at"], 2),
            }
            for signal in signals
        ]

    return {
        "queued_count": len(queued),
        "signals": queued,
    }
