const API_BASE_URL = 'http://localhost:8000';

// DOM Elements
const authSection = document.getElementById('auth-section');
const chatSection = document.getElementById('chat-section');
const authTitle = document.getElementById('auth-title');
const authMessage = document.getElementById('auth-message');
const loginForm = document.getElementById('login-form');
const signupForm = document.getElementById('signup-form');
const toggleAuthMode = document.getElementById('toggle-auth-mode');
const userEmailDisplay = document.getElementById('user-email-display');
const messagesDiv = document.getElementById('messages');
const chatForm = document.getElementById('chat-form');
const chatInput = document.getElementById('chat-input');
const newChatButton = document.getElementById('new-chat-button');
const logoutButton = document.getElementById('logout-button');

// State
let accessToken = localStorage.getItem('access_token');
let currentConversationId = null;

// Functions
function showAuth() {
    authSection.style.display = 'block';
    chatSection.style.display = 'none';
}

function showChat(email) {
    authSection.style.display = 'none';
    chatSection.style.display = 'block';
    userEmailDisplay.textContent = email;
    messagesDiv.innerHTML = '';
    currentConversationId = null;
    localStorage.removeItem('current_conversation_id');
    chatInput.focus();
}

function setAuthMessage(message, isError = true) {
    authMessage.textContent = message;
    authMessage.style.color = isError ? 'red' : 'green';
}

function clearAuthMessage() {
    authMessage.textContent = '';
}

function appendMessage(sender, content) {
    const msgDiv = document.createElement('div');
    msgDiv.classList.add('message', sender);
    msgDiv.textContent = content;
    messagesDiv.appendChild(msgDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

// Event Listeners
toggleAuthMode.addEventListener('click', () => {
    clearAuthMessage();
    if (loginForm.style.display === 'none') {
        loginForm.style.display = 'flex';
        signupForm.style.display = 'none';
        authTitle.textContent = 'Login';
        toggleAuthMode.textContent = "Don't have an account? Sign Up";
    } else {
        loginForm.style.display = 'none';
        signupForm.style.display = 'flex';
        authTitle.textContent = 'Sign Up';
        toggleAuthMode.textContent = "Already have an account? Login";
    }
});

loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    clearAuthMessage();
    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;

    try {
        const response = await fetch(`${API_BASE_URL}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });
        const data = await response.json();

        if (response.ok) {
            accessToken = data.access_token;
            localStorage.setItem('access_token', accessToken);
            localStorage.setItem('user_email_for_display', email);
            setAuthMessage('Login successful!', false);
            setTimeout(() => showChat(email), 500);
        } else {
            setAuthMessage(data.detail || 'Login failed.');
        }
    } catch (error) {
        console.error('Login error:', error);
        setAuthMessage('Network error or server unavailable.');
    }
});

signupForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    clearAuthMessage();
    const email = document.getElementById('signup-email').value;
    const username = document.getElementById('signup-username').value;
    const password = document.getElementById('signup-password').value;
    const confirm_password = document.getElementById('signup-confirm-password').value;

    if (password !== confirm_password) {
        setAuthMessage("Passwords do not match.");
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/auth/signup`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, username, password, confirm_password })
        });
        const data = await response.json();

        if (response.ok) {
            setAuthMessage(data.msg || 'Signup successful! Check your email to verify.', false);
            toggleAuthMode.click();
        } else {
            setAuthMessage(data.detail || 'Signup failed.');
        }
    } catch (error) {
        console.error('Signup error:', error);
        setAuthMessage('Network error or server unavailable.');
    }
});

logoutButton.addEventListener('click', () => {
    accessToken = null;
    localStorage.removeItem('access_token');
    localStorage.removeItem('current_conversation_id');
    localStorage.removeItem('user_email_for_display');
    currentConversationId = null;
    showAuth();
    setAuthMessage('You have been logged out.', false);
});

chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const query = chatInput.value.trim();
    if (!query) return;

    appendMessage('user', query);
    chatInput.value = '';

    try {
        const requestBody = { query: query };
        if (currentConversationId) {
            requestBody.conversation_id = currentConversationId;
        }

        const response = await fetch(`${API_BASE_URL}/chat/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${accessToken}`
            },
            body: JSON.stringify(requestBody)
        });

        if (!response.ok) {
            const errorData = await response.json();
            appendMessage('assistant', `Error: ${errorData.detail || 'Something went wrong.'}`);
            return;
        }

        const conversationIdHeader = response.headers.get("X-Conversation-ID");
        if (conversationIdHeader) {
            currentConversationId = conversationIdHeader;
            localStorage.setItem('current_conversation_id', currentConversationId);
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder('utf-8');
        let result = '';
        appendMessage('assistant', '');

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            const chunk = decoder.decode(value, { stream: true });
            result += chunk;
            const lastMsg = document.querySelector('.message.assistant:last-child');
            if (lastMsg) lastMsg.textContent = result;
        }

    } catch (error) {
        console.error('Chat error:', error);
        appendMessage('assistant', 'Network error or unable to connect to the LLM.');
    }
});

newChatButton.addEventListener('click', () => {
    showChat(userEmailDisplay.textContent);
    setAuthMessage('New chat started.', false);
    setTimeout(() => clearAuthMessage(), 3000);
});

// Initialize
function init() {
    if (accessToken) {
        const storedEmail = localStorage.getItem('user_email_for_display');
        if (storedEmail) {
            showChat(storedEmail);
            currentConversationId = localStorage.getItem('current_conversation_id');
        } else {
            showAuth();
            setAuthMessage('Please log in.', true);
        }
    } else {
        showAuth();
    }
}

init();