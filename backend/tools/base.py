import asyncio
import logging
import time
from abc import ABC, abstractmethod
from typing import Any, Optional, Type

from pydantic import BaseModel, ValidationError

logger = logging.getLogger(__name__)

class RetryPolicy(BaseModel):
    max_retries: int = 2
    base_delay: float = 1.0
    exponential_backoff: bool = True
    retryable_exceptions: list[str] = ["TimeoutError", "ConnectionError", "Exception"]

class ToolResult(BaseModel):
    success: bool
    data: Any = None
    error: Optional[str] = None
    latency_ms: float = 0.0
    retry_count: int = 0

class BaseTool(ABC):
    name: str
    description: str
    input_schema: Type[BaseModel]
    output_schema: Type[BaseModel]
    timeout: float = 30.0
    retry_policy: RetryPolicy = RetryPolicy()
    
    @abstractmethod
    async def execute(self, input_data: BaseModel) -> ToolResult:
        """Execute the tool logic."""
        pass
    
    async def run(self, input_data: dict) -> ToolResult:
        """
        Run the tool with input validation, retries, timeout, and logging.
        """
        start_time = time.time()
        
        try:
            validated_input = self.input_schema(**input_data)
        except ValidationError as e:
            latency_ms = (time.time() - start_time) * 1000
            logger.error(f"Tool {self.name} input validation failed: {e}")
            return ToolResult(
                success=False,
                error=f"Input validation error: {e}",
                latency_ms=latency_ms
            )

        retries = 0
        last_exception = None
        
        # Redact input conditionally if needed, here we just log a summary
        logger.info(f"Starting execution of tool {self.name}")
        
        while retries <= self.retry_policy.max_retries:
            try:
                # Enforce timeout
                result = await asyncio.wait_for(
                    self.execute(validated_input),
                    timeout=self.timeout
                )
                
                latency_ms = (time.time() - start_time) * 1000
                result.latency_ms = latency_ms
                result.retry_count = retries
                
                # Output schema validation check (optional, but good practice)
                if result.success and result.data:
                    try:
                        # Ensure the output matches the expected schema
                        self.output_schema(**result.data if isinstance(result.data, dict) else result.data.dict())
                    except Exception as schema_err:
                         logger.warning(f"Tool {self.name} output validation warning: {schema_err}")
                
                logger.info(f"Tool {self.name} execution succeeded. Latency: {latency_ms:.2f}ms, Retries: {retries}")
                return result
                
            except asyncio.TimeoutError as e:
                last_exception = e
                logger.warning(f"Tool {self.name} timed out after {self.timeout}s")
                if "TimeoutError" not in self.retry_policy.retryable_exceptions:
                    break
            except Exception as e:
                last_exception = e
                exception_name = type(e).__name__
                logger.warning(f"Tool {self.name} execution failed (attempt {retries + 1}): {e}")
                
                # Check if exception is retryable
                is_retryable = exception_name in self.retry_policy.retryable_exceptions or "Exception" in self.retry_policy.retryable_exceptions
                if not is_retryable:
                    break
            
            if retries < self.retry_policy.max_retries:
                delay = self.retry_policy.base_delay * (2 ** retries if self.retry_policy.exponential_backoff else 1)
                logger.info(f"Retrying tool {self.name} in {delay}s...")
                await asyncio.sleep(delay)
                
            retries += 1
            
        latency_ms = (time.time() - start_time) * 1000
        logger.error(f"Tool {self.name} failed after {retries} retries. Last error: {last_exception}")
        return ToolResult(
            success=False,
            error=f"Execution failed after {retries} retries: {last_exception}",
            latency_ms=latency_ms,
            retry_count=max(0, retries - 1)
        )
