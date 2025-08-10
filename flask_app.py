#!/usr/bin/env python3
"""
Flask app for Matic Studio Chat Agent
Serves the HTML chat interface and provides API endpoints
Production-ready for Render.com deployment
"""

import os
import uuid
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, request, jsonify, send_from_directory, session
from flask_cors import CORS
from src.agents.scheduling_agent import SchedulingAgent
from database import db_manager

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "maticstudio-secret-key-2024")

# Enable CORS for website integration
CORS(app, origins=[
    "https://maticstudio.net",
    "https://www.maticstudio.net",
    "http://localhost:3000",
    "http://localhost:5000"
])

# Initialize the scheduling agent
default_model = os.getenv("DEFAULT_MODEL", "gpt-4o-mini")
# Use temperature=1 for models that don't support custom temperature
temperature = 1.0 if default_model == "gpt-5" else 0.7
scheduling_agent = SchedulingAgent(model=default_model, temperature=temperature)

@app.route('/')
def serve_chat():
    """Serve the chat HTML file"""
    return send_from_directory('.', 'chatMATICStudio.html')

@app.route('/api/chat', methods=['POST'])
def chat_api():
    """API endpoint for chat functionality with session management and database storage"""
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        conversation_history = data.get('conversation_history', [])
        session_id = data.get('session_id')
        
        if not user_message:
            return jsonify({'error': 'No message provided'}), 400
        
        # Generate session ID if not provided
        if not session_id:
            session_id = str(uuid.uuid4())
        
        # Process the message using the scheduling agent
        response = scheduling_agent.process(user_message)
        
        # Update conversation history
        updated_history = conversation_history + [
            {"role": "user", "content": user_message},
            {"role": "assistant", "content": response}
        ]
        
        # Save conversation to database
        metadata = {
            "user_agent": request.headers.get('User-Agent'),
            "ip_address": request.remote_addr,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        db_manager.save_conversation(session_id, updated_history, metadata)
        
        # Check if this is a lead generation message (contains contact info)
        if any(keyword in user_message.lower() for keyword in ['email', 'phone', 'company', 'name']):
            # Extract potential lead information
            lead_data = extract_lead_info(user_message, updated_history)
            if lead_data:
                db_manager.save_lead(lead_data)
        
        return jsonify({
            'response': response,
            'status': 'success',
            'session_id': session_id
        })
        
    except Exception as e:
        print(f"Error in chat API: {str(e)}")
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500

def extract_lead_info(message: str, conversation_history: list) -> dict:
    """Extract lead information from conversation"""
    lead_data = {}
    
    # Simple extraction logic - can be enhanced with NLP
    message_lower = message.lower()
    
    # Extract email
    import re
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, message)
    if emails:
        lead_data['email'] = emails[0]
    
    # Extract phone
    phone_pattern = r'[\+]?[1-9][\d]{0,15}'
    phones = re.findall(phone_pattern, message)
    if phones and len(phones[0]) >= 10:
        lead_data['phone'] = phones[0]
    
    # Extract company name (simple heuristic)
    company_keywords = ['company', 'corp', 'inc', 'ltd', 'llc', 'enterprises']
    words = message.split()
    for i, word in enumerate(words):
        if any(keyword in word.lower() for keyword in company_keywords):
            if i > 0:
                lead_data['company'] = words[i-1] + ' ' + word
            break
    
    # Extract name (simple heuristic)
    name_keywords = ['name', 'i am', 'my name is', 'call me']
    for keyword in name_keywords:
        if keyword in message_lower:
            start_idx = message_lower.find(keyword) + len(keyword)
            name_part = message[start_idx:].strip().split()[0:2]
            if name_part:
                lead_data['name'] = ' '.join(name_part)
            break
    
    return lead_data if lead_data else None

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'MATIC Studio Chat Agent',
        'database': 'connected' if db_manager.client else 'disconnected'
    })

@app.route('/api/admin/leads', methods=['GET'])
def get_leads():
    """Admin endpoint to retrieve leads (protected)"""
    # Simple API key protection - you can enhance this
    api_key = request.headers.get('X-API-Key')
    if api_key != os.getenv("ADMIN_API_KEY"):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        limit = int(request.args.get('limit', 50))
        leads = db_manager.get_leads(limit)
        
        # Remove sensitive fields for security
        for lead in leads:
            lead.pop('_id', None)
        
        return jsonify({
            'leads': leads,
            'count': len(leads)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/analytics', methods=['GET'])
def get_analytics():
    """Admin endpoint to retrieve analytics (protected)"""
    api_key = request.headers.get('X-API-Key')
    if api_key != os.getenv("ADMIN_API_KEY"):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        analytics = db_manager.get_analytics()
        return jsonify(analytics)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/lead/<email>/status', methods=['PUT'])
def update_lead_status(email):
    """Admin endpoint to update lead status (protected)"""
    api_key = request.headers.get('X-API-Key')
    if api_key != os.getenv("ADMIN_API_KEY"):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        data = request.get_json()
        status = data.get('status')
        
        if not status:
            return jsonify({'error': 'Status is required'}), 400
        
        success = db_manager.update_lead_status(email, status)
        
        if success:
            return jsonify({'message': 'Lead status updated successfully'})
        else:
            return jsonify({'error': 'Lead not found'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OpenAI API key not found. Please add your API key to the .env file.")
        exit(1)
    
    print("🚀 Starting MATIC Studio Chat Agent...")
    print("📱 Chat interface available at: http://localhost:5001")
    print("🔧 API endpoint available at: http://localhost:5001/api/chat")
    print("💚 Health check available at: http://localhost:5001/health")
    
    app.run(host='0.0.0.0', port=5001, debug=True) 