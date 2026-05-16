"""
chat.py — Lógica principal del chatbot

Ahora el chatbot puede recordar mensajes relevantes de toda la historia,
no solo los últimos 10.
"""

from groq import Groq
from database import SessionLocal, User, Message
from personality import analyze_conversation, get_user_profile
from embeddings import store_message, search_relevant_messages
from datetime import datetime, timezone
import os
import json
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
CHATBOT_NAME = os.getenv("CHATBOT_NAME", "Aria")


def get_conversation_history(db, session_id: str, limit: int = 10) -> list:
    """Recupera los últimos mensajes de la conversación (memoria a corto plazo)."""
    messages = (
        db.query(Message)
        .filter(Message.session_id == session_id)
        .order_by(Message.created_at.desc())
        .limit(limit)
        .all()
    )
    return [{"role": m.role, "content": m.content} for m in reversed(messages)]


def build_system_prompt(user: User, profile: dict, relevant_memories: list) -> str:
    """
    Construye el system prompt combinando:
    - Personalidad base del chatbot
    - Perfil aprendido del usuario
    - Memorias semánticas relevantes para el mensaje actual
    """
    name = user.name if user.name else "usuario"
    interests = profile.get("interests", [])
    tone = profile.get("tone", "informal")
    preferred_length = profile.get("preferred_response_length", "media")
    other = profile.get("other", "")
    interests_text = ", ".join(interests) if interests else "desconocidos aún"

    # Formatear memorias relevantes
    memories_text = ""
    if relevant_memories:
        memories_text = "\nRecuerdos relevantes de conversaciones anteriores:\n"
        memories_text += "\n".join([f"- {m}" for m in relevant_memories])

    return f"""Eres {CHATBOT_NAME}, un asistente inteligente y amigable con personalidad propia.

Tu personalidad:
- Eres curioso, empático y con buen humor
- Te adaptas completamente al usuario
- Recuerdas lo que el usuario te ha contado

Lo que sabes de este usuario:
- Nombre: {name}
- Intereses: {interests_text}
- Tono preferido: {tone}
- Prefiere respuestas: {preferred_length}
- Otros datos: {other if other else "ninguno aún"}
- Mensajes enviados en total: {user.message_count}
{memories_text}

Instrucciones:
- Responde en el idioma del usuario
- Usa un tono {tone}
- Da respuestas de longitud {preferred_length}
- Si conoces sus intereses, menciónalos cuando sea natural
- Si el usuario te dice su nombre, úsalo de vez en cuando
- Nunca digas que eres una IA de Groq o Meta, eres {CHATBOT_NAME}
- Usa los recuerdos relevantes cuando sea apropiado, de forma natural
"""


async def process_message(session_id: str, message: str, user_name: str | None = None) -> dict:
    """Procesa un mensaje del usuario y devuelve la respuesta del chatbot."""
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

        # 2. Recuperar historial, perfil y memorias relevantes
        history = get_conversation_history(db, session_id)
        profile = get_user_profile(session_id)

        # Buscar memorias semánticas relevantes para el mensaje actual
        relevant_memories = search_relevant_messages(session_id, message)

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
        db.refresh(user_msg)

        # Guardar embedding del mensaje
        store_message(
            session_id=session_id,
            message_id=str(user_msg.id),
            text=message,
            role="user"
        )

        # 4. Llamar a Groq
        groq_messages = history + [{"role": "user", "content": message}]

        completion = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": build_system_prompt(user, profile, relevant_memories)},
                *groq_messages
            ],
            max_tokens=1000,
            temperature=0.7
        )

        bot_response = completion.choices[0].message.content
        tokens_used = completion.usage.total_tokens

        # 5. Guardar respuesta del bot
        bot_msg = Message(
            session_id=session_id,
            role="assistant",
            content=bot_response,
            tokens_used=tokens_used
        )
        db.add(bot_msg)
        db.commit()

        # 6. Analizar conversación cada 5 mensajes
        if user.message_count % 3 == 0:
            print(f"🧠 Analizando conversación de {session_id}...")
            analyze_conversation(session_id)
            profile_check = get_user_profile(session_id)
            print(f"🔍 Perfil recuperado para {session_id}: {profile}")
            print(f"📝 Perfil guardado: {profile_check}")

        return {
            "response": bot_response,
            "session_id": session_id,
            "message_count": user.message_count
        }

    finally:
        db.close()