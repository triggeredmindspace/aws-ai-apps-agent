"""
LLM client abstraction supporting both Anthropic Claude and OpenAI.
Supports Message Batches API for 50% cost reduction.
"""

import time
from typing import Optional, List, Dict
from abc import ABC, abstractmethod
from src.utils.logger import get_logger

logger = get_logger(__name__)


class LLMClient(ABC):
    """Abstract base class for LLM clients"""

    @abstractmethod
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048
    ) -> str:
        """Generate text from a prompt"""
        pass

    @abstractmethod
    def generate_with_messages(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048
    ) -> str:
        """Generate text from a conversation history"""
        pass

    def generate_batch(
        self,
        requests: Dict[str, dict],
        poll_interval: int = 10,
        max_wait: int = 600
    ) -> Dict[str, str]:
        """
        Submit multiple prompts as a batch for cost savings.
        Default: falls back to sequential calls.
        """
        results = {}
        for req_id, params in requests.items():
            results[req_id] = self.generate(**params)
        return results


class AnthropicClient(LLMClient):
    """Anthropic Claude client with Message Batches API support (50% off)"""

    def __init__(self, api_key: str, model: str = "claude-haiku-4-5-20251001"):
        try:
            import anthropic
            self.client = anthropic.Anthropic(api_key=api_key)
            self.model = model
        except ImportError:
            raise ImportError("anthropic package not installed. Run: pip install anthropic")

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048
    ) -> str:
        """Generate text using Claude (single request, full price)"""
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt or "",
                messages=[{"role": "user", "content": prompt}]
            )
            return message.content[0].text
        except Exception as e:
            logger.error(f"Claude API error: {e}")
            raise

    def generate_with_messages(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048
    ) -> str:
        """Generate text from conversation history"""
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt or "",
                messages=messages
            )
            return message.content[0].text
        except Exception as e:
            logger.error(f"Claude API error: {e}")
            raise

    def generate_batch(
        self,
        requests: Dict[str, dict],
        poll_interval: int = 10,
        max_wait: int = 600
    ) -> Dict[str, str]:
        """
        Submit multiple prompts via the Message Batches API (50% cheaper).
        Falls back to sequential calls if batch fails or times out.
        """
        if len(requests) < 2:
            return super().generate_batch(requests, poll_interval, max_wait)

        logger.info(f"Submitting batch of {len(requests)} requests (50% cost savings)")

        try:
            # Build batch requests
            batch_requests = []
            for req_id, params in requests.items():
                batch_requests.append({
                    "custom_id": req_id,
                    "params": {
                        "model": self.model,
                        "max_tokens": params.get("max_tokens", 2048),
                        "temperature": params.get("temperature", 0.7),
                        "system": params.get("system_prompt", "") or "",
                        "messages": [{"role": "user", "content": params["prompt"]}]
                    }
                })

            # Create the batch
            batch = self.client.messages.batches.create(requests=batch_requests)
            batch_id = batch.id
            logger.info(f"Batch created: {batch_id}")

            # Poll for completion
            elapsed = 0
            while elapsed < max_wait:
                batch = self.client.messages.batches.retrieve(batch_id)

                if batch.processing_status == "ended":
                    logger.info(f"Batch {batch_id} completed in {elapsed}s")
                    break

                logger.debug(f"Batch {batch_id}: {batch.processing_status} ({elapsed}s)")
                time.sleep(poll_interval)
                elapsed += poll_interval
            else:
                logger.warning(f"Batch timed out after {max_wait}s, falling back to sequential")
                return super().generate_batch(requests, poll_interval, max_wait)

            # Retrieve results
            results = {}
            for result in self.client.messages.batches.results(batch_id):
                req_id = result.custom_id
                if result.result.type == "succeeded":
                    results[req_id] = result.result.message.content[0].text
                else:
                    logger.error(f"Batch request {req_id} failed, retrying individually")
                    if req_id in requests:
                        try:
                            results[req_id] = self.generate(**requests[req_id])
                        except Exception:
                            results[req_id] = ""

            logger.info(f"Batch returned {len(results)}/{len(requests)} results")
            return results

        except Exception as e:
            logger.warning(f"Batch API failed ({e}), falling back to sequential")
            return super().generate_batch(requests, poll_interval, max_wait)


class OpenAIClient(LLMClient):
    """OpenAI GPT client implementation"""

    def __init__(self, api_key: str, model: str = "gpt-4-turbo"):
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=api_key)
            self.model = model
        except ImportError:
            raise ImportError("openai package not installed. Run: pip install openai")

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048
    ) -> str:
        """Generate text using GPT"""
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise

    def generate_with_messages(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048
    ) -> str:
        """Generate text from conversation history"""
        try:
            full_messages = []
            if system_prompt:
                full_messages.append({"role": "system", "content": system_prompt})
            full_messages.extend(messages)

            response = self.client.chat.completions.create(
                model=self.model,
                messages=full_messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise


def create_llm_client(provider: str, api_key: str, model: str) -> LLMClient:
    """Factory function to create appropriate LLM client."""
    if provider == "anthropic":
        return AnthropicClient(api_key, model)
    elif provider == "openai":
        return OpenAIClient(api_key, model)
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")
