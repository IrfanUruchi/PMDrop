from fastapi import APIRouter, Request
from pydantic import BaseModel
import time

from app.database import SessionLocal
from app.models import Device

router = APIRouter()


class DeviceRegistration(BaseModel):
    name: str


class DeviceHeartbeat(BaseModel):
    name: str


@router.get("/devices")
async def devices():
    db = SessionLocal()
    devices = db.query(Device).all()

    now = int(time.time())
    result = []

    for d in devices:
        last_seen = d.last_seen or 0
        is_online = (now - last_seen) <= 30

        result.append({
            "name": d.name,
            "ip": d.ip,
            "status": "online" if is_online else "offline",
            "last_seen": last_seen,
            "seconds_ago": now - last_seen
        })

    db.close()
    return {"devices": result}


@router.post("/devices/register")
async def register_device(device: DeviceRegistration, request: Request):
    db = SessionLocal()

    ip = request.client.host
    now = int(time.time())

    existing = db.query(Device).filter(Device.name == device.name).first()

    if existing:
        existing.ip = ip
        existing.last_seen = now
    else:
        new_device = Device(
            name=device.name,
            ip=ip,
            last_seen=now
        )
        db.add(new_device)

    db.commit()
    db.close()

    return {"message": "Device registered"}


@router.post("/devices/heartbeat")
async def heartbeat(device: DeviceHeartbeat):
    db = SessionLocal()

    existing = db.query(Device).filter(Device.name == device.name).first()

    if not existing:
        db.close()
        return {"success": False, "message": "Device not found"}

    existing.last_seen = int(time.time())

    db.commit()
    db.close()

    return {"success": True, "message": "Heartbeat received"}
