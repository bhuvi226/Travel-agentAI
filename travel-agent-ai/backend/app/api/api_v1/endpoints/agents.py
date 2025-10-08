from fastapi import APIRouter, Depends, HTTPException, status, Body
from typing import Dict, Any, List, Optional

from app.core.security import get_current_active_user
from app.agents.agent_manager import agent_manager
from app.schemas.agent import AgentRequest, WorkflowRequest

router = APIRouter()

@router.post("/{agent_name}")
async def process_agent_request(
    agent_name: str,
    request: AgentRequest,
    current_user: Dict = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """Process a request with the specified agent."""
    # Add user context to the request
    request.context = request.context or {}
    request.context["user"] = {
        "id": current_user.id,
        "email": current_user.email,
        "is_superuser": current_user.is_superuser
    }
    
    result = await agent_manager.process(
        agent_name=agent_name,
        input_data=request.dict()
    )
    
    if result["status"] == "error":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("message", "Error processing request")
        )
    
    return result

@router.post("/workflow/execute")
async def execute_workflow(
    workflow: WorkflowRequest,
    current_user: Dict = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """Execute a workflow of agent interactions."""
    # Add user context to each step in the workflow
    user_context = {
        "user": {
            "id": current_user.id,
            "email": current_user.email,
            "is_superuser": current_user.is_superuser
        }
    }
    
    # Prepare workflow steps with user context
    workflow_steps = []
    for step in workflow.steps:
        step_data = step.dict()
        if "context" not in step_data:
            step_data["context"] = {}
        step_data["context"].update(user_context)
        workflow_steps.append(step_data)
    
    # Execute the workflow
    result = await agent_manager.process_workflow(workflow_steps)
    
    if result.get("status") == "error":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("message", "Error executing workflow")
        )
    
    return result

@router.get("/list")
async def list_agents() -> Dict[str, Any]:
    """List all available agents and their capabilities."""
    agents_info = {
        "search": {
            "description": "Search for travel options (flights, trains, etc.)",
            "capabilities": ["search_flights", "search_trains"]
        },
        "optimizer": {
            "description": "Optimize travel plans and make recommendations",
            "capabilities": ["find_cheapest_option", "find_fastest_option", "recommend_based_on_preferences"]
        },
        "payment": {
            "description": "Handle payment processing",
            "capabilities": ["process_payment", "refund_payment", "get_transaction_status"]
        },
        "notification": {
            "description": "Manage user notifications",
            "capabilities": ["send_notification", "get_user_notifications", "mark_notification_read"]
        }
    }
    
    return {
        "status": "success",
        "agents": agents_info
    }
