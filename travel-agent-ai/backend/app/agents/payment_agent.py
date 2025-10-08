from typing import Dict, Any, List, Optional
from langchain.agents import Tool, AgentType, initialize_agent
from langchain.memory import ConversationBufferMemory
from langchain.chat_models import ChatOpenAI
import uuid
import json
from datetime import datetime, timedelta

from .base import BaseAgent, AgentInput, AgentOutput
from ..core.config import settings

class PaymentAgent(BaseAgent):
    """Agent responsible for handling payment processing and transactions."""
    
    def __init__(self):
        super().__init__()
        self.name = "PaymentAgent"
        self.description = "Handles payment processing and transaction management"
        self.llm = ChatOpenAI(
            temperature=0,  # More deterministic for payment operations
            model_name="gpt-4",
            openai_api_key=settings.OPENAI_API_KEY
        )
        self._setup_tools()
        # In-memory storage for transactions (replace with database in production)
        self.transactions = {}
    
    def _setup_tools(self) -> None:
        """Set up tools for the payment agent."""
        self.add_tool(
            Tool(
                name="process_payment",
                func=self._process_payment,
                description=(
                    "Process a payment for a booking. "
                    "Input should be a JSON string with 'amount', 'currency', 'payment_method', "
                    "'booking_reference', and 'user_id'."
                )
            )
        )
        
        self.add_tool(
            Tool(
                name="refund_payment",
                func=self._process_refund,
                description=(
                    "Process a refund for a booking. "
                    "Input should be a JSON string with 'transaction_id' and 'amount' (optional)."
                )
            )
        )
        
        self.add_tool(
            Tool(
                name="get_transaction_status",
                func=self._get_transaction_status,
                description=(
                    "Get the status of a transaction. "
                    "Input should be a JSON string with 'transaction_id'."
                )
            )
        )
    
    def get_agent(self) -> AgentExecutor:
        """Initialize and return the payment agent."""
        return initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=AgentType.OPENAI_FUNCTIONS,
            verbose=True,
            max_iterations=5,
            early_stopping_method="generate",
            memory=self.memory,
        )
    
    async def _process_payment(self, query: str) -> str:
        """Process a payment (simulated)."""
        try:
            data = json.loads(query)
            transaction_id = f"txn_{uuid.uuid4().hex[:16]}"
            
            # Simulate payment processing
            payment_successful = True  # In a real app, this would call a payment processor
            
            transaction = {
                "transaction_id": transaction_id,
                "amount": data.get("amount"),
                "currency": data.get("currency", "USD"),
                "status": "completed" if payment_successful else "failed",
                "payment_method": data.get("payment_method"),
                "booking_reference": data.get("booking_reference"),
                "user_id": data.get("user_id"),
                "timestamp": datetime.utcnow().isoformat(),
            }
            
            self.transactions[transaction_id] = transaction
            
            return json.dumps({
                "status": "success" if payment_successful else "error",
                "transaction_id": transaction_id,
                "message": "Payment processed successfully" if payment_successful else "Payment failed"
            })
            
        except Exception as e:
            return json.dumps({"status": "error", "message": str(e)})
    
    async def _process_refund(self, query: str) -> str:
        """Process a refund (simulated)."""
        try:
            data = json.loads(query)
            transaction_id = data.get("transaction_id")
            
            if transaction_id not in self.transactions:
                return json.dumps({"status": "error", "message": "Transaction not found"})
            
            transaction = self.transactions[transaction_id]
            refund_amount = data.get("amount", transaction["amount"])
            
            # Simulate refund processing
            refund_successful = True
            
            if refund_successful:
                refund_id = f"ref_{uuid.uuid4().hex[:16]}"
                transaction["refund_id"] = refund_id
                transaction["refund_amount"] = refund_amount
                transaction["refund_timestamp"] = datetime.utcnow().isoformat()
                
                return json.dumps({
                    "status": "success",
                    "refund_id": refund_id,
                    "amount_refunded": refund_amount,
                    "message": "Refund processed successfully"
                })
            else:
                return json.dumps({"status": "error", "message": "Refund failed"})
                
        except Exception as e:
            return json.dumps({"status": "error", "message": str(e)})
    
    async def _get_transaction_status(self, query: str) -> str:
        """Get the status of a transaction."""
        try:
            data = json.loads(query)
            transaction_id = data.get("transaction_id")
            
            if transaction_id not in self.transactions:
                return json.dumps({"status": "error", "message": "Transaction not found"})
            
            return json.dumps({
                "status": "success",
                "transaction": self.transactions[transaction_id]
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
