#!/usr/bin/env python3
"""
Startup script for MATIC Studio Chat Agent
"""

import os
import sys
import subprocess
import time
import webbrowser
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import flask
        import openai
        import dotenv
        print("✅ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please run: uv sync")
        return False

def check_env_file():
    """Check if .env file exists and has OpenAI API key"""
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env file not found")
        print("Please create a .env file with your OpenAI API key:")
        print("OPENAI_API_KEY=your_api_key_here")
        return False
    
    # Load and check the .env file
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OpenAI API key not found in .env file")
        print("Please add: OPENAI_API_KEY=your_api_key_here")
        return False
    
    print("✅ OpenAI API key found")
    return True

def start_flask_app():
    """Start the Flask app"""
    print("🚀 Starting MATIC Studio Chat Agent...")
    
    try:
        # Start the Flask app
        process = subprocess.Popen([
            sys.executable, "flask_app.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Wait a moment for the app to start
        time.sleep(3)
        
        # Check if the process is still running
        if process.poll() is None:
            print("✅ Flask app started successfully!")
            print("📱 Chat interface: http://localhost:5000")
            print("🔧 API endpoint: http://localhost:5000/api/chat")
            print("💚 Health check: http://localhost:5000/health")
            print("\n🌐 Opening chat interface in your browser...")
            
            # Open the chat interface in the default browser
            webbrowser.open("http://localhost:5001")
            
            print("\n🔄 Chat agent is running. Press Ctrl+C to stop.")
            
            try:
                # Keep the script running
                process.wait()
            except KeyboardInterrupt:
                print("\n🛑 Stopping chat agent...")
                process.terminate()
                process.wait()
                print("✅ Chat agent stopped")
        else:
            stdout, stderr = process.communicate()
            print(f"❌ Failed to start Flask app:")
            print(f"STDOUT: {stdout}")
            print(f"STDERR: {stderr}")
            
    except Exception as e:
        print(f"❌ Error starting Flask app: {e}")

def main():
    """Main startup function"""
    print("🤖 MATIC Studio Chat Agent")
    print("=" * 40)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check environment
    if not check_env_file():
        sys.exit(1)
    
    print("\n" + "=" * 40)
    
    # Start the Flask app
    start_flask_app()

if __name__ == "__main__":
    main() 