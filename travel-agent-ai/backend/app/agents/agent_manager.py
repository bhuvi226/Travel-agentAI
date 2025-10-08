from typing import Dict, Any, Optional, List
from .search_agent import SearchAgent
from .optimizer_agent import OptimizerAgent
from .payment_agent import PaymentAgent
from .notification_agent import NotificationAgent
from .base import AgentInput, AgentOutput

class AgentManager:
    """Manages all agents and coordinates between them."""
    
    def __init__(self):
        self.agents = {
            "search": SearchAgent(),
            "optimizer": OptimizerAgent(),
            "payment": PaymentAgent(),
            "notification": NotificationAgent()
        }
        
    async def process(self, agent_name: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input with the specified agent."""
        if agent_name not in self.agents:
            return {
                "status": "error",
                "message": f"Agent '{agent_name}' not found"
            }
            
        agent = self.agents[agent_name]
        agent_input = AgentInput(
            query=input_data.get("query", ""),
            context=input_data.get("context", {})
        )
        
        try:
            result = await agent.process(agent_input)
            return {
                "status": "success",
                "output": result.output,
                "metadata": result.metadata
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "agent": agent_name
            }
    
    async def process_workflow(self, workflow: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process a workflow of agent interactions."""
        results = {}
        context = {}
        
        for i, step in enumerate(workflow):
            agent_name = step.get("agent")
            if not agent_name:
                results[f"step_{i}"] = {
                    "status": "error",
                    "message": "No agent specified"
                }
                continue
                
            # Add previous results to context
            step_input = step.get("input", {})
            if "context" not in step_input:
                step_input["context"] = {}
            step_input["context"].update(context)
            
            # Process the step
            result = await self.process(agent_name, step_input)
            results[f"step_{i}"] = result
            
            # If any step fails, mark the workflow as failed
            if result.get("status") == "error":
                results["status"] = "error"
                results["failed_step"] = i
                break
                
            # Update context with the result
            context[agent_name] = result
        
        if "status" not in results:
            results["status"] = "success"
            
        return results

# Global instance of the agent manager
agent_manager = AgentManager()
