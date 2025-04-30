document.addEventListener('DOMContentLoaded', function() {
    const chatContainer = document.getElementById('chat-container');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const clearBtn = document.getElementById('clear-btn');
    const contactBtn = document.getElementById('contact-btn');
    
    // Session and contact state management
    let contactRequested = false;
    let contactFormShown = false;
    const sessionId = generateSessionId();

    // Add welcome message
    addMessage("👋 Welcome to ABC Barber's Chat! How can I help you today? You can ask me about our services, prices, or book an appointment!", false);

    // Function to generate session ID
    function generateSessionId() {
        return 'session_' + Date.now() + Math.random().toString(36).substr(2, 9);
    }

    // Unified message creation function
    function addMessage(content, isUser) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;
        
        const header = document.createElement('div');
        header.className = 'message-header';
        header.textContent = isUser ? 'You' : 'Bot';
        
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        messageContent.textContent = content;
        
        messageDiv.appendChild(header);
        messageDiv.appendChild(messageContent);
        chatContainer.appendChild(messageDiv);
        chatContainer.scrollTop = chatContainer.scrollHeight;
        
        return messageContent;
    }

    // Contact form handling
    function showContactForm() {
        if (contactFormShown) return;
        
        const modalBackdrop = document.createElement('div');
        modalBackdrop.className = 'modal-backdrop';
        modalBackdrop.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0,0,0,0.5);
            z-index: 1000;
            display: flex;
            justify-content: center;
            align-items: center;
        `;
        
        const modalContent = document.createElement('div');
        modalContent.className = 'modal-content';
        modalContent.style.cssText = `
            background-color: white;
            padding: 20px;
            border-radius: 10px;
            max-width: 500px;
            width: 90%;
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        `;
        
        modalContent.innerHTML = `
            <h2 style="color: #000; margin-top: 0;">Te contactaremos</h2>
            <p style="color: #666;">Danos tu informacion de contacto</p>
            <form id="contact-form" style="text-align: left; color: #000;">
                <div class="mb-3">
                    <label for="name" class="form-label">Nombre completo:</label>
                    <input type="text" class="form-control" id="name" required>
                </div>
                <div class="mb-3">
                    <label for="phone" class="form-label">Numero de telefono:</label>
                    <input type="tel" class="form-control" id="phone" required>
                </div>
                <div class="mb-3">
                    <label for="city" class="form-label">Ciudad:</label>
                    <input type="text" class="form-control" id="city" required>
                </div>
                <div class="mb-3">
                    <label for="notes" class="form-label">Notas:</label>
                    <textarea class="form-control" id="notes" rows="3"></textarea>
                </div>
                <div style="display: flex; justify-content: space-between;">
                    <button type="button" id="cancel-form" class="btn btn-outline-secondary">Cancel</button>
                    <button type="submit" class="btn btn-primary">Submit</button>
                </div>
            </form>
        `;

        modalBackdrop.appendChild(modalContent);
        document.body.appendChild(modalBackdrop);
        contactFormShown = true;

        // Form submission handler
        document.getElementById('contact-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = {
                session_id: sessionId,
                name: document.getElementById('name').value,
                phone: document.getElementById('phone').value,
                city: document.getElementById('city').value,
                notes: document.getElementById('notes').value
            };

            try {
                await fetch('/contact', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(formData)
                });
                
                document.body.removeChild(modalBackdrop);
                contactFormShown = false;
                addMessage(`Thank you, ${formData.name}! We'll contact you at ${formData.phone} to confirm.`, false);
            } catch (error) {
                console.error('Error:', error);
                addMessage('Error submitting form. Please try again.', false);
            }
        });

        // Cancel button handler
        document.getElementById('cancel-form').addEventListener('click', () => {
            document.body.removeChild(modalBackdrop);
            contactFormShown = false;
            addMessage("Appointment cancelled. Feel free to ask anything else!", false);
        });
    }

    // Chat message handling
    async function sendMessage() {
        const message = userInput.value.trim();
        if (!message) return;

        addMessage(message, true);
        userInput.value = '';

        try {
            // Check if message requires immediate contact form
            if (shouldTriggerContactForm(message)) {
                contactRequested = true;
                showContactForm();
                return;
            }

            // Send to backend
            await fetch('/chat', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ message, session_id: sessionId })
            });

            // Handle streaming response
            const streamingContainer = addMessage('', false);
            const eventSource = new EventSource(`/stream/${sessionId}`);
            let responseText = '';

            eventSource.onmessage = (event) => {
                const data = JSON.parse(event.data);
                if (data.content) {
                    responseText += data.content;
                    streamingContainer.textContent = responseText;
                    chatContainer.scrollTop = chatContainer.scrollHeight;
                }
                if (data.status === 'complete') eventSource.close();
            };

            eventSource.onerror = () => {
                if (!responseText) streamingContainer.textContent = 'Error connecting to server.';
                eventSource.close();
            };

        } catch (error) {
            console.error('Error:', error);
            addMessage('Error processing request. Please try again.', false);
        }
    }

    // Contact form trigger logic
    function shouldTriggerContactForm(message) {
        const msg = message.toLowerCase();
        return (
            !contactRequested && (
                (msg.includes('appointment') && (msg.includes('book') || msg.includes('schedule'))) ||
                (msg.includes('yes') && chatContainer.lastElementChild?.textContent.includes("book"))
            )
        );
    }

    // Clear chat function
    async function clearChat() {
        try {
            await fetch(`/history/${sessionId}`, { method: 'DELETE' });
            chatContainer.innerHTML = '';
            addMessage("Chat cleared! How can I help you today?", false);
            contactRequested = false;
        } catch (error) {
            console.error('Error clearing chat:', error);
        }
    }

    // Event listeners
    sendBtn.addEventListener('click', sendMessage);
    contactBtn.addEventListener('click', () => {
        contactRequested = true;
        showContactForm();
    });
    clearBtn.addEventListener('click', clearChat);
    userInput.addEventListener('keypress', (e) => e.key === 'Enter' && sendMessage());

    // Load chat history
    async function loadHistory() {
        try {
            const response = await fetch(`/history/${sessionId}`);
            const data = await response.json();
            data.history?.forEach(msg => addMessage(msg.content, msg.role === 'user'));
        } catch (error) {
            console.error('Error loading history:', error);
        }
    }
    loadHistory();
});