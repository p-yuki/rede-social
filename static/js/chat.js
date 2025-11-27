const socket = io();

// Abrir/fechar chat
const chatBtn = document.getElementById("chatButton");
const chatWindow = document.getElementById("chatWindow");

chatBtn.addEventListener("click", () => {
    chatWindow.style.display =
        chatWindow.style.display === "flex" ? "none" : "flex";
});

// Enviar mensagem
document.getElementById("sendBtn").onclick = () => {
    const msg = document.getElementById("messageInput").value;
    if (!msg.trim()) return;

    socket.emit("mensagem", msg);

    document.getElementById("messages").innerHTML +=
        `<div><b>Você:</b> ${msg}</div>`;

    document.getElementById("messageInput").value = "";
};

// Receber mensagem do servidor
socket.on("resposta", (msg) => {
    document.getElementById("messages").innerHTML +=
        `<div><b>Bot:</b> ${msg}</div>`;
});