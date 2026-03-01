from typing import Dict, Any, Callable
from enum import Enum
from dataclasses import dataclass
import asyncio
from datetime import datetime

from agents.detection_agent import DetectionAgentState
from agents.loading_agent import LoadingAgentState


class MessageType(Enum):
    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"
    ERROR = "error"


class AgentType(Enum):
    DETECTION = "detection"
    LOADING = "loading"
    ANALYSIS = "analysis"
    PROCESSING = "processing"


class Message:
    """
    Standard message format for agent communication
    """
    def __init__(self, msg_type: MessageType, sender: AgentType, receiver: AgentType, 
                 content: Dict[str, Any], correlation_id: str = None):
        self.type = msg_type
        self.sender = sender
        self.receiver = receiver
        self.content = content
        self.correlation_id = correlation_id or f"msg_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        self.timestamp = datetime.now()


class AgentCommunicationHub:
    """
    Central hub for agent communication.
    Manages message passing between different agents.
    """
    
    def __init__(self):
        self.agents = {}
        self.message_queue = asyncio.Queue()
        self.history = []
    
    def register_agent(self, agent_type: AgentType, agent_instance):
        """
        Register an agent with the communication hub.
        """
        self.agents[agent_type] = agent_instance
    
    async def send_message(self, message: Message):
        """
        Send a message to the appropriate agent.
        """
        self.history.append(message)
        await self.message_queue.put(message)
        
        # Process the message
        await self._route_message(message)
    
    async def _route_message(self, message: Message):
        """
        Route the message to the appropriate receiver.
        """
        if message.receiver in self.agents:
            receiver = self.agents[message.receiver]
            
            # Handle different message types
            if message.type == MessageType.REQUEST:
                await self._handle_request(receiver, message)
            elif message.type == MessageType.NOTIFICATION:
                await self._handle_notification(receiver, message)
            elif message.type == MessageType.ERROR:
                await self._handle_error(receiver, message)
    
    async def _handle_request(self, receiver, message: Message):
        """
        Handle a request message.
        """
        request_type = message.content.get('request_type')
        
        if request_type == "scan_directories":
            custom_dirs = message.content.get('directories')
            if hasattr(receiver, 'scan_directories'):
                result = receiver.scan_directories(custom_dirs)
                response_msg = Message(
                    msg_type=MessageType.RESPONSE,
                    sender=message.receiver,
                    receiver=message.sender,
                    content={
                        'request_type': 'scan_directories',
                        'result': result.dict() if hasattr(result, 'dict') else result.__dict__,
                        'correlation_id': message.correlation_id
                    },
                    correlation_id=message.correlation_id
                )
                await self.send_message(response_msg)
        
        elif request_type == "load_file":
            file_path = message.content.get('file_path')
            file_type = message.content.get('file_type')
            if hasattr(receiver, 'load_file'):
                result = receiver.load_file(file_path, file_type)
                response_msg = Message(
                    msg_type=MessageType.RESPONSE,
                    sender=message.receiver,
                    receiver=message.sender,
                    content={
                        'request_type': 'load_file',
                        'result': result.dict() if hasattr(result, 'dict') else result.__dict__,
                        'correlation_id': message.correlation_id
                    },
                    correlation_id=message.correlation_id
                )
                await self.send_message(response_msg)
        
        elif request_type == "load_multiple_files":
            file_list = message.content.get('file_list')
            if hasattr(receiver, 'load_multiple_files'):
                result = receiver.load_multiple_files(file_list)
                response_msg = Message(
                    msg_type=MessageType.RESPONSE,
                    sender=message.receiver,
                    receiver=message.sender,
                    content={
                        'request_type': 'load_multiple_files',
                        'result': result.dict() if hasattr(result, 'dict') else result.__dict__,
                        'correlation_id': message.correlation_id
                    },
                    correlation_id=message.correlation_id
                )
                await self.send_message(response_msg)
    
    async def _handle_notification(self, receiver, message: Message):
        """
        Handle a notification message.
        """
        notification_type = message.content.get('notification_type')
        if notification_type == "update_state":
            new_state = message.content.get('state')
            if hasattr(receiver, 'update_state'):
                # Convert dict back to appropriate state object based on agent type
                if isinstance(receiver, type(self.agents[AgentType.DETECTION])):
                    from agents.detection_agent import DetectionAgentState
                    state_obj = DetectionAgentState(**new_state)
                    receiver.update_state(state_obj)
                elif isinstance(receiver, type(self.agents[AgentType.LOADING])):
                    from agents.loading_agent import LoadingAgentState
                    state_obj = LoadingAgentState(**new_state)
                    receiver.update_state(state_obj)
    
    async def _handle_error(self, receiver, message: Message):
        """
        Handle an error message.
        """
        error_content = message.content.get('error')
        print(f"Error received by {message.receiver.value} agent: {error_content}")
    
    async def get_next_message(self):
        """
        Get the next message from the queue.
        """
        return await self.message_queue.get()
    
    def get_history(self):
        """
        Get the message history.
        """
        return self.history


class AgentCollaborationManager:
    """
    Manager class to coordinate collaboration between agents.
    """
    
    def __init__(self):
        self.communication_hub = AgentCommunicationHub()
        
    def register_agents(self, detection_agent, loading_agent):
        """
        Register the main agents for the data science workflow.
        """
        self.communication_hub.register_agent(AgentType.DETECTION, detection_agent)
        self.communication_hub.register_agent(AgentType.LOADING, loading_agent)
    
    async def coordinate_data_loading(self, directories: list = None):
        """
        Coordinate the process of scanning directories and loading files.
        """
        # Step 1: Request detection agent to scan directories
        scan_request = Message(
            msg_type=MessageType.REQUEST,
            sender=AgentType.PROCESSING,
            receiver=AgentType.DETECTION,
            content={'request_type': 'scan_directories', 'directories': directories}
        )
        await self.communication_hub.send_message(scan_request)
        
        # Wait for response from detection agent
        detection_response = await self._wait_for_response(scan_request.correlation_id)
        
        # Step 2: Use detection results to load files with loading agent
        if detection_response and 'detected_files' in detection_response.get('result', {}):
            detected_files = detection_response['result']['detected_files']
            
            # Send notification to loading agent to prepare for loading
            load_request = Message(
                msg_type=MessageType.REQUEST,
                sender=AgentType.PROCESSING,
                receiver=AgentType.LOADING,
                content={'request_type': 'load_multiple_files', 'file_list': detected_files}
            )
            await self.communication_hub.send_message(load_request)
            
            # Wait for response from loading agent
            loading_response = await self._wait_for_response(load_request.correlation_id)
            
            return detection_response, loading_response
        
        return None, None
    
    async def _wait_for_response(self, correlation_id: str, timeout: int = 30):
        """
        Wait for a response with a specific correlation ID.
        """
        start_time = datetime.now()
        while (datetime.now() - start_time).seconds < timeout:
            for msg in self.communication_hub.get_history():
                if (msg.correlation_id == correlation_id and 
                    msg.type == MessageType.RESPONSE):
                    return msg.content
            await asyncio.sleep(0.1)  # Brief pause before checking again
        return None