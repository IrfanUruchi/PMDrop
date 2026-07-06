from fastapi import APIRouter
from pydantic import BaseModel
import time

from app.database import SessionLocal
from app.models import Device

router = APIRouter()


class DeviceRegistration(BaseModel):
    name: str
    ip: str


@router.get("/devices")
async def devices():
    db = SessionLocal()

    devices = db.query(Device).all()

    result = []

    for d in devices:
        result.append({
            "name": d.name,
            "ip": d.ip,
            "status": "online",
            "last_seen": d.last_seen
        })

    db.close()

    return {
        "devices": result
    }


@router.post("/devices/register")
async def register_device(device: DeviceRegistration):
    db = SessionLocal()

    existing = db.query(Device).filter(Device.ip == device.ip).first()

    if existing:
        existing.name = device.name
        existing.last_seen = int(time.time())
    else:
        new_device = Device(
            name=device.name,
            ip=device.ip,
            last_seen=int(time.time())
        )
        db.add(new_device)

    db.commit()
    db.close()

    return {
        "message": "Device registered"
    }
