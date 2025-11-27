let room = "bloco";
let username = prompt("Seu nome:") ?? "Usuário";
const socket = io();

// Trocar de sala
function trocarSala(novaSala) {
    room = novaSala;
    document.getElementById("chat-title").textContent =
        novaSala === "bloco" ? "Chat do Bloco" : "Chat da Assembleia 🏛️";

    document.getElementById("messages").innerHTML = "";

    socket.emit("join", { username, room });
}

socket.on("connect", () => {
    socket.emit("join", { username, room });
});

socket.on("users", (users) => {
    const ul = document.getElementById("users");
    ul.innerHTML = "";
    users.forEach((u) => {
        const li = document.createElement("li");
        li.textContent = u;
        ul.appendChild(li);
    });
});

socket.on("system_message", (data) => {
    addSystem(data.msg);
});

socket.on("message", (data) => {
    addMessage(data.username, data.msg);
});

// Enviar mensagem
document.getElementById("form").addEventListener("submit", (e) => {
    e.preventDefault();
    const input = document.getElementById("input");
    if (input.value.trim() === "") return;

    socket.emit("message", {
        username,
        msg: input.value,
        room
    });

    input.value = "";
});

function addSystem(msg) {
    let box = document.getElementById("messages");
    let el = document.createElement("div");
    el.classList.add("system");
    el.textContent = msg;
    box.appendChild(el);
    box.scrollTop = box.scrollHeight;
}

function addMessage(user, msg) {
    let box = document.getElementById("messages");
    let el = document.createElement("div");
    el.classList.add("bubble");

    if (user === username) el.classList.add("me");

    el.innerHTML = `<strong>${user}:</strong> <span>${msg}</span>`;

    box.appendChild(el);
    box.scrollTop = box.scrollHeight;
}