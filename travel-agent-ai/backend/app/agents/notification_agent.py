from typing import Dict, Any, List, Optional
from langchain.agents import Tool, AgentType, initialize_agent
from langchain.memory import ConversationBufferMemory
from langchain.chat_models import ChatOpenAI
import json
from datetime import datetime

from .base import BaseAgent, AgentInput, AgentOutput
from ..core.config import settings

class NotificationAgent(BaseAgent):
    """Agent responsible for handling user notifications and alerts."""
    
    def __init__(self):
        super().__init__()
        self.name = "NotificationAgent"
        self.description = "Manages user notifications and alerts"
        self.llm = ChatOpenAI(
            temperature=0.3,  # Slightly creative for notification content
            model_name="gpt-4",
            openai_api_key=settings.OPENAI_API_KEY
        )
        self._setup_tools()
        # In-memory storage for notifications (replace with database in production)
        self.notifications = {}
    
    def _setup_tools(self) -> None:
        """Set up tools for the notification agent."""
        self.add_tool(
            Tool(
                name="send_notification",
                func=self._send_notification,
                description=(
                    "Send a notification to a user. "
                    "Input should be a JSON string with 'user_id', 'title', 'message', "
                    "'notification_type' (email/sms/push), and optional 'metadata'."
                )
            )
        )
        
        self.add_tool(
            Tool(
                name="get_user_notifications",
                func=self._get_user_notifications,
                description=(
                    "Get notifications for a specific user. "
                    "Input should be a JSON string with 'user_id' and optional 'limit' and 'unread_only'."
                )
            )
        )
        
        self.add_tool(
            Tool(
                name="mark_notification_read",
                func=self._mark_notification_read,
                description=(
                    "Mark a notification as read. "
                    "Input should be a JSON string with 'notification_id'."
                )
            )
        )
    
    def get_agent(self) -> AgentExecutor:
        """Initialize and return the notification agent."""
        return initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=AgentType.OPENAI_FUNCTIONS,
            verbose=True,
            max_iterations=5,
            early_stopping_method="generate",
            memory=self.memory,
        )
    
    async def _send_notification(self, query: str) -> str:
        """Send a notification to a user (simulated)."""
        try:
            data = json.loads(query)
            notification_id = f"notif_{len(self.notifications) + 1}"
            
            notification = {
                "notification_id": notification_id,
                "user_id": data.get("user_id"),
                "title": data.get("title"),
                "message": data.get("message"),
                "notification_type": data.get("notification_type", "email"),
                "metadata": data.get("metadata", {}),
                "is_read": False,
                "created_at": datetime.utcnow().isoformat(),
            }
            
            # In a real app, this would send an actual email/SMS/push notification
            if notification["notification_type"] == "email":
                print(f"[EMAIL] {notification['title']}\n{notification['message']}")
            elif notification["notification_type"] == "sms":
                print(f"[SMS] {notification['message']}")
            else:  # push
                print(f"[PUSH] {notification['title']}: {notification['message']}")
            
            self.notifications[notification_id] = notification
            
            return json.dumps({
                "status": "success",
                "notification_id": notification_id,
                "message": "Notification sent successfully"
            })
            
        except Exception as e:
            return json.dumps({"status": "error", "message": str(e)})
    
    async def _get_user_notifications(self, query: str) -> str:
        """Get notifications for a specific user."""
        try:
            data = json.loads(query)
            user_id = data.get("user_id")
            limit = data.get("limit", 10)
            unread_only = data.get("unread_only", False)
            
            user_notifications = [
                n for n in self.notifications.values() 
                if n["user_id"] == user_id
            ]
            
            if unread_only:
                user_notifications = [n for n in user_notifications if not n["is_read"]]
            
            # Sort by creation date, newest first
            user_notifications.sort(key=lambda x: x["created_at"], reverse=True)
            
            return json.dumps({
                "status": "success",
                "notifications": user_notifications[:limit],
                "total": len(user_notifications),
                "unread_count": sum(1 for n in user_notifications if not n["is_read"])
            })
            
        except Exception as e:
            return json.dumps({"status": "error", "message": str(e)})
    
    async def _mark_notification_read(self, query: str) -> str:
        """Mark a notification as read."""
        try:
            data = json.loads(query)
            notification_id = data.get("notification_id")
            
            if notification_id not in self.notifications:
                return json.dumps({"status": "error", "message": "Notification not found"})
            
            self.notifications[notification_id]["is_read"] = True
            self.notifications[notification_id]["read_at"] = datetime.utcnow().isoformat()
            
            return json.dumps({
                "status": "success",
                "message": "Notification marked as read"
            })
            
        except Exception as e:
            return json.dumps({"status": "error", "message": str(e)})
    
    async def process(self, input_data: AgentInput) -> AgentOutput:
        """Process the input and return a response."""
        if not self.agent:
            self.agent = self.get_agent()
            
        try:
            result = await self.agent.arun(input_data.query)
            return AgentOutput(
                output=result,
                metadata={"agent": self.name}
            )
        except Exception as e:
            return AgentOutput(
                output=f"An error occurred: {str(e)}",
                metadata={"agent": self.name, "error": True}
            )
