from fastapi import APIRouter
from app.database import SessionLocal
from app.models import File, Device

router = APIRouter()


def human_size(size):
    if size < 1024:
        return f"{size} B"
    if size < 1024 * 1024:
        return f"{size / 1024:.1f} KB"
    if size < 1024 * 1024 * 1024:
        return f"{size / (1024 * 1024):.1f} MB"

    return f"{size / (1024 * 1024 * 1024):.1f} GB"


@router.get("/stats")
async def stats():
    db = SessionLocal()

    files = db.query(File).all()
    devices = db.query(Device).all()

    total_size = sum(f.size for f in files)

    db.close()

    return {
        "files": len(files),
        "devices": len(devices),
        "storage_bytes": total_size,
        "storage_human": human_size(total_size)
    }
