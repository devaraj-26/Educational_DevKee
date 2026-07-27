from fastapi import FastAPI, Form, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
from app.models import Message
from sqlalchemy.orm import Session

from app.database import engine, Base, get_db
from app.models import User
from app.auth import hash_password, verify_password
from app.websocket import router as websocket_router

# ----------------------
# FastAPI
# ----------------------

app = FastAPI(title="Private Chat")

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

# Create Database Tables
Base.metadata.create_all(bind=engine)

# Include WebSocket Routes
app.include_router(websocket_router)

# ----------------------
# Routes
# ----------------------

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="login.html"
    )


@app.post("/register")
async def register(
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):

    existing = db.query(User).filter(
        User.username == username
    ).first()

    if existing:
        return {
            "message": "Username already exists"
        }

    user = User(
        username=username,
        password=hash_password(password)
    )

    db.add(user)
    db.commit()

    return {
        "message": "User Registered Successfully"
    }


@app.post("/login")
async def login(
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):

    user = db.query(User).filter(
        User.username == username
    ).first()

    if user is None:
        return {
            "message": "User not found"
        }

    if not verify_password(password, user.password):
        return {
            "message": "Incorrect password"
        }

    response = RedirectResponse(
        url="/chat",
        status_code=303
    )

    response.set_cookie(
        key="username",
        value=username
    )

    return response

@app.get("/chat", response_class=HTMLResponse)
async def chat(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="chat.html"
    )
    
@app.get("/history/{user1}/{user2}")
async def history(user1: str, user2: str, db: Session = Depends(get_db)):

    chats = db.query(Message).filter(
        ((Message.sender == user1) & (Message.receiver == user2)) |
        ((Message.sender == user2) & (Message.receiver == user1))
    ).order_by(Message.id).all()

    return JSONResponse([
        {
            "sender": c.sender,
            "receiver": c.receiver,
            "message": c.message,
            "status": c.status,
            "time": str(c.created_at)
        }
        for c in chats
    ])