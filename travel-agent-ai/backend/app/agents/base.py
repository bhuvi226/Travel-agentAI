from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from langchain.agents import Tool
from langchain.agents.agent import AgentExecutor
from langchain.memory import ConversationBufferMemory

class BaseAgent(ABC):
    """Base class for all agents in the system."""
    
    def __init__(self, **kwargs):
        self.agent: Optional[AgentExecutor] = None
        self.tools: List[Tool] = []
        self.memory = ConversationBufferMemory(memory_key="chat_history")
        
    @abstractmethod
    def get_agent(self) -> AgentExecutor:
        """Initialize and return the agent."""
        pass
    
    def add_tool(self, tool: Tool) -> None:
        """Add a tool to the agent's toolset."""
        self.tools.append(tool)
    
    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run the agent with the given input."""
        if not self.agent:
            self.agent = self.get_agent()
        return await self.agent.arun(input_data)

class AgentInput(BaseModel):
    """Base input model for agents."""
    query: str = Field(..., description="The user's query or input")
    context: Optional[Dict[str, Any]] = Field(
        default_factory=dict, 
        description="Additional context for the agent"
    )

class AgentOutput(BaseModel):
    """Base output model for agents."""
    output: str = Field(..., description="The agent's response")
    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict, 
        description="Additional metadata from the agent's execution"
    )
