"""
personality.py — Sistema de personalidad adaptativa

Este módulo analiza las conversaciones y extrae información sobre el usuario
para que el chatbot lo recuerde entre sesiones y adapte su comportamiento.

Ejemplos de cosas que aprende:
- Nombre, intereses, tono preferido
- Temas que le gustan o disgustan
- Si prefiere respuestas cortas o largas
"""

import json
from database import SessionLocal, User, Message
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")


def get_user_profile(session_id: str) -> dict:
    """
    Recupera el perfil aprendido del usuario desde la base de datos.
    Si no existe, devuelve un perfil vacío.
    """
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.session_id == session_id).first()
        if not user or not user.profile_json:
            return {}
        return json.loads(user.profile_json)
    finally:
        db.close()


def save_user_profile(session_id: str, profile: dict):
    """
    Guarda el perfil actualizado del usuario en la base de datos.
    """
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.session_id == session_id).first()
        if user:
            user.profile_json = json.dumps(profile, ensure_ascii=False)
            db.commit()
    finally:
        db.close()


def analyze_conversation(session_id: str):
    """
    Analiza los últimos mensajes del usuario y actualiza su perfil.
    Se llama cada 5 mensajes para no sobrecargar la API.

    El análisis lo hace el propio LLM — le pedimos que extraiga
    información relevante del usuario en formato JSON.
    """
    db = SessionLocal()
    try:
        # Obtener los últimos 10 mensajes del usuario
        messages = (
            db.query(Message)
            .filter(
                Message.session_id == session_id,
                Message.role == "user"
            )
            .order_by(Message.created_at.desc())
            .limit(10)
            .all()
        )

        if not messages:
            return

        # Perfil actual
        current_profile = get_user_profile(session_id)

        # Construir texto de los mensajes para analizar
        conversation_text = "\n".join([f"- {m.content}" for m in reversed(messages)])

        # Pedirle al LLM que extraiga información del usuario
        prompt = f"""Analiza estos mensajes de un usuario y extrae información relevante sobre él.
        
Mensajes del usuario:
{conversation_text}

Perfil actual conocido:
{json.dumps(current_profile, ensure_ascii=False)}

Devuelve SOLO un JSON con esta estructura (sin explicaciones, solo el JSON):
{{
    "interests": ["lista de intereses detectados"],
    "tone": "formal/informal/técnico/casual",
    "name": "nombre si lo mencionó o null",
    "language": "idioma que usa",
    "preferred_response_length": "corta/media/larga",
    "other": "cualquier otra info relevante"
}}

Combina la información nueva con la del perfil actual. No pierdas datos anteriores."""

        completion = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.1  # Muy bajo para respuestas consistentes
        )

        response_text = completion.choices[0].message.content.strip()

        # Limpiar la respuesta por si viene con ```json
        if "```" in response_text:
            response_text = response_text.split("```")[1]
            if response_text.startswith("json"):
                response_text = response_text[4:]

        new_profile = json.loads(response_text)
        save_user_profile(session_id, new_profile)

    except Exception as e:
        print(f"Error analizando conversación: {e}")
    finally:
        db.close()