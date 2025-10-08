from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional

class AgentRequest(BaseModel):
    """Schema for agent request data."""
    query: str = Field(..., description="The query or input for the agent")
    context: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Additional context for the agent"
    )
    parameters: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Additional parameters for the agent"
    )

class WorkflowStep(BaseModel):
    """Schema for a single step in a workflow."""
    agent: str = Field(..., description="Name of the agent to use")
    input: AgentRequest = Field(..., description="Input for the agent")
    description: Optional[str] = Field(
        None,
        description="Description of what this step does"
    )

class WorkflowRequest(BaseModel):
    """Schema for a workflow of agent interactions."""
    steps: List[WorkflowStep] = Field(..., description="List of steps to execute")
    context: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Global context for the workflow"
    )

class AgentResponse(BaseModel):
    """Base response schema for agent operations."""
    status: str = Field(..., description="Status of the operation")
    output: Optional[Any] = Field(
        None,
        description="Output from the agent"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Additional metadata from the agent"
    )
    error: Optional[str] = Field(
        None,
        description="Error message if the operation failed"
    )

class WorkflowResponse(BaseModel):
    """Response schema for workflow execution."""
    status: str = Field(..., description="Overall status of the workflow")
    results: Dict[str, Any] = Field(
        ...,
        description="Results from each step in the workflow"
    )
    context: Dict[str, Any] = Field(
        default_factory=dict,
        description="Final context after workflow execution"
    )
