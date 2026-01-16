from abc import ABC, abstractmethod
from typing import Dict, Any


class RobotInterface(ABC):
    """
    OEM-agnostic robot control interface.
    All hardware-specific drivers must implement this.
    """

    @abstractmethod
    def connect(self) -> bool:
        pass

    @abstractmethod
    def navigate_to_node(self, node_id: str) -> bool:
        pass

    @abstractmethod
    def start_cleaning(self, mode: str, params: Dict[str, Any] | None = None) -> bool:
        pass

    @abstractmethod
    def stop_cleaning(self) -> bool:
        pass

    @abstractmethod
    def get_status(self) -> Dict[str, Any]:
        pass
