"""
chat.py — Lógica principal del chatbot

Este archivo orquesta todo: recibe el mensaje, consulta la memoria,
construye el prompt, llama al LLM y guarda la respuesta.

"""

from groq import Groq
from database import SessionLocal, User, Message
from datetime import datetime, timezone
import os
from dotenv import load_dotenv

load_dotenv()

# Cliente de Groq
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
CHATBOT_NAME = os.getenv("CHATBOT_NAME", "Aria")


def get_conversation_history(db, session_id: str, limit: int = 10) -> list:
    """
    Recupera los últimos mensajes de la conversación.
    Esto es la memoria a corto plazo del chatbot.
    limit=10 significa que recuerda los últimos 10 mensajes.
    """
    messages = (
        db.query(Message)
        .filter(Message.session_id == session_id)
        .order_by(Message.created_at.desc())
        .limit(limit)
        .all()
    )
    # Los devolvemos en orden cronológico (del más antiguo al más nuevo)
    return [{"role": m.role, "content": m.content} for m in reversed(messages)]


def build_system_prompt(user: User) -> str:
    """
    Construye el system prompt del chatbot.
    El system prompt es el mensaje inicial que define
    cómo se comporta el chatbot en toda la conversación.
    """
    name = user.name if user.name else "usuario"

    return f"""Eres {CHATBOT_NAME}, un asistente inteligente y amigable con personalidad propia.

Tu personalidad:
- Eres curioso, empático y algo humor
- Te adaptas al tono del usuario (si es formal, tú también; si es informal, tú también)
- Recuerdas lo que el usuario te ha contado durante la conversación
- Haces preguntas cuando quieres saber más sobre el usuario

Información sobre este usuario:
- Nombre: {name}
- Mensajes enviados: {user.message_count}

Instrucciones:
- Responde siempre en el idioma que use el usuario
- Sé conciso pero completo
- Si el usuario te dice su nombre, úsalo de vez en cuando
- Nunca digas que eres una IA de Groq o Meta, simplemente eres {CHATBOT_NAME}
"""


async def process_message(session_id: str, message: str, user_name: str | None = None) -> dict:
    """
    Procesa un mensaje del usuario y devuelve la respuesta del chatbot.
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

        if user_name and not user.name:
            user.name = user_name

        # 2. Recuperar historial (memoria a corto plazo)
        history = get_conversation_history(db, session_id)

        # 3. Guardar mensaje del usuario
        user_msg = Message(
            session_id=session_id,
            role="user",
            content=message
        )
        db.add(user_msg)
        user.message_count += 1
        user.last_seen = datetime.now(timezone.utc)
        db.commit()

        # 4. Construir los mensajes para Groq
        # Groq recibe: system prompt + historial + mensaje actual
        groq_messages = history + [{"role": "user", "content": message}]

        # 5. Llamar a Groq
        completion = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": build_system_prompt(user)},
                *groq_messages
            ],
            max_tokens=1000,
            temperature=0.7  # 0=muy predecible, 1=muy creativo
        )

        bot_response = completion.choices[0].message.content
        tokens_used = completion.usage.total_tokens

        # 6. Guardar respuesta del bot
        bot_msg = Message(
            session_id=session_id,
            role="assistant",
            content=bot_response,
            tokens_used=tokens_used
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