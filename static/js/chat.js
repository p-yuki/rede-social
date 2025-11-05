document.addEventListener('DOMContentLoaded', () => {
    console.log("Aplicativo Condomínio carregado! Interatividade JS iniciada.");

    // ======================================
    // 1. INTERAÇÃO GERAL (Hover/Click em Cards)
    // ======================================
    const interactiveCards = document.querySelectorAll('.feed-item, .service-card, .profile-info-card');

    interactiveCards.forEach(card => {
        if (card.classList.contains('alert-box')) return;
        
        card.style.transition = 'transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out';
        
        card.addEventListener('mouseenter', () => {
            card.style.transform = 'translateY(-3px)';
            card.style.boxShadow = '0 6px 12px rgba(0, 0, 0, 0.15)';
            card.style.cursor = 'pointer';
        });

        card.addEventListener('mouseleave', () => {
            card.style.transform = 'translateY(0)';
            card.style.boxShadow = '0 1px 4px rgba(0, 0, 0, 0.05)'; 
        });
        
        card.addEventListener('click', () => {
            const titleElement = card.querySelector('h3') || card.querySelector('span') || card.querySelector('p');
            const cardTitle = titleElement ? titleElement.textContent.trim().substring(0, 30) + '...' : 'Card';
            // console.log(`Item "${cardTitle}" clicado!`);
        });
    });


    // ======================================
    // 2. INTERAÇÃO DA PÁGINA DE CHAT
    // ======================================
    const chatItems = document.querySelectorAll('.chat-item');
    const messagesDisplay = document.querySelector('.messages-display');
    const messageInput = document.querySelector('.message-input-area input');
    const sendButton = document.querySelector('.message-input-area button');

    if (chatItems.length > 0) {
        
        // Função para alternar Chat Ativo...
        chatItems.forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                chatItems.forEach(i => i.classList.remove('active-chat'));
                item.classList.add('active-chat');

                const chatName = item.querySelector('span').textContent;
                messagesDisplay.innerHTML = ''; 
                
                const welcomeMessage = document.createElement('div');
                welcomeMessage.className = 'message received';
                welcomeMessage.innerHTML = `<div class="message-avatar received-avatar"></div><div class="message-bubble">Bem-vindo ao chat: <strong>${chatName}</strong>.</div>`;
                messagesDisplay.appendChild(welcomeMessage);
                messagesDisplay.scrollTop = messagesDisplay.scrollHeight;
            });
        });

        // Função para simular Envio de Mensagem...
        const sendMessage = () => {
            const text = messageInput.value.trim();
            if (text === "") return;

            const newMessage = document.createElement('div');
            newMessage.className = 'message sent';
            newMessage.innerHTML = `<div class="message-bubble">${text}</div><div class="message-avatar sent-avatar"></div>`;
            
            messagesDisplay.appendChild(newMessage);
            messageInput.value = '';
            messagesDisplay.scrollTop = messagesDisplay.scrollHeight;

            setTimeout(() => {
                const reply = document.createElement('div');
                reply.className = 'message received';
                reply.innerHTML = `<div class="message-avatar received-avatar"></div><div class="message-bubble">Mensagem enviada! (Simulação)</div>`;
                messagesDisplay.appendChild(reply);
                messagesDisplay.scrollTop = messagesDisplay.scrollHeight;
            }, 1000);
        };

        sendButton.addEventListener('click', sendMessage);
        messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
        
        if(chatItems[0]) {
            chatItems[0].click();
        }
    }
});