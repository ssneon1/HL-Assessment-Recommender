const form = document.getElementById('chat-form');
const input = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');
const messagesContainer = document.getElementById('chat-messages');
const chatContainer = document.getElementById('chat-container');

// Store conversation history globally
let conversationHistory = [];
let isProcessing = false;

// Format test type full name
const typeMap = {
    'K': 'Knowledge & Skills',
    'P': 'Personality & Behavior',
    'S': 'Simulations',
    'D': 'Development & 360',
    'B': 'Biodata & Situational Judgment',
    'C': 'Competencies',
    'A': 'Ability & Assessment'
};

function scrollToBottom() {
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function createMessageElement(role, text) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${role}`;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.innerText = text;
    
    msgDiv.appendChild(contentDiv);
    return msgDiv;
}

function showLoading() {
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'message assistant loading-msg';
    loadingDiv.id = 'loading-indicator';
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content loading';
    
    for (let i = 0; i < 3; i++) {
        contentDiv.appendChild(document.createElement('span'));
    }
    
    loadingDiv.appendChild(contentDiv);
    messagesContainer.appendChild(loadingDiv);
    scrollToBottom();
}

function removeLoading() {
    const loading = document.getElementById('loading-indicator');
    if (loading) loading.remove();
}

function createRecommendationsGrid(recommendations) {
    const grid = document.createElement('div');
    grid.className = 'recommendations-grid';
    
    const template = document.getElementById('recommendation-template');
    
    recommendations.forEach(rec => {
        const clone = template.content.cloneNode(true);
        
        clone.querySelector('.rec-title').textContent = rec.name;
        clone.querySelector('.rec-link').href = rec.url;
        
        const fullType = typeMap[rec.test_type] || `Type: ${rec.test_type}`;
        clone.querySelector('.rec-type').textContent = fullType;
        
        grid.appendChild(clone);
    });
    
    return grid;
}

async function sendMessage(text) {
    if (isProcessing || !text.trim()) return;
    
    isProcessing = true;
    input.disabled = true;
    sendBtn.disabled = true;
    
    // Add user message to UI
    messagesContainer.appendChild(createMessageElement('user', text));
    scrollToBottom();
    
    // Update history
    conversationHistory.push({ role: 'user', content: text });
    
    showLoading();
    
    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ messages: conversationHistory })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        removeLoading();
        
        // Add assistant message to UI
        const astMsg = createMessageElement('assistant', data.reply);
        messagesContainer.appendChild(astMsg);
        
        // Render recommendations if any
        if (data.recommendations && data.recommendations.length > 0) {
            messagesContainer.appendChild(createRecommendationsGrid(data.recommendations));
        }
        
        scrollToBottom();
        
        // Update history
        conversationHistory.push({ role: 'assistant', content: data.reply });
        
        if (data.end_of_conversation) {
            input.placeholder = "Conversation ended. Refresh to start over.";
            input.disabled = true;
        } else {
            input.disabled = false;
            sendBtn.disabled = false;
            input.focus();
        }
        
    } catch (error) {
        console.error('Error:', error);
        removeLoading();
        messagesContainer.appendChild(createMessageElement('assistant', 'Sorry, I encountered a network error. Please try again later.'));
        scrollToBottom();
        
        // Pop the user message from history so they can retry
        conversationHistory.pop();
        
        input.disabled = false;
        sendBtn.disabled = false;
        input.focus();
    } finally {
        isProcessing = false;
    }
}

form.addEventListener('submit', (e) => {
    e.preventDefault();
    const text = input.value;
    input.value = '';
    sendMessage(text);
});
