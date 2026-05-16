const API_URL = "http://localhost:8000";

// El session_id se genera UNA sola vez y nunca cambia
// Ni al borrar la conversación ni al recargar la página
if (!localStorage.getItem("session_id")) {
    const id = "user_" + Date.now() + "_" + Math.random().toString(36).substr(2, 5);
    localStorage.setItem("session_id", id);
}
const sessionId = localStorage.getItem("session_id");

let userName = localStorage.getItem("user_name") || null;

// Elementos del DOM
const welcomeScreen = document.getElementById("welcome-screen");
const chatScreen    = document.getElementById("chat-screen");
const nameInput     = document.getElementById("name-input");
const startBtn      = document.getElementById("start-btn");
const messagesDiv   = document.getElementById("messages");
const messageInput  = document.getElementById("message-input");
const sendBtn       = document.getElementById("send-btn");
const clearBtn      = document.getElementById("clear-btn");

// Si ya hay sesión guardada, ir directo al chat
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

    addMessage("user", message);
    messageInput.value = "";
    sendBtn.disabled = true;

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
        removeMessage(typingId);
        addMessage("bot", data.response);

    } catch (error) {
        removeMessage(typingId);
        addMessage("bot", "❌ Error al conectar con el servidor. ¿Está arrancado?");
    }

    sendBtn.disabled = false;
    messageInput.focus();
}

async function handleClear() {
    if (!confirm("¿Borrar toda la conversación?")) return;

    await fetch(`${API_URL}/history/${sessionId}`, { method: "DELETE" });

    messagesDiv.innerHTML = "";
    localStorage.removeItem("user_name");
    userName = null;

    // El session_id NO se borra — así el perfil aprendido se mantiene
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
    div.scrollIntoView({ behavior: "smooth" });
    return id;
}

function removeMessage(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
}