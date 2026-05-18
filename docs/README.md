# 🤖 Rogobot — Chatbot IA con Memoria y Personalidad Propia

Proyecto de fin de curso — Chatbot inteligente que aprende de las conversaciones
y adapta su comportamiento a cada usuario usando técnicas modernas de NLP.

## ✨ Características

- 🧠 **Memoria conversacional** — recuerda el contexto dentro de cada conversación
- 👤 **Personalidad adaptativa** — aprende sobre el usuario entre sesiones
- 🌍 **Multiidioma** — responde en el idioma del usuario
- ⚡ **Respuestas rápidas** — powered by Groq (LLaMA 3.3 70B)
- 💾 **Historial persistente** — guarda las conversaciones en SQLite
- 🎨 **Interfaz web moderna** — frontend limpio y responsive

## 🛠️ Stack tecnológico

| Capa | Tecnología |
|------|-----------|
| Backend | FastAPI + Python |
| LLM | Groq API (LLaMA 3.3 70B) |
| Base de datos | SQLite + SQLAlchemy |
| Embeddings | sentence-transformers |
| Frontend | HTML + CSS + JavaScript |

## 🚀 Instalación y uso

### 1. Clona el repositorio
```bash
git clone https://github.com/RoGoLo-05/rogobot.git
cd rogobot
```

### 2. Crea el entorno virtual
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux
```

### 3. Instala las dependencias
```bash
pip install -r requirements.txt
```

### 4. Configura las variables de entorno
```bash
copy .env.example .env  # Windows
cp .env.example .env    # Mac/Linux
```
Edita el `.env` y añade tu API key de Groq (gratuita en https://console.groq.com)

### 5. Arranca el servidor
```bash
cd backend
python main.py
```

### 6. Abre el navegador
http://localhost:8000

## 📁 Estructura del proyecto

```
rogobot/
├── backend/
│   ├── main.py          # Servidor FastAPI + endpoints
│   ├── chat.py          # Lógica del chatbot
│   ├── personality.py   # Sistema de personalidad adaptativa
│   └── database.py      # Modelos SQLite
├── frontend/
│   ├── index.html       # Interfaz web
│   ├── style.css        # Estilos
│   └── app.js           # Lógica del frontend
├── docs/                # Documentación del proyecto
├── .env.example         # Plantilla de configuración
└── requirements.txt     # Dependencias
```

## 📚 Documentación

Toda la documentación del proyecto está en la carpeta `/docs`:

- 📋 [Análisis y Diseño](docs/analisis_diseno.md)
- 👤 [Manual de Usuario](docs/manual_usuario.md)

## 🔑 API Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/health` | Estado del servidor |
| POST | `/chat` | Enviar mensaje al chatbot |
| GET | `/history/{session_id}` | Ver historial |
| DELETE | `/history/{session_id}` | Borrar historial |
| GET | `/docs` | Documentación interactiva |

## 👨‍💻 Autor

Roberto — Proyecto TFG Máster IA
