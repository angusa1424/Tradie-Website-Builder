class LiveChat {
    constructor() {
        this.chatWindow = null;
        this.chatButton = null;
        this.messages = [];
        this.isOpen = false;
        this.agentTyping = false;
        this.init();
    }

    init() {
        this.createChatButton();
        this.createChatWindow();
        this.loadChatHistory();
    }

    createChatButton() {
        this.chatButton = document.createElement('button');
        this.chatButton.className = 'chat-button';
        this.chatButton.innerHTML = `
            <i class="fas fa-comments"></i>
            <span>Chat with us</span>
        `;
        this.chatButton.addEventListener('click', () => this.toggleChat());
        document.body.appendChild(this.chatButton);
    }

    createChatWindow() {
        this.chatWindow = document.createElement('div');
        this.chatWindow.className = 'chat-window hidden';
        this.chatWindow.innerHTML = `
            <div class="chat-header">
                <div class="chat-title">
                    <i class="fas fa-comments"></i>
                    <span>Live Chat</span>
                </div>
                <button class="minimize-button">−</button>
            </div>
            <div class="chat-messages"></div>
            <div class="chat-input-container">
                <textarea placeholder="Type your message..." rows="1"></textarea>
                <button class="send-button">
                    <i class="fas fa-paper-plane"></i>
                </button>
            </div>
        `;

        document.body.appendChild(this.chatWindow);
        this.attachChatEventListeners();
    }

    attachChatEventListeners() {
        const minimizeButton = this.chatWindow.querySelector('.minimize-button');
        const sendButton = this.chatWindow.querySelector('.send-button');
        const textarea = this.chatWindow.querySelector('textarea');

        minimizeButton.addEventListener('click', () => this.toggleChat());
        sendButton.addEventListener('click', () => this.sendMessage());
        textarea.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // Auto-resize textarea
        textarea.addEventListener('input', () => {
            textarea.style.height = 'auto';
            textarea.style.height = textarea.scrollHeight + 'px';
        });
    }

    toggleChat() {
        this.isOpen = !this.isOpen;
        this.chatWindow.classList.toggle('hidden');
        this.chatButton.classList.toggle('hidden');
        
        if (this.isOpen && this.messages.length === 0) {
            this.addAutomatedMessage("Hello! How can I help you today?");
        }
    }

    async sendMessage() {
        const textarea = this.chatWindow.querySelector('textarea');
        const message = textarea.value.trim();
        
        if (message) {
            this.addMessage(message, 'user');
            textarea.value = '';
            textarea.style.height = 'auto';
            
            // Show typing indicator
            this.showTypingIndicator();
            
            // Get automated response
            const response = await this.getAutomatedResponse(message);
            
            // Remove typing indicator and show response
            this.hideTypingIndicator();
            this.addMessage(response, 'agent');
            
            // Save to history
            this.saveChatHistory();
        }
    }

    addMessage(text, sender) {
        const messagesContainer = this.chatWindow.querySelector('.chat-messages');
        const messageElement = document.createElement('div');
        messageElement.className = `message ${sender}-message`;
        messageElement.innerHTML = `
            <div class="message-content">
                <div class="message-text">${this.formatMessage(text)}</div>
                <div class="message-time">${this.getCurrentTime()}</div>
            </div>
        `;
        
        messagesContainer.appendChild(messageElement);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
        
        this.messages.push({
            text,
            sender,
            timestamp: new Date().toISOString()
        });
    }

    addAutomatedMessage(text) {
        this.addMessage(text, 'agent');
    }

    showTypingIndicator() {
        const messagesContainer = this.chatWindow.querySelector('.chat-messages');
        const indicator = document.createElement('div');
        indicator.className = 'message agent-message typing-indicator';
        indicator.innerHTML = `
            <div class="message-content">
                <div class="typing-dots">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            </div>
        `;
        messagesContainer.appendChild(indicator);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    hideTypingIndicator() {
        const indicator = this.chatWindow.querySelector('.typing-indicator');
        if (indicator) {
            indicator.remove();
        }
    }

    async getAutomatedResponse(message) {
        // Simple keyword-based responses
        const keywords = {
            'pricing': 'Our pricing plans start at $29/month. Would you like to know more about our different tiers?',
            'website': 'Our website builder allows you to create a professional website in just 3 clicks. Would you like a demo?',
            'help': 'I can help you with website creation, customization, and technical support. What specific assistance do you need?',
            'contact': 'You can reach our support team at support@3clickwebsite.com or call us at (555) 123-4567.',
            'feature': 'We offer various features including mobile responsiveness, SEO optimization, and custom domains. Which feature would you like to know more about?'
        };

        // Check for keywords in the message
        for (const [keyword, response] of Object.entries(keywords)) {
            if (message.toLowerCase().includes(keyword)) {
                return response;
            }
        }

        // Default response
        return "I understand your question. Let me connect you with a human agent who can better assist you. Please hold for a moment...";
    }

    formatMessage(text) {
        // Convert URLs to clickable links
        const urlRegex = /(https?:\/\/[^\s]+)/g;
        return text.replace(urlRegex, url => `<a href="${url}" target="_blank">${url}</a>`);
    }

    getCurrentTime() {
        return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }

    loadChatHistory() {
        const history = localStorage.getItem('chatHistory');
        if (history) {
            this.messages = JSON.parse(history);
            this.messages.forEach(msg => {
                this.addMessage(msg.text, msg.sender);
            });
        }
    }

    saveChatHistory() {
        localStorage.setItem('chatHistory', JSON.stringify(this.messages));
    }
}

// Initialize chat when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new LiveChat();
}); 