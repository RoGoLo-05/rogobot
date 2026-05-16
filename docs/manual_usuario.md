# 👤 Manual de Usuario — Rogobot

## ¿Qué es Rogobot?

Rogobot es un chatbot inteligente que aprende sobre ti con cada conversación.
Cuanto más hablas con él, mejor te conoce y más se adapta a tu forma de ser.

## Primeros pasos

### 1. Acceder al chatbot
Abre el navegador y ve a:
http://localhost:8000

### 2. Pantalla de bienvenida
Al entrar verás una pantalla donde te pide tu nombre.
Escribe tu nombre y pulsa **"Empezar a chatear"**.

> 💡 Tu nombre se guarda en el navegador, así que la próxima vez
> que entres no tendrás que escribirlo de nuevo.

### 3. Interfaz del chat
Una vez dentro verás:
- **Cabecera** — nombre del chatbot y botón para borrar la conversación
- **Área de mensajes** — donde aparece la conversación
- **Caja de texto** — donde escribes tus mensajes

## Cómo usar el chat

### Enviar un mensaje
Escribe en la caja de texto y pulsa **Enter** o el botón **➤**.

### Lo que puede hacer Aria

| Acción | Ejemplo |
|--------|---------|
| Conversar sobre cualquier tema | "Háblame del Sevilla FC" |
| Cambiar de idioma | "Habla en inglés a partir de ahora" |
| Adaptarse a tu tono | "Habla más informal" |
| Recordar lo que dijiste | "¿Recuerdas mi jugador favorito?" |
| Responder preguntas | "¿Qué es el machine learning?" |

### Borrar la conversación
Pulsa el icono 🗑️ en la cabecera. Esto borrará todo el historial
y volverás a la pantalla de bienvenida.

> ⚠️ Esta acción no se puede deshacer.

## Preguntas frecuentes

**¿Aria recuerda mis conversaciones anteriores?**
Sí. Cada vez que envías 3 mensajes, Aria analiza la conversación
y actualiza su conocimiento sobre ti. La próxima vez que entres,
ya sabrá tus intereses y preferencias.

**¿Puedo hablar en cualquier idioma?**
Sí. Aria detecta el idioma que usas y responde en el mismo.
También puedes pedirle explícitamente que cambie de idioma.

**¿Mis conversaciones son privadas?**
Las conversaciones se guardan localmente en tu ordenador
en una base de datos SQLite. No se envían a ningún servidor externo
salvo el texto de cada mensaje a la API de Groq para generar la respuesta.

**¿Por qué a veces tarda en responder?**
Aria llama a una API externa (Groq) para generar cada respuesta.
El tiempo depende de la conexión a internet y la carga del servidor.
Normalmente responde en menos de 3 segundos.

**¿Cómo sabe Aria mi nombre?**
Se lo dices tú en la pantalla de bienvenida. A partir de ahí,
lo recuerda durante toda la conversación y en las siguientes.

## Consejos para sacar el máximo partido

- **Cuéntale tus intereses** — cuanto más sepa de ti, mejor se adapta
- **Corrígele si se equivoca** — aprende de tus correcciones
- **Pídele que cambie su estilo** — puede ser formal, informal, gracioso...
- **Habla con naturalidad** — no hace falta usar comandos especiales