# Matic Studio Chat Agent

An AI-powered chat agent designed to assist potential clients and leads for Matic Studio, providing information about services, helping with inquiries, and facilitating meeting scheduling.

## Overview

This chat agent is built using a progressive AI agent framework that can:
1. Answer queries about Matic Studio and its services
2. Provide detailed information about products and solutions
3. Help compose professional inquiry emails
4. Assist in scheduling meetings with Matic Studio's lead architect

## Features

### Stage 0: Basic Information Agent
- Answer general questions about Matic Studio
- Provide company information and background
- Basic service descriptions

### Stage 1: Enhanced Response Agent
- Detailed service explanations with examples
- Professional tone and formatting
- Context-aware responses

### Stage 2: Conversation Memory Agent
- Maintains conversation context
- Remembers previous interactions
- Personalized responses based on conversation history

### Stage 3: Email Composition Agent
- Help compose professional inquiry emails
- Generate meeting request emails
- Format emails with proper business etiquette

### Stage 4: Meeting Scheduling Agent
- Check availability and schedule meetings
- Generate calendar invites
- Coordinate with Matic Studio's lead architect

## Setup

1. Clone this repository
2. Copy `.env.example` to `.env` and add your OpenAI API key
3. Install dependencies:
   ```bash
   uv sync
   ```

## Running the Chat Agent

### Option 1: HTML Chat Interface (Recommended)
```bash
# Install dependencies
uv sync

# Run the chat agent (easiest way)
uv run python start_chat.py
```

Or run the Flask app directly:
```bash
uv run python flask_app.py
```

The chat interface will open in your browser at `http://localhost:5000`

### Option 2: Streamlit Interface
```bash
# Install dependencies
uv sync

# Run the Streamlit app
uv run streamlit run app.py
```

The Streamlit app will open in your browser at `http://localhost:8501`

## Chat Interface Features

The HTML chat interface provides:
- **Modern UI**: Clean, responsive design optimized for mobile and desktop
- **Quick Actions**: Pre-defined buttons for common inquiries
- **Real-time Chat**: Instant responses with typing indicators
- **API Integration**: Connects to the MATIC Studio scheduling agent
- **Fallback Responses**: Works even when API is unavailable

## Usage

### HTML Chat Interface
1. **Quick Actions**: Use the pre-defined buttons for common inquiries
2. **Type Messages**: Ask questions about MATIC Studio's services
3. **Get Responses**: Receive detailed information about automation solutions
4. **Schedule Consultations**: Request to schedule calls with the lead architect

### Streamlit Interface
1. **Select Agent Type**: Choose from different stages in the sidebar
2. **Ask Questions**: Inquire about Matic Studio's services
3. **Request Email Help**: Ask for assistance composing inquiry emails
4. **Schedule Meetings**: Request to schedule a call or meeting

## Testing

Test the chat agent API:
```bash
# Start the Flask app first
uv run python flask_app.py

# In another terminal, run the test
uv run python test_chat.py
```

## Architecture

```
src/
   core/               # Foundation components
      base_agent.py   # Abstract base class
      prompts.py      # Matic Studio specific prompts
      tools.py        # Email and scheduling tools
   agents/             # Progressive agent implementations
      simple_agent.py # Basic information responses
      few_shot_agent.py # Enhanced responses
      memory_agent.py # Conversation memory
      email_agent.py  # Email composition
      scheduling_agent.py # Meeting scheduling
```

## Key Design Principles

1. **Progressive Enhancement**: Each stage builds on previous capabilities
2. **Business Focus**: Tailored specifically for Matic Studio's needs
3. **Professional Tone**: Maintains appropriate business communication
4. **Client-Centric**: Designed to assist potential clients effectively

## Configuration

Update the following in `src/core/prompts.py`:
- Company information
- Service descriptions
- Contact details
- Meeting availability

## Extending the Agent

To add new capabilities:
1. Extend `BaseAgent` or existing agent classes
2. Add new tools to `src/core/tools.py`
3. Update prompts in `src/core/prompts.py`
4. Test with the Streamlit interface