from typing import Dict, Any
from abc import ABC, abstractmethod

class UniversalTool(ABC):
    """Base interface for all DSTT tools."""
    
    @abstractmethod
    def execute(self, *inputs) -> Any:
        """Executes the tool with the given inputs."""
        pass

    @abstractmethod
    def get_signature(self) -> Dict[str, Any]:
        """Returns the signature of the tool containing inputs and outputs."""
        pass
