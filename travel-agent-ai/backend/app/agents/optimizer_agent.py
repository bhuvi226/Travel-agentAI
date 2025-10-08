from typing import Dict, Any, List, Optional
from langchain.agents import Tool, AgentType, initialize_agent
from langchain.memory import ConversationBufferMemory
from langchain.chat_models import ChatOpenAI

from .base import BaseAgent, AgentInput, AgentOutput
from ..core.config import settings

class OptimizerAgent(BaseAgent):
    """Agent responsible for optimizing travel plans and making recommendations."""
    
    def __init__(self):
        super().__init__()
        self.name = "OptimizerAgent"
        self.description = "Specialized in optimizing travel plans and making recommendations"
        self.llm = ChatOpenAI(
            temperature=0.7,  # Slightly more creative for recommendations
            model_name="gpt-4",
            openai_api_key=settings.OPENAI_API_KEY
        )
        self._setup_tools()
    
    def _setup_tools(self) -> None:
        """Set up tools for the optimizer agent."""
        self.add_tool(
            Tool(
                name="find_cheapest_option",
                func=self._find_cheapest_option,
                description=(
                    "Find the cheapest travel option from a list of options. "
                    "Input should be a JSON string with 'options' array containing 'price' and other details."
                )
            )
        )
        
        self.add_tool(
            Tool(
                name="find_fastest_option",
                func=self._find_fastest_option,
                description=(
                    "Find the fastest travel option from a list of options. "
                    "Input should be a JSON string with 'options' array containing 'duration' and other details."
                )
            )
        )
        
        self.add_tool(
            Tool(
                name="recommend_based_on_preferences",
                func=self._recommend_based_on_preferences,
                description=(
                    "Recommend the best travel option based on user preferences. "
                    "Input should be a JSON string with 'options' array and 'preferences' object."
                )
            )
        )
    
    def get_agent(self) -> AgentExecutor:
        """Initialize and return the optimizer agent."""
        return initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=AgentType.OPENAI_FUNCTIONS,
            verbose=True,
            max_iterations=5,
            early_stopping_method="generate",
            memory=self.memory,
        )
    
    async def _find_cheapest_option(self, query: str) -> str:
        """Find the cheapest option from a list of travel options."""
        import json
        try:
            data = json.loads(query)
            options = data.get("options", [])
            
            if not options:
                return json.dumps({"status": "error", "message": "No options provided"})
            
            cheapest = min(options, key=lambda x: float(x.get("price", float('inf'))))
            return json.dumps({"status": "success", "result": cheapest})
            
        except Exception as e:
            return json.dumps({"status": "error", "message": str(e)})
    
    async def _find_fastest_option(self, query: str) -> str:
        """Find the fastest option from a list of travel options."""
        import json
        try:
            data = json.loads(query)
            options = data.get("options", [])
            
            if not options:
                return json.dumps({"status": "error", "message": "No options provided"})
            
            # Assuming duration is in minutes
            fastest = min(options, key=lambda x: int(x.get("duration_minutes", float('inf'))))
            return json.dumps({"status": "success", "result": fastest})
            
        except Exception as e:
            return json.dumps({"status": "error", "message": str(e)})
    
    async def _recommend_based_on_preferences(self, query: str) -> str:
        """Recommend the best option based on user preferences."""
        import json
        try:
            data = json.loads(query)
            options = data.get("options", [])
            preferences = data.get("preferences", {})
            
            if not options:
                return json.dumps({"status": "error", "message": "No options provided"})
            
            # Simple scoring based on preferences
            def calculate_score(option):
                score = 0
                
                # Price preference (lower is better)
                price_weight = preferences.get("price_importance", 0.5)
                max_price = max(opt.get("price", 0) for opt in options) or 1
                score += (1 - (option.get("price", 0) / max_price)) * price_weight
                
                # Duration preference (shorter is better)
                duration_weight = preferences.get("duration_importance", 0.5)
                max_duration = max(opt.get("duration_minutes", 0) for opt in options) or 1
                score += (1 - (option.get("duration_minutes", 0) / max_duration)) * duration_weight
                
                # Add more preference factors as needed
                
                return score
            
            # Sort options by score
            ranked = sorted(options, key=calculate_score, reverse=True)
            return json.dumps({
                "status": "success",
                "result": ranked[0] if ranked else None,
                "all_ranked": ranked
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
