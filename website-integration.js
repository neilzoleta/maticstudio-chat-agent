/**
 * MATIC Studio Chat Agent - Website Integration
 * 
 * Add this script to your website to integrate the chat agent.
 * Replace 'YOUR_RENDER_URL' with your actual Render.com deployment URL.
 */

(function() {
    'use strict';
    
    // Configuration
    const CHAT_API_URL = 'YOUR_RENDER_URL'; // Replace with your Render.com URL
    const CHAT_CONTAINER_ID = 'maticstudio-chat';
    
    // Chat state
    let sessionId = null;
    let conversationHistory = [];
    let isProcessing = false;
    
    // Create chat widget HTML
    function createChatWidget() {
        const chatHTML = `
            <div id="${CHAT_CONTAINER_ID}" class="maticstudio-chat-widget">
                <div class="chat-header">
                    <div class="chat-title">
                        <h3>MATIC Studio Assistant</h3>
                        <span class="status-indicator">🟢 Online</span>
                    </div>
                    <button class="chat-toggle" onclick="toggleChat()">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
                        </svg>
                    </button>
                </div>
                
                <div class="chat-body" style="display: none;">
                    <div class="chat-messages" id="chat-messages">
                        <div class="message bot-message">
                            <p>Hello! I'm your MATIC Studio assistant. I'm here to help you discover how automation can transform your business processes. What would you like to learn about today?</p>
                        </div>
                    </div>
                    
                    <div class="quick-replies" id="quick-replies">
                        <button class="quick-reply-btn" onclick="sendQuickReply('Set a tune-up call?')">Set a tune-up call?</button>
                        <button class="quick-reply-btn" onclick="sendQuickReply('What do you offer?')">What do you offer?</button>
                        <button class="quick-reply-btn" onclick="sendQuickReply('Learn more about MATICStudio')">Learn more about MATICStudio</button>
                    </div>
                    
                    <div class="chat-input">
                        <input type="text" id="message-input" placeholder="Type your message..." onkeypress="handleKeyPress(event)">
                        <button onclick="sendMessage()" id="send-btn">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <line x1="22" y1="2" x2="11" y2="13"></line>
                                <polygon points="22,2 15,22 11,13 2,9"></polygon>
                            </svg>
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        // Add to page
        document.body.insertAdjacentHTML('beforeend', chatHTML);
        
        // Add CSS
        addChatStyles();
    }
    
    // Add chat styles
    function addChatStyles() {
        const styles = `
            <style>
                .maticstudio-chat-widget {
                    position: fixed;
                    bottom: 20px;
                    right: 20px;
                    width: 350px;
                    max-height: 500px;
                    background: white;
                    border-radius: 12px;
                    box-shadow: 0 4px 20px rgba(0,0,0,0.15);
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    z-index: 10000;
                    border: 1px solid #e9ecef;
                }
                
                .chat-header {
                    background: #212529;
                    color: white;
                    padding: 15px 20px;
                    border-radius: 12px 12px 0 0;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                }
                
                .chat-title h3 {
                    margin: 0;
                    font-size: 16px;
                    font-weight: 500;
                }
                
                .status-indicator {
                    font-size: 12px;
                    opacity: 0.8;
                }
                
                .chat-toggle {
                    background: none;
                    border: none;
                    color: white;
                    cursor: pointer;
                    padding: 5px;
                }
                
                .chat-body {
                    height: 400px;
                    display: flex;
                    flex-direction: column;
                }
                
                .chat-messages {
                    flex: 1;
                    padding: 15px;
                    overflow-y: auto;
                    max-height: 250px;
                }
                
                .message {
                    margin-bottom: 10px;
                    padding: 10px 12px;
                    border-radius: 8px;
                    font-size: 14px;
                    line-height: 1.4;
                }
                
                .bot-message {
                    background: #f8f9fa;
                    color: #212529;
                    border: 1px solid #e9ecef;
                }
                
                .user-message {
                    background: #212529;
                    color: white;
                    margin-left: 20px;
                }
                
                .quick-replies {
                    padding: 10px 15px;
                    border-top: 1px solid #e9ecef;
                }
                
                .quick-reply-btn {
                    display: block;
                    width: 100%;
                    background: #f8f9fa;
                    border: 1px solid #dee2e6;
                    border-radius: 8px;
                    padding: 8px 12px;
                    margin-bottom: 5px;
                    font-size: 13px;
                    color: #495057;
                    cursor: pointer;
                    text-align: left;
                    transition: all 0.2s;
                }
                
                .quick-reply-btn:hover {
                    background: #e9ecef;
                    border-color: #adb5bd;
                }
                
                .chat-input {
                    padding: 15px;
                    border-top: 1px solid #e9ecef;
                    display: flex;
                    gap: 8px;
                }
                
                .chat-input input {
                    flex: 1;
                    padding: 8px 12px;
                    border: 1px solid #dee2e6;
                    border-radius: 20px;
                    font-size: 14px;
                    outline: none;
                }
                
                .chat-input input:focus {
                    border-color: #6c757d;
                }
                
                .chat-input button {
                    width: 32px;
                    height: 32px;
                    background: #212529;
                    border: none;
                    border-radius: 50%;
                    color: white;
                    cursor: pointer;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }
                
                .chat-input button:hover {
                    background: #495057;
                }
                
                .chat-input button:disabled {
                    background: #adb5bd;
                    cursor: not-allowed;
                }
                
                .typing-indicator {
                    padding: 10px 12px;
                    background: #f8f9fa;
                    border: 1px solid #e9ecef;
                    border-radius: 8px;
                    font-size: 14px;
                    color: #6c757d;
                    margin-bottom: 10px;
                }
                
                @media (max-width: 480px) {
                    .maticstudio-chat-widget {
                        width: calc(100vw - 40px);
                        right: 20px;
                        left: 20px;
                    }
                }
            </style>
        `;
        
        document.head.insertAdjacentHTML('beforeend', styles);
    }
    
    // Toggle chat visibility
    window.toggleChat = function() {
        const chatBody = document.querySelector('.chat-body');
        const isVisible = chatBody.style.display !== 'none';
        chatBody.style.display = isVisible ? 'none' : 'block';
        
        if (!isVisible && !sessionId) {
            // Initialize session on first open
            sessionId = 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        }
    };
    
    // Send message
    window.sendMessage = function() {
        const input = document.getElementById('message-input');
        const message = input.value.trim();
        
        if (message && !isProcessing) {
            addUserMessage(message);
            input.value = '';
            sendToAPI(message);
        }
    };
    
    // Send quick reply
    window.sendQuickReply = function(message) {
        if (!isProcessing) {
            addUserMessage(message);
            sendToAPI(message);
            hideQuickReplies();
        }
    };
    
    // Handle Enter key
    window.handleKeyPress = function(event) {
        if (event.key === 'Enter') {
            sendMessage();
        }
    };
    
    // Add user message to chat
    function addUserMessage(message) {
        const messagesContainer = document.getElementById('chat-messages');
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message user-message';
        messageDiv.textContent = message;
        messagesContainer.appendChild(messageDiv);
        scrollToBottom();
    }
    
    // Add bot message to chat
    function addBotMessage(message) {
        const messagesContainer = document.getElementById('chat-messages');
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message bot-message';
        messageDiv.innerHTML = formatMessage(message);
        messagesContainer.appendChild(messageDiv);
        scrollToBottom();
    }
    
    // Format message with markdown-like formatting
    function formatMessage(message) {
        return message
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/\n/g, '<br>')
            .replace(/•/g, '•');
    }
    
    // Show typing indicator
    function showTypingIndicator() {
        const messagesContainer = document.getElementById('chat-messages');
        const typingDiv = document.createElement('div');
        typingDiv.className = 'typing-indicator';
        typingDiv.id = 'typing-indicator';
        typingDiv.innerHTML = '🤖 Thinking...';
        messagesContainer.appendChild(typingDiv);
        scrollToBottom();
    }
    
    // Hide typing indicator
    function hideTypingIndicator() {
        const typingIndicator = document.getElementById('typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }
    
    // Hide quick replies
    function hideQuickReplies() {
        const quickReplies = document.getElementById('quick-replies');
        quickReplies.style.display = 'none';
    }
    
    // Scroll to bottom of messages
    function scrollToBottom() {
        const messagesContainer = document.getElementById('chat-messages');
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
    
    // Send message to API
    async function sendToAPI(message) {
        isProcessing = true;
        showTypingIndicator();
        
        // Disable input
        const input = document.getElementById('message-input');
        const sendBtn = document.getElementById('send-btn');
        input.disabled = true;
        sendBtn.disabled = true;
        
        try {
            const response = await fetch(`${CHAT_API_URL}/api/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    conversation_history: conversationHistory,
                    session_id: sessionId
                })
            });
            
            const data = await response.json();
            
            hideTypingIndicator();
            
            if (data.status === 'success') {
                addBotMessage(data.response);
                conversationHistory.push(
                    { role: 'user', content: message },
                    { role: 'assistant', content: data.response }
                );
                
                if (data.session_id) {
                    sessionId = data.session_id;
                }
            } else {
                addBotMessage("I apologize, but I'm having trouble connecting right now. Please try again later or contact us directly at inquire@maticstudio.net.");
            }
            
        } catch (error) {
            console.error('Error sending message:', error);
            hideTypingIndicator();
            addBotMessage("I apologize, but I'm having trouble connecting right now. Please try again later or contact us directly at inquire@maticstudio.net.");
        } finally {
            // Re-enable input
            input.disabled = false;
            sendBtn.disabled = false;
            input.focus();
            isProcessing = false;
        }
    }
    
    // Initialize chat widget when DOM is loaded
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', createChatWidget);
    } else {
        createChatWidget();
    }
    
})();
