"""
Abstract base class for LLM operations.
All LLM implementations must follow this interface.
"""
from abc import ABC, abstractmethod
from typing import Optional


class LLMService(ABC):
    """Abstract LLM service interface."""
    
    @abstractmethod
    async def chat(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        temperature: float = 0.0,
        max_tokens: int = 2000
    ) -> str:
        """
        Generate a chat completion.
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            temperature: Sampling temperature (0 = deterministic)
            max_tokens: Maximum tokens in response
            
        Returns:
            Generated text response
        """
        pass
    
    @abstractmethod
    async def chat_json(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.0
    ) -> dict:
        """
        Generate a chat completion and parse as JSON.
        
        Args:
            prompt: User prompt (should request JSON output)
            system_prompt: Optional system prompt
            temperature: Sampling temperature
            
        Returns:
            Parsed JSON response as dict
        """
        pass
