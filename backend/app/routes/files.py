from fastapi import APIRouter, UploadFile, File
from fastapi.responses import FileResponse
import os
import time

from app.database import SessionLocal
from app.models import File as FileModel

router = APIRouter()

UPLOAD_DIR = "storage"
os.makedirs(UPLOAD_DIR, exist_ok=True)


def format_size(size):
    if size < 1024:
        return f"{size} B"
    if size < 1024 * 1024:
        return f"{size / 1024:.1f} KB"
    if size < 1024 * 1024 * 1024:
        return f"{size / (1024 * 1024):.1f} MB"
    return f"{size / (1024 * 1024 * 1024):.1f} GB"


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    path = os.path.join(UPLOAD_DIR, file.filename)

    content = await file.read()

    with open(path, "wb") as f:
        f.write(content)

    now = int(time.time())
    size = len(content)

    db = SessionLocal()

    existing = db.query(FileModel).filter(FileModel.filename == file.filename).first()

    if existing:
        existing.size = size
        existing.path = path
        existing.uploaded_at = now
    else:
        db.add(FileModel(
            filename=file.filename,
            size=size,
            path=path,
            uploaded_at=now
        ))

    db.commit()
    db.close()

    return {
        "filename": file.filename,
        "status": "uploaded"
    }


@router.get("/files")
async def list_files():
    db = SessionLocal()
    db_files = db.query(FileModel).all()

    files = []

    for f in db_files:
        if os.path.exists(f.path):
            files.append({
                "name": f.filename,
                "size": f.size,
                "size_human": format_size(f.size),
                "uploaded_at": f.uploaded_at,
                "uploaded_at_human": time.strftime(
                    "%Y-%m-%d %H:%M",
                    time.localtime(f.uploaded_at)
                )
            })

    db.close()

    files.sort(key=lambda x: x["uploaded_at"], reverse=True)

    return {"files": files}


@router.get("/download/{filename}")
async def download_file(filename: str):
    db = SessionLocal()
    db_file = db.query(FileModel).filter(FileModel.filename == filename).first()
    db.close()

    if not db_file or not os.path.exists(db_file.path):
        return {"error": "File not found"}

    return FileResponse(db_file.path, filename=filename)


@router.delete("/delete/{filename}")
async def delete_file(filename: str):
    db = SessionLocal()
    db_file = db.query(FileModel).filter(FileModel.filename == filename).first()

    if not db_file:
        db.close()
        return {"error": "File not found"}

    if os.path.exists(db_file.path):
        os.remove(db_file.path)

    db.delete(db_file)
    db.commit()
    db.close()

    return {
        "filename": filename,
        "status": "deleted"
    }
