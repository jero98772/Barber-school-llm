document.addEventListener('DOMContentLoaded', function() {
    const chatContainer = document.getElementById('chat-container');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const clearBtn = document.getElementById('clear-btn');
    
    // Generate a unique session ID for this chat
    const sessionId = 'session_' + Date.now();
    
    // Function to add a message to the chat
  function addMessage(content, isUser) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`; // Clases actualizadas
    
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
    // Function to create a streaming bot message
    function createStreamingMessage() {
        const botMessageContent = addMessage('', false);
        return botMessageContent;
    }
    
    // Function to send a message and handle streaming response
    async function sendMessage() {
        const message = userInput.value.trim();
        if (message === '') return;
        
        // Add user message to chat
        addMessage(message, true);
        userInput.value = '';
        
        try {
            // First send the message to the server
            const sendResponse = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    session_id: sessionId
                }),
            });
            
            // Create bot message container for streaming content
            const streamingContainer = createStreamingMessage();
            
            // Connect to the streaming endpoint
            const eventSource = new EventSource(`/stream/${sessionId}`);
            
            let responseText = '';
            
            eventSource.onmessage = function(event) {
                const data = JSON.parse(event.data);
                
                if (data.error) {
                    streamingContainer.textContent = `Error: ${data.error}`;
                    eventSource.close();
                    return;
                }
                
                if (data.status === 'complete') {
                    eventSource.close();
                    return;
                }
                
                if (data.content) {
                    responseText += data.content;
                    streamingContainer.textContent = responseText;
                    
                    // Scroll to the bottom of the chat
                    chatContainer.scrollTop = chatContainer.scrollHeight;
                }
            };
            
            eventSource.onerror = function() {
                if (responseText === '') {
                    streamingContainer.textContent = 'An error occurred. Please try again.';
                }
                eventSource.close();
            };
            
        } catch (error) {
            console.error('Error:', error);
            addMessage('An error occurred. Please try again.', false);
        }
    }
    
    // Function to clear chat history
    async function clearChat() {
        try {
            await fetch(`/history/${sessionId}`, {
                method: 'DELETE',
            });
            chatContainer.innerHTML = '';
        } catch (error) {
            console.error('Error clearing chat:', error);
        }
    }
    
    // Event listeners
    sendBtn.addEventListener('click', sendMessage);
    userInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
    clearBtn.addEventListener('click', clearChat);
    
    // Load any existing chat history
    async function loadHistory() {
        try {
            const response = await fetch(`/history/${sessionId}`);
            const data = await response.json();
            
            if (data.history && data.history.length > 0) {
                data.history.forEach(msg => {
                    addMessage(msg.content, msg.role === 'user');
                });
            }
        } catch (error) {
            console.error('Error loading history:', error);
        }
    }
    
    // Load history when page loads
    loadHistory();
});


