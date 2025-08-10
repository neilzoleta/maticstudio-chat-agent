#!/usr/bin/env python3
"""
MongoDB integration for MATIC Studio Chat Agent
Handles conversation storage and lead management
"""

import os
from datetime import datetime
from typing import Dict, List, Optional
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from dotenv import load_dotenv

load_dotenv()

class DatabaseManager:
    def __init__(self):
        self.mongodb_uri = os.getenv("MONGODB_URI")
        self.client = None
        self.db = None
        self.conversations = None
        self.leads = None
        self.initialize_database()
    
    def initialize_database(self):
        """Initialize MongoDB connection and collections"""
        try:
            if not self.mongodb_uri:
                print("⚠️  MONGODB_URI not found. Database features will be disabled.")
                return
            
            self.client = MongoClient(self.mongodb_uri)
            # Test the connection
            self.client.admin.command('ping')
            
            self.db = self.client.maticstudio_chat
            self.conversations = self.db.conversations
            self.leads = self.db.leads
            
            # Create indexes for better performance
            self.conversations.create_index("session_id")
            self.conversations.create_index("created_at")
            self.leads.create_index("email")
            self.leads.create_index("company")
            self.leads.create_index("created_at")
            
            print("✅ MongoDB connected successfully")
            
        except ConnectionFailure as e:
            print(f"❌ MongoDB connection failed: {e}")
            self.client = None
        except Exception as e:
            print(f"❌ Database initialization error: {e}")
            self.client = None
    
    def save_conversation(self, session_id: str, messages: List[Dict], metadata: Dict = None):
        """Save conversation to MongoDB"""
        if not self.conversations:
            return False
        
        try:
            conversation_data = {
                "session_id": session_id,
                "messages": messages,
                "metadata": metadata or {},
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            # Update existing conversation or insert new one
            result = self.conversations.update_one(
                {"session_id": session_id},
                {"$set": conversation_data},
                upsert=True
            )
            
            return True
            
        except Exception as e:
            print(f"❌ Error saving conversation: {e}")
            return False
    
    def get_conversation(self, session_id: str) -> Optional[Dict]:
        """Retrieve conversation from MongoDB"""
        if not self.conversations:
            return None
        
        try:
            conversation = self.conversations.find_one({"session_id": session_id})
            return conversation
            
        except Exception as e:
            print(f"❌ Error retrieving conversation: {e}")
            return None
    
    def save_lead(self, lead_data: Dict) -> bool:
        """Save lead information to MongoDB"""
        if not self.leads:
            return False
        
        try:
            lead_data.update({
                "created_at": datetime.utcnow(),
                "status": "new",
                "source": "chat_agent"
            })
            
            # Check if lead already exists
            existing_lead = self.leads.find_one({
                "$or": [
                    {"email": lead_data.get("email")},
                    {"phone": lead_data.get("phone")}
                ]
            })
            
            if existing_lead:
                # Update existing lead
                self.leads.update_one(
                    {"_id": existing_lead["_id"]},
                    {
                        "$set": {
                            "updated_at": datetime.utcnow(),
                            "last_contact": datetime.utcnow(),
                            "conversation_count": existing_lead.get("conversation_count", 0) + 1
                        }
                    }
                )
            else:
                # Insert new lead
                lead_data["conversation_count"] = 1
                self.leads.insert_one(lead_data)
            
            return True
            
        except Exception as e:
            print(f"❌ Error saving lead: {e}")
            return False
    
    def get_leads(self, limit: int = 50) -> List[Dict]:
        """Retrieve leads from MongoDB"""
        if not self.leads:
            return []
        
        try:
            leads = list(self.leads.find().sort("created_at", -1).limit(limit))
            return leads
            
        except Exception as e:
            print(f"❌ Error retrieving leads: {e}")
            return []
    
    def update_lead_status(self, email: str, status: str) -> bool:
        """Update lead status"""
        if not self.leads:
            return False
        
        try:
            result = self.leads.update_one(
                {"email": email},
                {
                    "$set": {
                        "status": status,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            return result.modified_count > 0
            
        except Exception as e:
            print(f"❌ Error updating lead status: {e}")
            return False
    
    def get_analytics(self) -> Dict:
        """Get basic analytics from the database"""
        if not self.leads or not self.conversations:
            return {}
        
        try:
            total_leads = self.leads.count_documents({})
            new_leads = self.leads.count_documents({"status": "new"})
            total_conversations = self.conversations.count_documents({})
            
            # Get leads by company
            company_stats = list(self.leads.aggregate([
                {"$group": {"_id": "$company", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}},
                {"$limit": 10}
            ]))
            
            return {
                "total_leads": total_leads,
                "new_leads": new_leads,
                "total_conversations": total_conversations,
                "top_companies": company_stats
            }
            
        except Exception as e:
            print(f"❌ Error getting analytics: {e}")
            return {}

# Global database instance
db_manager = DatabaseManager()
