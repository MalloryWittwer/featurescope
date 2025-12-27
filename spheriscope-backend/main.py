from typing import List
from pydantic import BaseModel
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, Form
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import Column, Integer, LargeBinary, Float, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker
from PIL import Image
import io
from fastapi.responses import JSONResponse
import base64
import os

THUMBNAIL_SIZE = int(os.getenv("THUMBNAIL_SIZE", 64))

DATABASE_URL = "sqlite:///./images.db"
FRONTEND_URL = "http://localhost:3000"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class EmbeddedImageData(Base):
    __tablename__ = "images"
    id = Column(Integer, primary_key=True, index=True)
    image_data = Column(LargeBinary)
    thumbnail_data = Column(LargeBinary)
    x_pos = Column(Float)
    y_pos = Column(Float)


class ThumbnailResponse(BaseModel):
    id: int
    x_pos: float
    y_pos: float
    thumbnail: str


class ImageResponse(BaseModel):
    id: int
    x_pos: float
    y_pos: float
    image: str


Base.metadata.create_all(bind=engine)

app = FastAPI()

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def home():
    return {"status": "running"}


@app.post("/images/")
async def upload_image(
    file: UploadFile = File(...),
    x_pos: float = Form(...),
    y_pos: float = Form(...),
    db: Session = Depends(get_db),
):
    image_data = await file.read()
    
    image = Image.open(io.BytesIO(image_data))

    thumbnail = image.resize((THUMBNAIL_SIZE, THUMBNAIL_SIZE))

    output = io.BytesIO()
    thumbnail.save(output, format=image.format)
    thumbnail_data = output.getvalue()

    entry = EmbeddedImageData(
        image_data=image_data,
        thumbnail_data=thumbnail_data,
        x_pos=x_pos,
        y_pos=y_pos,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)

    return {"id": entry.id}


@app.get("/thumbnails/", response_model=List[ThumbnailResponse])
async def get_thumbnails(db: Session = Depends(get_db)):
    db_entries = db.query(EmbeddedImageData).all()
    content = [
        {
            "id": db_entry.id,
            "x_pos": db_entry.x_pos,
            "y_pos": db_entry.y_pos,
            "thumbnail": base64.b64encode(db_entry.thumbnail_data).decode('utf-8'),
        }
        for db_entry in db_entries
    ]
    return JSONResponse(content=content)


@app.get("/images/{image_id}", response_model=ImageResponse)
async def get_image(image_id: int, db: Session = Depends(get_db)):
    db_entry = db.query(EmbeddedImageData).filter(EmbeddedImageData.id == image_id).first()
    if db_entry is None:
        raise HTTPException(status_code=404, detail="Image not found")
    
    content = {
        "id": db_entry.id,
        "x_pos": db_entry.x_pos,
        "y_pos": db_entry.y_pos,
        "image": base64.b64encode(db_entry.image_data).decode('utf-8'),
    }

    return JSONResponse(content=content)