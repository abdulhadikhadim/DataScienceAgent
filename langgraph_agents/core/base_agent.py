from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum
import logging
from datetime import datetime


class AgentStatus(Enum):
    """Agent execution status"""
    IDLE = "idle"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class ProcessingPriority(Enum):
    """Processing priority levels"""
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4


@dataclass
class AgentMetrics:
    """Metrics for agent performance tracking"""
    execution_time: float = 0.0
    records_processed: int = 0
    records_modified: int = 0
    errors_encountered: int = 0
    warnings_generated: int = 0
    memory_usage_mb: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "execution_time": self.execution_time,
            "records_processed": self.records_processed,
            "records_modified": self.records_modified,
            "errors_encountered": self.errors_encountered,
            "warnings_generated": self.warnings_generated,
            "memory_usage_mb": self.memory_usage_mb
        }


@dataclass
class AgentResult:
    """Standardized result from agent execution"""
    status: AgentStatus
    agent_name: str
    timestamp: datetime = field(default_factory=datetime.now)
    metrics: AgentMetrics = field(default_factory=AgentMetrics)
    messages: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status.value,
            "agent_name": self.agent_name,
            "timestamp": self.timestamp.isoformat(),
            "metrics": self.metrics.to_dict(),
            "messages": self.messages,
            "errors": self.errors,
            "warnings": self.warnings,
            "metadata": self.metadata
        }


class BaseAgent(ABC):
    """
    Abstract base class for all preprocessing agents.
    Implements OOP principles: Encapsulation, Abstraction, Polymorphism.
    """
    
    def __init__(self, name: str, priority: ProcessingPriority = ProcessingPriority.MEDIUM):
        self.name = name
        self.priority = priority
        self.logger = self._setup_logger()
        self._status = AgentStatus.IDLE
        self._metrics = AgentMetrics()
    
    def _setup_logger(self) -> logging.Logger:
        """Setup agent-specific logger"""
        logger = logging.getLogger(f"Agent.{self.name}")
        logger.setLevel(logging.INFO)
        return logger
    
    @property
    def status(self) -> AgentStatus:
        """Get current agent status"""
        return self._status
    
    @abstractmethod
    def validate_input(self, state: Dict[str, Any]) -> bool:
        """
        Validate input state before processing.
        Returns True if input is valid, False otherwise.
        """
        pass
    
    @abstractmethod
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main processing logic. Must be implemented by subclasses.
        Returns updated state.
        """
        pass
    
    @abstractmethod
    def can_run_parallel(self) -> bool:
        """
        Indicates if this agent can run in parallel with others.
        Returns True if parallel execution is safe.
        """
        pass
    
    def execute(self, state: Dict[str, Any]) -> AgentResult:
        """
        Execute agent with error handling and metrics tracking.
        Template Method Pattern.
        """
        start_time = datetime.now()
        result = AgentResult(
            status=AgentStatus.PROCESSING,
            agent_name=self.name
        )
        
        try:
            self._status = AgentStatus.PROCESSING
            self.logger.info(f"Starting {self.name} agent")
            
            if not self.validate_input(state):
                result.status = AgentStatus.FAILED
                result.errors.append("Input validation failed")
                self._status = AgentStatus.FAILED
                return result
            
            updated_state = self.process(state)
            
            result.status = AgentStatus.COMPLETED
            result.messages.append(f"{self.name} completed successfully")
            self._status = AgentStatus.COMPLETED
            
            execution_time = (datetime.now() - start_time).total_seconds()
            result.metrics.execution_time = execution_time
            
            self.logger.info(f"{self.name} completed in {execution_time:.2f}s")
            
            return result
            
        except Exception as e:
            result.status = AgentStatus.FAILED
            result.errors.append(f"Error in {self.name}: {str(e)}")
            self._status = AgentStatus.FAILED
            self.logger.error(f"Error in {self.name}: {str(e)}", exc_info=True)
            return result
    
    def get_metrics(self) -> AgentMetrics:
        """Get agent execution metrics"""
        return self._metrics
    
    def reset(self):
        """Reset agent state"""
        self._status = AgentStatus.IDLE
        self._metrics = AgentMetrics()


class AgentFactory:
    """
    Factory Pattern for creating agents.
    Centralizes agent instantiation logic.
    """
    
    _registry: Dict[str, type] = {}
    
    @classmethod
    def register(cls, agent_type: str, agent_class: type):
        """Register an agent class"""
        cls._registry[agent_type] = agent_class
    
    @classmethod
    def create(cls, agent_type: str, **kwargs) -> BaseAgent:
        """Create an agent instance"""
        if agent_type not in cls._registry:
            raise ValueError(f"Unknown agent type: {agent_type}")
        
        agent_class = cls._registry[agent_type]
        return agent_class(**kwargs)
    
    @classmethod
    def list_available(cls) -> List[str]:
        """List all registered agent types"""
        return list(cls._registry.keys())


class AgentChain:
    """
    Chain of Responsibility Pattern for sequential agent execution.
    """
    
    def __init__(self):
        self.agents: List[BaseAgent] = []
    
    def add_agent(self, agent: BaseAgent):
        """Add agent to chain"""
        self.agents.append(agent)
    
    def execute(self, state: Dict[str, Any]) -> List[AgentResult]:
        """Execute all agents in sequence"""
        results = []
        current_state = state
        
        for agent in self.agents:
            result = agent.execute(current_state)
            results.append(result)
            
            if result.status == AgentStatus.FAILED:
                break
        
        return results
