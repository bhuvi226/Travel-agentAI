from typing import Dict, Any, List, Optional
from langchain.agents import Tool, AgentType, initialize_agent
from langchain.memory import ConversationBufferMemory
from langchain.chat_models import ChatOpenAI
from langchain.agents.agent import AgentExecutor

from .base import BaseAgent, AgentInput, AgentOutput
from ..core.config import settings

class SearchAgent(BaseAgent):
    """Agent responsible for searching and retrieving travel options."""
    
    def __init__(self):
        super().__init__()
        self.name = "SearchAgent"
        self.description = "Specialized in finding and comparing travel options"
        self.llm = ChatOpenAI(
            temperature=0,
            model_name="gpt-4",
            openai_api_key=settings.OPENAI_API_KEY
        )
        self._setup_tools()
    
    def _setup_tools(self) -> None:
        """Set up tools for the search agent."""
        self.add_tool(
            Tool(
                name="search_flights",
                func=self._search_flights,
                description=(
                    "Search for flights based on origin, destination, and dates. "
                    "Input should be a JSON string with 'origin', 'destination', 'departure_date', "
                    "and optional 'return_date' and 'passengers'."
                )
            )
        )
        
        self.add_tool(
            Tool(
                name="search_trains",
                func=self._search_trains,
                description=(
                    "Search for train routes based on origin, destination, and date. "
                    "Input should be a JSON string with 'origin', 'destination', 'date', "
                    "and optional 'passengers'."
                )
            )
        )
    
    def get_agent(self) -> AgentExecutor:
        """Initialize and return the search agent."""
        return initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=AgentType.OPENAI_FUNCTIONS,
            verbose=True,
            max_iterations=5,
            early_stopping_method="generate",
            memory=self.memory,
        )
    
    async def _search_flights(self, query: str) -> str:
        """Search for flights using external API (simulated for now)."""
        # In a real implementation, this would call an actual flight API
        # For now, we'll simulate a response
        import json
        try:
            params = json.loads(query)
            return json.dumps({
                "status": "success",
                "results": [
                    {
                        "id": "flt_123",
                        "airline": "Demo Airlines",
                        "flight_number": "DA123",
                        "origin": params.get("origin", "Unknown"),
                        "destination": params.get("destination", "Unknown"),
                        "departure_time": f"{params.get('departure_date')}T10:00:00",
                        "arrival_time": f"{params.get('departure_date')}T12:00:00",
                        "price": 299.99,
                        "currency": "USD"
                    }
                ]
            })
        except Exception as e:
            return json.dumps({"status": "error", "message": str(e)})
    
    async def _search_trains(self, query: str) -> str:
        """Search for train routes using external API (simulated for now)."""
        # In a real implementation, this would call an actual train API
        # For now, we'll simulate a response
        import json
        try:
            params = json.loads(query)
            return json.dumps({
                "status": "success",
                "results": [
                    {
                        "id": "train_456",
                        "train_name": "Express Train",
                        "train_number": "ET456",
                        "origin": params.get("origin", "Unknown"),
                        "destination": params.get("destination", "Unknown"),
                        "departure_time": f"{params.get('date')}T08:30:00",
                        "arrival_time": f"{params.get('date')}T11:45:00",
                        "price": 89.99,
                        "currency": "USD",
                        "class": "Standard"
                    }
                ]
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
