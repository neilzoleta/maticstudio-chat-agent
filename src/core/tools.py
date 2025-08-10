from typing import Dict, List, Callable, Any
import json
from datetime import datetime, timedelta
import random
import os
import requests
from src.core.prompts import MATIC_STUDIO_INFO


class Tool:
    def __init__(self, name: str, description: str, function: Callable, parameters: Dict[str, Any]):
        self.name = name
        self.description = description
        self.function = function
        self.parameters = parameters
    
    def to_openai_function(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters
        }
    
    def execute(self, **kwargs) -> str:
        try:
            result = self.function(**kwargs)
            return json.dumps(result) if not isinstance(result, str) else result
        except Exception as e:
            return f"Error executing {self.name}: {str(e)}"


def _create_calendly_scheduling_link(
    event_type_url: str,
    api_token: str,
    invitee_name: str,
    invitee_email: str
) -> Dict[str, Any]:
    """Create a Calendly scheduling link (one-off) with prefilled name/email.
    Requires: CALENDLY_EVENT_TYPE_URL, CALENDLY_API_TOKEN
    Docs: POST https://api.calendly.com/scheduling_links
    """
    try:
        headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json"
        }
        payload = {
            "owner": event_type_url,
            "owner_type": "EventType",
            "max_event_count": 1,
            "prefill": {
                "name": invitee_name,
                "email": invitee_email
            }
        }
        resp = requests.post("https://api.calendly.com/scheduling_links", headers=headers, json=payload, timeout=15)
        if resp.status_code >= 400:
            return {"error": f"Calendly API error {resp.status_code}: {resp.text}"}
        data = resp.json()
        resource = data.get("resource", {})
        return {
            "scheduling_url": resource.get("booking_url") or resource.get("scheduling_url"),
            "raw": data
        }
    except Exception as e:
        return {"error": f"Calendly request failed: {str(e)}"}


# Email composition tool
def compose_inquiry_email(
    client_name: str,
    company_name: str,
    project_type: str,
    project_description: str,
    timeline: str,
    budget_range: str,
    contact_email: str,
    contact_phone: str
) -> Dict[str, Any]:
    """Compose a professional inquiry email for Matic Studio"""
    
    subject = f"Inquiry - {project_type} Services"
    
    email_body = f"""Dear {MATIC_STUDIO_INFO['lead_architect']},

I hope this email finds you well. I'm reaching out to inquire about Matic Studio's {project_type.lower()} services for our company.

**About Our Project:**
{project_description}

**Project Details:**
- Project Type: {project_type}
- Timeline: {timeline}
- Budget Range: {budget_range}

**Why Matic Studio:**
I was impressed by your portfolio and approach to digital product development, particularly your expertise in {project_type.lower()}.

**Next Steps:**
I would appreciate the opportunity to discuss our project in detail. Would you be available for a 30-minute consultation call next week? I'm flexible with timing and can work around your schedule.

**Contact Information:**
- Name: {client_name}
- Company: {company_name}
- Email: {contact_email}
- Phone: {contact_phone}

Thank you for your time and consideration. I look forward to hearing from you.

Best regards,
{client_name}
{company_name}

---
*This email will be sent to: {MATIC_STUDIO_INFO['email']}*"""
    
    return {
        "subject": subject,
        "body": email_body,
        "to": MATIC_STUDIO_INFO['email'],
        "from": contact_email,
        "status": "ready_to_send"
    }


# Meeting scheduling tool
def schedule_consultation_meeting(
    client_name: str,
    company_name: str,
    preferred_date: str,
    preferred_time: str,
    contact_email: str,
    project_type: str = "",
    meeting_duration: str = "30 minutes",
    contact_phone: str = ""
) -> Dict[str, Any]:
    """Schedule a consultation meeting with Matic Studio's lead architect
    Minimum required: client_name, company_name, preferred_date, preferred_time, contact_email
    Optional: project_type, meeting_duration, contact_phone
    """
    
    # Generate available time slots (fallback mock implementation)
    available_slots = [
        "Monday 10:00 AM EST",
        "Monday 2:00 PM EST", 
        "Tuesday 11:00 AM EST",
        "Tuesday 3:00 PM EST",
        "Wednesday 10:00 AM EST",
        "Wednesday 2:00 PM EST",
        "Thursday 11:00 AM EST",
        "Thursday 3:00 PM EST",
        "Friday 10:00 AM EST",
        "Friday 2:00 PM EST"
    ]
    
    # Use provided date/time if available; otherwise pick a slot
    if preferred_date and preferred_time:
        selected_slot = f"{preferred_date} {preferred_time}"
    else:
        selected_slot = random.choice(available_slots)
    
    meeting_details = {
        "meeting_type": "Initial Consultation",
        "duration": meeting_duration or "30 minutes",
        "date_time": selected_slot,
        "format": "Video Call (Zoom/Teams)",
        "attendees": [
            f"{client_name} ({company_name})",
            f"{MATIC_STUDIO_INFO['lead_architect']} (Matic Studio)"
        ],
        "agenda": [
            "Project/Process overview and goals",
            "Service capabilities and approach",
            "Timeline and budget considerations",
            "Next steps and proposal process"
        ],
        "calendar_invite": {
            "subject": f"Consultation Meeting{f' - {project_type} Project' if project_type else ''}",
            "description": f"""Meeting with {client_name} from {company_name}{f' to discuss {project_type} project' if project_type else ''}.

Agenda:
- Project/process overview and goals
- Service capabilities and approach  
- Timeline and budget considerations
- Next steps

Duration: {meeting_duration or '30 minutes'}
Format: Video Call (Zoom/Teams)

Contact: {contact_email}{f' | {contact_phone}' if contact_phone else ''}""",
            "status": "invite_prepared"
        }
    }

    # Try Calendly integration if configured
    calendly_event_type_url = os.getenv("CALENDLY_EVENT_TYPE_URL", "").strip()
    calendly_api_token = os.getenv("CALENDLY_API_TOKEN", "").strip()
    if calendly_event_type_url and calendly_api_token:
        calendly_result = _create_calendly_scheduling_link(
            calendly_event_type_url,
            calendly_api_token,
            invitee_name=client_name,
            invitee_email=contact_email
        )
        meeting_details["calendly"] = calendly_result
        # If link available, elevate status
        if isinstance(calendly_result, dict) and calendly_result.get("scheduling_url"):
            meeting_details["calendar_invite"]["status"] = "calendly_link_created"
            meeting_details["calendar_invite"]["scheduling_url"] = calendly_result["scheduling_url"]
    
    return meeting_details


# Service information tool
def get_service_details(service_name: str) -> Dict[str, Any]:
    """Get detailed information about Matic Studio services"""
    
    services = {
        "web_development": {
            "name": "Web Development",
            "description": "Custom web applications, e-commerce platforms, and responsive websites",
            "technologies": ["React", "Vue.js", "Node.js", "Python", "PHP", "WordPress"],
            "process": [
                "Requirements gathering and planning",
                "UI/UX design and wireframing", 
                "Frontend and backend development",
                "Testing and quality assurance",
                "Deployment and launch",
                "Ongoing maintenance and support"
            ],
            "timeline": "4-12 weeks depending on complexity",
            "starting_price": "$15,000"
        },
        "mobile_development": {
            "name": "Mobile Development", 
            "description": "Native and cross-platform mobile applications for iOS and Android",
            "technologies": ["React Native", "Flutter", "Swift", "Kotlin", "Xamarin"],
            "process": [
                "App concept and requirements",
                "UI/UX design and prototyping",
                "Development and testing",
                "App store submission",
                "Launch and maintenance"
            ],
            "timeline": "8-16 weeks depending on complexity",
            "starting_price": "$25,000"
        },
        "ui_ux_design": {
            "name": "UI/UX Design",
            "description": "User-centered design solutions with focus on usability and aesthetics",
            "deliverables": ["Wireframes", "Prototypes", "Design systems", "User research", "Usability testing"],
            "process": [
                "User research and analysis",
                "Information architecture",
                "Wireframing and prototyping",
                "Visual design and branding",
                "Usability testing and iteration"
            ],
            "timeline": "3-8 weeks depending on scope",
            "starting_price": "$8,000"
        },
        "consulting": {
            "name": "Digital Strategy Consulting",
            "description": "Strategic guidance for digital transformation and product development",
            "services": ["Product strategy", "Technology consulting", "Digital transformation", "Market analysis"],
            "process": [
                "Current state assessment",
                "Strategy development",
                "Technology recommendations",
                "Implementation roadmap",
                "Ongoing guidance and support"
            ],
            "timeline": "2-6 weeks depending on scope",
            "starting_price": "$5,000"
        }
    }
    
    return services.get(service_name.lower(), {
        "error": f"Service '{service_name}' not found. Available services: {list(services.keys())}"
    })


# Tool definitions
MATIC_STUDIO_TOOLS = [
    Tool(
        name="compose_inquiry_email",
        description="Compose a professional inquiry email to Matic Studio",
        function=compose_inquiry_email,
        parameters={
            "type": "object",
            "properties": {
                "client_name": {"type": "string", "description": "Client's full name"},
                "company_name": {"type": "string", "description": "Client's company name"},
                "project_type": {"type": "string", "description": "Type of project (web development, mobile development, UI/UX design, consulting)"},
                "project_description": {"type": "string", "description": "Brief description of the project"},
                "timeline": {"type": "string", "description": "Expected project timeline"},
                "budget_range": {"type": "string", "description": "Budget range for the project"},
                "contact_email": {"type": "string", "description": "Client's email address"},
                "contact_phone": {"type": "string", "description": "Client's phone number"}
            },
            "required": ["client_name", "company_name", "project_type", "project_description", "contact_email"]
        }
    ),
    Tool(
        name="schedule_consultation_meeting",
        description="Schedule a consultation meeting with Matic Studio's lead architect",
        function=schedule_consultation_meeting,
        parameters={
            "type": "object",
            "properties": {
                "client_name": {"type": "string", "description": "Client's full name"},
                "company_name": {"type": "string", "description": "Client's company name"},
                "preferred_date": {"type": "string", "description": "Preferred meeting date"},
                "preferred_time": {"type": "string", "description": "Preferred meeting time"},
                "contact_email": {"type": "string", "description": "Client's email address"},
                "project_type": {"type": "string", "description": "Type of project to discuss (optional)"},
                "meeting_duration": {"type": "string", "description": "Preferred meeting duration (e.g., 30 minutes) (optional)"},
                "contact_phone": {"type": "string", "description": "Client's phone number (optional)"}
            },
            "required": ["client_name", "company_name", "preferred_date", "preferred_time", "contact_email"]
        }
    ),
    Tool(
        name="get_service_details",
        description="Get detailed information about Matic Studio services",
        function=get_service_details,
        parameters={
            "type": "object",
            "properties": {
                "service_name": {"type": "string", "description": "Name of the service (web_development, mobile_development, ui_ux_design, consulting)"}
            },
            "required": ["service_name"]
        }
    )
]