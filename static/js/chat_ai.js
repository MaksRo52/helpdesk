document.addEventListener('DOMContentLoaded', function () {
    const chatBtn = document.getElementById("neuroChatBtn");
    const chatWindow = document.getElementById("neuroChat");
    const closeBtn = document.getElementById("closeNeuroChat");
    const sendBtn = document.getElementById("sendNeuroBtn");
    const chatMessages = document.getElementById("chatMessages");
    const inputField = document.getElementById("neuroInput");

    chatBtn.addEventListener("click", function () {
        chatWindow.style.display = chatWindow.style.display === 'none' ? 'block' : 'none';
    });

    closeBtn.addEventListener("click", function () {
        chatWindow.style.display = 'none';
    });

    document.getElementById("clearChatBtn").addEventListener("click", function () {
    fetch("/clear-context/")
        .then(response => response.json())
        .then(data => {
            chatMessages.innerHTML = '';
            console.log("Контекст очищен:", data.status);
        });
});

    sendBtn.addEventListener("click", function () {
        const userInput = inputField.value.trim();
        if (!userInput) return;

        chatMessages.innerHTML += `<div><b>🧑 Вы:</b> ${userInput}</div>`;
        inputField.value = '';

        const messageWrapper = document.createElement("div");
        messageWrapper.innerHTML = `<b>💻 Нейросеть:</b><pre style="white-space: pre-wrap; word-break: break-word;" id="streamed-text"></pre>`;
        chatMessages.appendChild(messageWrapper);

        const streamedText = messageWrapper.querySelector("#streamed-text");

        const eventSource = new EventSource(`/stream-gemini/?prompt=${encodeURIComponent(userInput)}`);

        let fullText = "";

        eventSource.onmessage = function (event) {
            fullText += event.data;
            streamedText.innerHTML = fullText;
            chatMessages.scrollTop = chatMessages.scrollHeight;
        };

        eventSource.onerror = function () {
            eventSource.close();
        };
    });

    inputField.addEventListener('keydown', function(event) {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault(); // чтобы не переносило строку
            sendBtn.click();        // отправляем сообщение
        }
    });
});