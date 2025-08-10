#!/usr/bin/env python3
"""
Streamlit app for Matic Studio Chat Agent with Flask API support
"""

import streamlit as st
import os
from dotenv import load_dotenv
from src.agents.scheduling_agent import SchedulingAgent
from flask import Flask, request, jsonify, send_from_directory
import threading
import time

# Load environment variables
load_dotenv()

# Initialize Flask app for API
flask_app = Flask(__name__)

# Initialize the scheduling agent
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gpt-5")
scheduling_agent = SchedulingAgent(model=DEFAULT_MODEL, temperature=0.7)

@flask_app.route('/')
def serve_chat():
    """Serve the chat HTML file"""
    return send_from_directory('.', 'chatMATICStudio.html')

@flask_app.route('/api/chat', methods=['POST'])
def chat_api():
    """API endpoint for chat functionality"""
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        conversation_history = data.get('conversation_history', [])
        
        if not user_message:
            return jsonify({'error': 'No message provided'}), 400
        
        # Process the message using the scheduling agent
        response = scheduling_agent.process(user_message)
        
        return jsonify({
            'response': response,
            'status': 'success'
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500

def run_flask():
    """Run Flask app in a separate thread"""
    flask_app.run(host='0.0.0.0', port=5000, debug=False)

# Start Flask server in background thread
flask_thread = threading.Thread(target=run_flask, daemon=True)
flask_thread.start()

# Give Flask time to start
time.sleep(2)

# Page configuration
st.set_page_config(
    page_title="MATIC Studio Chat Agent",
    page_icon="🤖",
    layout="centered"
)

# Custom CSS for modern look
st.markdown("""
<style>
    /* Hide Streamlit defaults */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Main background */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
    }
    
    /* Chat container */
    .chat-container {
        background: white;
        border-radius: 20px;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
        margin: 20px;
        overflow: hidden;
    }
    
    /* Header */
    .chat-header {
        background: #f8fafc;
        padding: 20px;
        border-bottom: 1px solid #e2e8f0;
        text-align: center;
    }
    
    .chat-header h1 {
        color: #1e293b;
        font-size: 24px;
        font-weight: 600;
        margin: 0;
    }
    
    /* Messages area */
    .messages-area {
        padding: 20px;
        max-height: 500px;
        overflow-y: auto;
    }
    
    /* Message styling */
    .message {
        margin-bottom: 16px;
        display: flex;
        align-items: flex-start;
        gap: 12px;
    }
    
    .user-message {
        justify-content: flex-end;
    }
    
    .bot-message {
        justify-content: flex-start;
    }
    
    .avatar {
        width: 32px;
        height: 32px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 14px;
        font-weight: 600;
    }
    
    .user-avatar {
        background: #667eea;
        color: white;
    }
    
    .bot-avatar {
        background: #f1f5f9;
        color: #64748b;
    }
    
    .message-bubble {
        max-width: 70%;
        padding: 12px 16px;
        border-radius: 18px;
        font-size: 14px;
        line-height: 1.5;
    }
    
    .user-bubble {
        background: #667eea;
        color: white;
        border-bottom-right-radius: 4px;
    }
    
    .bot-bubble {
        background: #f1f5f9;
        color: #1e293b;
        border-bottom-left-radius: 4px;
    }
    
    /* Quick questions */
    .quick-questions {
        padding: 20px;
        background: #f8fafc;
        border-top: 1px solid #e2e8f0;
    }
    
    .quick-questions h3 {
        color: #64748b;
        font-size: 14px;
        font-weight: 500;
        margin-bottom: 12px;
    }
    
    /* Question button styling */
    .stButton > button {
        width: 100%;
        text-align: left;
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 16px;
        padding: 16px;
        margin-bottom: 8px;
        transition: all 0.2s;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    
    .stButton > button:hover {
        background: #f3f4f6;
        border-color: #d1d5db;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transform: translateY(-1px);
    }
    
    .stButton > button::before {
        content: "📞";
        margin-right: 12px;
        font-size: 20px;
    }
    
    .stButton > button::after {
        content: "→";
        color: #9ca3af;
        font-size: 16px;
        transition: color 0.2s;
    }
    
    .stButton > button:hover::after {
        color: #667eea;
    }
    
    /* Second button styling */
    .stButton:nth-child(2) > button::before {
        content: "🏢";
    }
    
    /* Chat input */
    .stChatInput {
        background: white;
        border-top: 1px solid #e2e8f0;
        padding: 20px;
    }
    
    .stChatInput input {
        border: 1px solid #d1d5db;
        border-radius: 24px;
        padding: 12px 16px;
        font-size: 14px;
        outline: none;
        transition: all 0.2s;
    }
    
    .stChatInput input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Controls */
    .controls {
        position: absolute;
        top: 20px;
        right: 20px;
        display: flex;
        gap: 8px;
        z-index: 1000;
    }
    
    .control-btn {
        background: rgba(255, 255, 255, 0.9);
        border: none;
        border-radius: 8px;
        padding: 8px 12px;
        font-size: 16px;
        cursor: pointer;
        transition: all 0.2s;
        backdrop-filter: blur(10px);
    }
    
    .control-btn:hover {
        background: rgba(255, 255, 255, 1);
        transform: translateY(-1px);
    }
    
    /* Model selector */
    .model-selector {
        position: absolute;
        top: 20px;
        left: 20px;
        z-index: 1000;
    }
    
    .model-selector select {
        background: rgba(255, 255, 255, 0.9);
        border: none;
        border-radius: 8px;
        padding: 8px 12px;
        font-size: 12px;
        backdrop-filter: blur(10px);
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "agent" not in st.session_state:
        st.session_state.agent = SchedulingAgent(model=DEFAULT_MODEL, temperature=0.7)
    
    if "selected_model" not in st.session_state:
        st.session_state.selected_model = DEFAULT_MODEL

def main():
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        st.error("❌ OpenAI API key not found. Please add your API key to the .env file.")
        st.stop()
    
    # Initialize session state
    initialize_session_state()
    
    # Controls overlay
    st.markdown("""
    <div class="controls">
        <button class="control-btn" onclick="window.location.reload()" title="Reset All">🗑️</button>
        <button class="control-btn" onclick="clearChat()" title="Clear Chat">🧹</button>
    </div>
    """, unsafe_allow_html=True)
    
    # Model selector
    with st.container():
        st.markdown(f"""
        <div class="model-selector">
            <select onchange="changeModel(this.value)">
                <option value="{DEFAULT_MODEL}" selected>{DEFAULT_MODEL}</option>
                <option value="gpt-4o">GPT-4o</option>
                <option value="gpt-4o-mini">GPT-4o Mini</option>
                <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
            </select>
        </div>
        """, unsafe_allow_html=True)
    
    # Main chat container
    st.markdown("""
    <div class="chat-container">
        <div class="chat-header">
            <h1>🤖 MATIC Studio Chat Agent</h1>
        </div>
    """, unsafe_allow_html=True)
    
    # Messages area
    st.markdown('<div class="messages-area">', unsafe_allow_html=True)
    
    # Display messages
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f"""
            <div class="message user-message">
                <div class="message-bubble user-bubble">
                    {message["content"]}
                </div>
                <div class="avatar user-avatar">U</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="message bot-message">
                <div class="avatar bot-avatar">🤖</div>
                <div class="message-bubble bot-bubble">
                    {message["content"]}
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Quick questions (only show if no messages) - Using Streamlit buttons with custom styling
    if len(st.session_state.messages) == 0:
        st.markdown("""
        <div class="quick-questions">
            <h3>Quick questions:</h3>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Setup a consultation call", key="consultation_btn"):
            st.session_state.messages.append({
                "role": "user", 
                "content": "I'd like to schedule a consultation call to discuss automation solutions for our business processes."
            })
            st.rerun()
        
        if st.button("Learn about MATIC Studio services", key="services_btn"):
            st.session_state.messages.append({
                "role": "user", 
                "content": "Tell me about MATIC Studio and what automation services you offer."
            })
            st.rerun()
    
    # Chat input
    if prompt := st.chat_input("Type your message..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.rerun()
    
    # Process messages and get responses
    if len(st.session_state.messages) > 0 and st.session_state.messages[-1]["role"] == "user":
        try:
            with st.spinner("🤖 Thinking..."):
                response = st.session_state.agent.process(st.session_state.messages[-1]["content"])
            
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()
            
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
    
    # Close chat container
    st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()