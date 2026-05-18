# 📋 Análisis y Diseño — Rogobot

## 1. Introducción

Rogobot es un chatbot inteligente desarrollado como proyecto de fin de curso.
El objetivo es crear un asistente conversacional que aprenda de las interacciones
y adapte su comportamiento a cada usuario, usando técnicas modernas de NLP.

## 2. Análisis de requisitos

### Requisitos funcionales

| ID | Requisito |
|----|-----------|
| RF01 | El sistema debe responder mensajes en lenguaje natural |
| RF02 | El sistema debe recordar el contexto dentro de una conversación |
| RF03 | El sistema debe aprender sobre el usuario entre sesiones |
| RF04 | El sistema debe adaptarse al tono e idioma del usuario |
| RF05 | El sistema debe permitir borrar el historial |
| RF06 | El sistema debe tener una interfaz web accesible |

### Requisitos no funcionales

| ID | Requisito |
|----|-----------|
| RNF01 | Tiempo de respuesta menor a 3 segundos |
| RNF02 | Interfaz responsive y moderna |
| RNF03 | API documentada automáticamente |
| RNF04 | Código comentado y mantenible |

## 3. Arquitectura del sistema
```
┌─────────────────────────────────────────────┐
│                  USUARIO                    │
└───────────────────┬─────────────────────────┘
│ HTTP
┌───────────────────▼─────────────────────────┐
│              FRONTEND                       │
│         HTML + CSS + JavaScript             │
│  - Pantalla de bienvenida                   │
│  - Interfaz de chat                         │
│  - Gestión de sesión (localStorage)         │
└───────────────────┬─────────────────────────┘
│ REST API
┌───────────────────▼─────────────────────────┐
│              BACKEND (FastAPI)              │
│                                             │
│  ┌──────────┐  ┌───────────┐  ┌──────────┐  │
│  │ chat.py  │  │personality│  │database  │  │
│  │          │  │   .py     │  │   .py    │  │
│  └────┬─────┘  └─────┬─────┘  └────┬─────┘  │
└───────┼──────────────┼─────────────┼────────┘
│              │             │
┌───────▼──────┐ ┌─────▼──────┐ ┌───▼────────┐
│   GROQ API   │ │  ANÁLISIS  │ │  SQLite    │
│  LLaMA 3.3   │ │    NLP     │ │  Database  │
│      70B     │ │            │ │            │
└──────────────┘ └────────────┘ └────────────┘
```

## 4. Diseño de la base de datos

### Tabla `users`
| Campo        | Tipo          | Descripción                             |
|--------------|---------------|-----------------------------------------|
| id           | INTEGER       | Clave primaria                         |
| session_id   | STRING        | ID único de sesión                    |
| name         | STRING        | Nombre del usuario                      |
| message_count| INTEGER       | Total de mensajes                       |
| created_at   | DATETIME      | Fecha de registro                       |
| last_seen    | DATETIME      | Última actividad                        |
| profile_json | TEXT          | Perfil aprendido (JSON)               |

### Tabla `messages`
| Campo        | Tipo          | Descripción                             |
|--------------|---------------|-----------------------------------------|
| id           | INTEGER       | Clave primaria                         |
| session_id   | STRING        | ID de sesión                            |
| role         | STRING        | "user" o "assistant"                  |
| content      | TEXT          | Contenido del mensaje                   |
| created_at   | DATETIME      | Fecha del mensaje                       |
| tokens_used  | INTEGER       | Tokens consumidos                       |

### Tabla `personality_snapshots`
| Campo        | Tipo          | Descripción                             |
|--------------|---------------|-----------------------------------------|
| id           | INTEGER       | Clave primaria                         |
| session_id   | STRING        | ID de sesión                            |
| snapshot     | TEXT          | Estado de personalidad (JSON)           |
| created_at   | DATETIME      | Fecha del snapshot                      |

## 5. Flujo de una conversación
```
Usuario escribe mensaje
│
▼
FastAPI recibe la petición POST /chat
│
▼
Se busca o crea el usuario en SQLite
│
▼
Se recupera el historial (últimos 10 mensajes)
│
▼
Se recupera el perfil aprendido del usuario
│
▼
Se construye el system prompt con toda la info
│
▼
Se llama a Groq API (LLaMA 3.3 70B)
│
▼
Se guarda la respuesta en SQLite
│
▼
Cada 5 mensajes → se analiza la conversación
y se actualiza el perfil del usuario
│
▼
Se devuelve la respuesta al frontend
```

## 6. Tecnologías utilizadas

### FastAPI
Framework web moderno para Python. Elegido por su rendimiento,
tipado estático y generación automática de documentación.

### Groq + LLaMA 3.3 70B
Groq es una plataforma de inferencia ultrarrápida. LLaMA 3.3 70B
es un modelo open-source de Meta con capacidades similares a GPT-4.
Se eligió por ser gratuito y muy potente.

### SQLite + SQLAlchemy
Base de datos ligera que no requiere servidor. SQLAlchemy permite
trabajar con ella usando Python puro en lugar de SQL directo.

### sentence-transformers
Librería para generar embeddings semánticos. Permite comparar
textos por significado, no solo por palabras exactas.

## 7. Decisiones de diseño

**¿Por qué Groq y no OpenAI?**
Groq ofrece una API gratuita con modelos de calidad similar.
Para un proyecto académico es la opción más accesible.

**¿Por qué SQLite y no PostgreSQL?**
SQLite no requiere instalar ni configurar nada. Para el alcance
de este proyecto es más que suficiente.

**¿Por qué analizar el perfil cada 3 mensajes?**
Para no hacer una llamada extra a la API en cada mensaje,
lo que encarecería el uso y ralentizaría las respuestas.
