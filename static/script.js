document.addEventListener('DOMContentLoaded', () => {
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const chatHistory = document.getElementById('chat-history');
    const ingestBtn = document.getElementById('ingest-btn');
    const toast = document.getElementById('toast');

    // Function to show toast
    function showToast(message, isError = false) {
        toast.textContent = message;
        toast.style.background = isError ? "rgba(234, 63, 63, 0.9)" : "rgba(46, 172, 89, 0.9)";
        toast.classList.add('show');
        setTimeout(() => {
            toast.classList.remove('show');
        }, 3000);
    }

    // Function to append a message to the chat
    function appendMessage(sender, text) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message');
        messageDiv.classList.add(sender === 'user' ? 'user-message' : 'ai-message');

        const avatar = document.createElement('div');
        avatar.classList.add('avatar');
        avatar.classList.add(sender === 'user' ? 'user-avatar' : 'ai-avatar');
        avatar.textContent = sender === 'user' ? 'U' : 'AI';

        const content = document.createElement('div');
        content.classList.add('message-content');
        
        // Handle line breaks
        content.innerHTML = text.replace(/\n/g, '<br>');

        messageDiv.appendChild(avatar);
        messageDiv.appendChild(content);

        chatHistory.appendChild(messageDiv);
        scrollToBottom();
    }

    function scrollToBottom() {
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }

    // Show typing indicator
    function showTypingIndicator() {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', 'ai-message');
        messageDiv.id = 'typing-indicator-msg';

        const avatar = document.createElement('div');
        avatar.classList.add('avatar', 'ai-avatar');
        avatar.textContent = 'AI';

        const content = document.createElement('div');
        content.classList.add('message-content');
        content.innerHTML = `
            <div class="typing-indicator">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            </div>
        `;

        messageDiv.appendChild(avatar);
        messageDiv.appendChild(content);
        chatHistory.appendChild(messageDiv);
        scrollToBottom();
    }

    function removeTypingIndicator() {
        const indicator = document.getElementById('typing-indicator-msg');
        if (indicator) {
            indicator.remove();
        }
    }

    // Handle Form Submit
    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const prompt = userInput.value.trim();
        if (!prompt) return;

        // Clear input
        userInput.value = '';
        
        // Append User Message
        appendMessage('user', prompt);

        // Show typing indicator
        showTypingIndicator();

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ prompt: prompt })
            });

            const data = await response.json();
            
            removeTypingIndicator();

            if (response.ok) {
                appendMessage('ai', data.answer);
            } else {
                appendMessage('ai', `Error: ${data.detail || 'Failed to get response.'}`);
            }
        } catch (error) {
            removeTypingIndicator();
            appendMessage('ai', 'Error: Could not connect to the server.');
        }
    });

    // Handle Ingest Button
    ingestBtn.addEventListener('click', async () => {
        ingestBtn.disabled = true;
        ingestBtn.style.opacity = '0.5';
        ingestBtn.textContent = 'Ingesting...';

        try {
            const response = await fetch('/api/ingest', {
                method: 'POST'
            });

            const data = await response.json();

            if (response.ok) {
                showToast(data.message);
            } else {
                showToast(data.detail || 'Ingestion failed.', true);
            }
        } catch (error) {
            showToast('Network error during ingestion.', true);
        } finally {
            ingestBtn.disabled = false;
            ingestBtn.style.opacity = '1';
            ingestBtn.textContent = 'Ingest Corpus';
        }
    });
});
