"""
main.py — Punto de entrada de la aplicación FastAPI

Este archivo arranca el servidor web y define las rutas (endpoints) de la API.
FastAPI genera automáticamente documentación interactiva en /docs
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

from database import create_tables

load_dotenv()


# CICLO DE VIDA DE LA APP
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Se ejecuta al arrancar y al apagar el servidor.
    Aquí inicializamos la base de datos.
    """
    print("Iniciando chatbot...")
    create_tables()
    print("Base de datos lista")
    yield
    print("Apagando servidor...")


# CREAR LA APP
app = FastAPI(
    title="Chatbot IA con Memoria",
    description="Chatbot inteligente que aprende y se adapta a cada usuario",
    version="1.0.0",
    lifespan=lifespan
)

# CORS: permite que el frontend (HTML/JS) llame a la API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# MODELOS DE PETICIÓN / RESPUESTA
class ChatRequest(BaseModel):
    """Estructura del JSON que recibe el endpoint /chat"""
    session_id: str
    message: str
    user_name: str | None = None


class ChatResponse(BaseModel):
    """Estructura del JSON que devuelve el endpoint /chat"""
    response: str
    session_id: str
    message_count: int


class HealthResponse(BaseModel):
    status: str
    chatbot_name: str
    model: str


# ENDPOINTS
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    GET /health — Comprueba que el servidor está funcionando.
    """
    return {
        "status": "ok",
        "chatbot_name": os.getenv("CHATBOT_NAME", "Aria"),
        "model": os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    POST /chat — Endpoint principal del chatbot.
    """
    from chat import process_message

    if not request.message.strip():
        raise HTTPException(status_code=400, detail="El mensaje no puede estar vacío")

    try:
        result = await process_message(
            session_id=request.session_id,
            message=request.message,
            user_name=request.user_name
        )
        return ChatResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/history/{session_id}")
async def get_history(session_id: str, limit: int = 20):
    """
    GET /history/{session_id} — Devuelve el historial de mensajes.
    """
    from database import SessionLocal, Message

    db = SessionLocal()
    try:
        messages = (
            db.query(Message)
            .filter(Message.session_id == session_id)
            .order_by(Message.created_at.desc())
            .limit(limit)
            .all()
        )
        return {
            "session_id": session_id,
            "messages": [
                {
                    "role": m.role,
                    "content": m.content,
                    "created_at": m.created_at.isoformat()
                }
                for m in reversed(messages)
            ]
        }
    finally:
        db.close()


@app.delete("/history/{session_id}")
async def clear_history(session_id: str):
    """
    DELETE /history/{session_id} — Borra el historial de mensajes
    pero MANTIENE el perfil aprendido del usuario.
    """
    from database import SessionLocal, Message, User
    from embeddings import delete_user_collection

    db = SessionLocal()
    try:
        # Borrar solo los mensajes, NO el usuario ni su perfil
        db.query(Message).filter(Message.session_id == session_id).delete()
        db.commit()

        # Borrar embeddings
        delete_user_collection(session_id)

        return {"status": "ok", "message": "Historial borrado correctamente"}
    finally:
        db.close()


# SERVIR EL FRONTEND
frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")

if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")

    @app.get("/")
    async def serve_frontend():
        return FileResponse(os.path.join(frontend_path, "index.html"))


# ARRANCAR EL SERVIDOR
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 8000)),
        reload=True
    )