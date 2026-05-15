"""
chat.py — Lógica principal del chatbot

Este archivo orquesta todo: recibe el mensaje, consulta la memoria,
construye el prompt, llama al LLM y guarda la respuesta.

"""

from database import SessionLocal, User, Message
from datetime import datetime, timezone


async def process_message(session_id: str, message: str, user_name: str | None = None) -> dict:
    """
    Procesa un mensaje del usuario y devuelve la respuesta del chatbot.

    Args:
        session_id: ID único de la sesión del usuario
        message:    Texto del mensaje
        user_name:  Nombre del usuario (si se conoce)

    Returns:
        dict con 'response', 'session_id' y 'message_count'
    """
    db = SessionLocal()
    try:
        # 1. Buscar o crear usuario
        user = db.query(User).filter(User.session_id == session_id).first()

        if not user:
            user = User(
                session_id=session_id,
                name=user_name,
                message_count=0
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        # Actualizar nombre si se proporciona ahora
        if user_name and not user.name:
            user.name = user_name

        # 2. Guardar mensaje del usuario
        user_msg = Message(
            session_id=session_id,
            role="user",
            content=message
        )
        db.add(user_msg)

        # 3. Incrementar contador
        user.message_count += 1
        user.last_seen = datetime.now(timezone.utc)

        # 4. Generar respuesta
        bot_response = (
            f"[Fase 1 - placeholder] Recibido: '{message}'. "
            f"En la Fase 2 responderé con IA real. "
            f"Mensajes en esta sesión: {user.message_count}"
        )

        # 5. Guardar respuesta del bot
        bot_msg = Message(
            session_id=session_id,
            role="assistant",
            content=bot_response
        )
        db.add(bot_msg)

        db.commit()

        return {
            "response": bot_response,
            "session_id": session_id,
            "message_count": user.message_count
        }

    finally:
        db.close()