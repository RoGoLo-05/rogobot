// Configuración 
const API_URL = "http://localhost:8000";

// Generamos un ID único para esta sesión del usuario
// Se guarda en localStorage para que persista si recargas la página
let sessionId = localStorage.getItem("session_id");
if (!sessionId) {
    sessionId = "user_" + Math.random().toString(36).substr(2, 9);
    localStorage.setItem("session_id", sessionId);
}

let userName = localStorage.getItem("user_name") || null;

// Elementos del DOM 
const welcomeScreen   = document.getElementById("welcome-screen");
const chatScreen      = document.getElementById("chat-screen");
const nameInput       = document.getElementById("name-input");
const startBtn        = document.getElementById("start-btn");
const messagesDiv     = document.getElementById("messages");
const messageInput    = document.getElementById("message-input");
const sendBtn         = document.getElementById("send-btn");
const clearBtn        = document.getElementById("clear-btn");

// Inicio 
// Si el usuario ya tiene nombre guardado, saltamos la bienvenida
if (userName) {
    showChat();
    loadHistory();
}

// Eventos 
startBtn.addEventListener("click", handleStart);
nameInput.addEventListener("keydown", e => { if (e.key === "Enter") handleStart(); });
sendBtn.addEventListener("click", handleSend);
messageInput.addEventListener("keydown", e => { if (e.key === "Enter") handleSend(); });
clearBtn.addEventListener("click", handleClear);

// Funciones 
function handleStart() {
    const name = nameInput.value.trim();
    if (!name) {
        nameInput.placeholder = "Por favor escribe tu nombre";
        return;
    }
    userName = name;
    localStorage.setItem("user_name", userName);
    showChat();
    addMessage("bot", `¡Hola ${userName}! Soy Aria 🤖 ¿En qué puedo ayudarte hoy?`);
}

function showChat() {
    welcomeScreen.classList.add("hidden");
    chatScreen.classList.remove("hidden");
    messageInput.focus();
}

async function handleSend() {
    const message = messageInput.value.trim();
    if (!message) return;

    // Mostrar mensaje del usuario
    addMessage("user", message);
    messageInput.value = "";
    sendBtn.disabled = true;

    // Mostrar indicador de escritura
    const typingId = addMessage("bot", "Escribiendo...", "typing");

    try {
        const response = await fetch(`${API_URL}/chat`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                session_id: sessionId,
                message: message,
                user_name: userName
            })
        });

        const data = await response.json();

        // Quitar indicador de escritura y mostrar respuesta
        removeMessage(typingId);
        addMessage("bot", data.response);

    } catch (error) {
        removeMessage(typingId);
        addMessage("bot", "Error al conectar con el servidor. ¿Está arrancado?");
    }

    sendBtn.disabled = false;
    messageInput.focus();
}

async function handleClear() {
    if (!confirm("¿Borrar toda la conversación?")) return;

    await fetch(`${API_URL}/history/${sessionId}`, { method: "DELETE" });

    messagesDiv.innerHTML = "";
    localStorage.removeItem("user_name");
    localStorage.removeItem("session_id");

    // Reiniciar sesión
    sessionId = "user_" + Math.random().toString(36).substr(2, 9);
    localStorage.setItem("session_id", sessionId);
    userName = null;

    chatScreen.classList.add("hidden");
    welcomeScreen.classList.remove("hidden");
}

async function loadHistory() {
    try {
        const response = await fetch(`${API_URL}/history/${sessionId}`);
        const data = await response.json();

        data.messages.forEach(msg => {
            addMessage(msg.role === "user" ? "user" : "bot", msg.content);
        });
    } catch (error) {
        console.error("Error cargando historial:", error);
    }
}

function addMessage(role, content, extraClass = "") {
    const div = document.createElement("div");
    const id = "msg_" + Date.now() + Math.random();
    div.id = id;
    div.classList.add("message", role);
    if (extraClass) div.classList.add(extraClass);
    div.textContent = content;
    messagesDiv.appendChild(div);

    // Scroll automático al último mensaje
    div.scrollIntoView({ behavior: "smooth" });

    return id;
}

function removeMessage(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
}