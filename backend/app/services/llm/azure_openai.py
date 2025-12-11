"""
Azure OpenAI implementation for LLM operations.
"""
from openai import AzureOpenAI
from typing import Optional
import json
from .base import LLMService


class AzureOpenAIService(LLMService):
    """Azure OpenAI LLM service implementation."""
    
    def __init__(
        self, 
        endpoint: str, 
        api_key: str, 
        deployment: str,
        api_version: str = "2024-02-15-preview"
    ):
        self.client = AzureOpenAI(
            azure_endpoint=endpoint,
            api_key=api_key,
            api_version=api_version
        )
        self.deployment = deployment
    
    async def chat(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        temperature: float = 0.0,
        max_tokens: int = 2000
    ) -> str:
        """Generate a chat completion."""
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        response = self.client.chat.completions.create(
            model=self.deployment,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        return response.choices[0].message.content
    
    async def chat_json(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.0
    ) -> dict:
        """Generate a chat completion and parse as JSON."""
        # Add JSON instruction to system prompt
        json_system = "You are a helpful assistant that responds only in valid JSON format."
        if system_prompt:
            json_system = f"{system_prompt}\n\nIMPORTANT: Respond only in valid JSON format."
        
        response = await self.chat(
            prompt=prompt,
            system_prompt=json_system,
            temperature=temperature
        )
        
        # Clean response and parse JSON
        response = response.strip()
        if response.startswith("```json"):
            response = response[7:]
        if response.startswith("```"):
            response = response[3:]
        if response.endswith("```"):
            response = response[:-3]
        
        return json.loads(response.strip())
