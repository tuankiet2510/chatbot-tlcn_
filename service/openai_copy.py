from typing import Iterable, Optional, Literal, Dict, Any
from uuid import UUID
from env import env
from openai import NotGiven, OpenAI
import json
from openai.types.chat import (
    ChatCompletionMessageParam,
    ChatCompletionToolMessageParam,
    ChatCompletionToolParam,
) # typehint to ensure safety
from tools.invoke_tool import invoke
import chainlit as cl
import requests
from pydantic import BaseModel, Field

_model = "gpt-4o-mini"
_client = OpenAI(
    api_key=env.OPENAI_API_KEY,
)


# Thêm model type để phân biệt loại model
ModelType = Literal["openai", "open_source"]

# Cấu hình cho model open source
class OpenSourceModelConfig(BaseModel):
    url: str = Field(..., description="API endpoint URL")
    model_name: str = Field(..., description="Tên model")
    api_key: Optional[str] = Field(None, description="API key nếu cần")
    max_tokens: int = Field(2048, description="Số token tối đa cho output")
    temperature: float = Field(0.0, description="Temperature parameter")

# Cấu hình model open source mặc định
_open_source_config = OpenSourceModelConfig(
    url=env.OPEN_SOURCE_MODEL_URL,
    model_name=env.OPEN_SOURCE_MODEL_NAME,
    api_key=env.OPEN_SOURCE_API_KEY,
    max_tokens=2048,
    temperature=0.0
)

def gen_answer(
    user_id: UUID,
    thread_id: UUID,
    messages: list[ChatCompletionMessageParam],
    tools: Iterable[ChatCompletionToolParam],
    max_iterator: int = 5,
    model: str = _model,
    temporary_memory: dict = {},
    model_type: ModelType = "openai",
    open_source_config: Optional[OpenSourceModelConfig] = None,
) -> tuple[str, dict[str, str]]:
    """
    Generate answer using specified model
    
    Args:
        user_id: User ID
        thread_id: Thread ID
        messages: List of messages
        tools: List of tools
        max_iterator: Maximum number of tool calling iterations
        model: Model name
        temporary_memory: Temporary memory dictionary
        model_type: Type of model to use ("openai" or "open_source")
        open_source_config: Configuration for open source model
        
    Returns:
        Tuple of (response text, temporary memory)
    """
    if model_type == "openai":
        return _gen_openai_answer(
            user_id=user_id,
            thread_id=thread_id,
            messages=messages,
            tools=tools,
            max_iterator=max_iterator,
            model=model,
            temporary_memory=temporary_memory,
        )
    else:
        return _gen_open_source_answer(
            user_id=user_id,
            thread_id=thread_id,
            messages=messages,
            tools=tools,
            max_iterator=max_iterator,
            config=open_source_config or _open_source_config,
            temporary_memory=temporary_memory,
        )

def _gen_openai_answer(
    user_id: UUID,
    thread_id: UUID,
    messages: list[ChatCompletionMessageParam],
    tools: Iterable[ChatCompletionToolParam],
    max_iterator: int = 5,
    model: str = _model,
    temporary_memory: dict = {},
) -> tuple[str, dict[str, str]]:
    """Hàm gốc gen_answer được đổi tên thành _gen_openai_answer"""
    counter = 0
    response = (
        _client.chat.completions.create(
            messages=messages,
            model=model,
            user=str(user_id),
            tools=tools,
            temperature=0,
            timeout=30,
        )
        .choices[0]
        .message
    )
    # OpenAI will return tool_calls corresponding to the tools used by the model with instructions prompt
    tool_choices = response.tool_calls
    # return response immediately if no tool_calls
    if not tool_choices:
        if not response.content:
            raise Exception("No response content from the model")
        print("Final response:", response.content)
        return response.content, temporary_memory

    while tool_choices and counter < max_iterator:
        counter += 1
        
        print("counter:", counter) 
        # append model's function call message's copy
        messages.append(response.model_copy())  # type: ignore
        print("\n\n==== tool_calls ====\n\n")
        for tool in tool_choices:
            print(tool.function.name)
            call_id = tool.id
            tool_name = tool.function.name
            args = json.loads(tool.function.arguments) # parse tool func arguments to json
            tool_response: ChatCompletionToolMessageParam = {
                "role": "tool",
                "tool_call_id": call_id,
                "content": invoke(user_id, thread_id, tool_name, args), # get tool response from invoke_tool.py
            }
            # append tool result to messages
            messages.append(tool_response)  # type: ignore
            # store tool result to temporary memory
            temporary_memory[tool_name] = tool_response["content"]
            print("Tool response:", tool_response["content"])
        response = (
            _client.chat.completions.create(
                messages=messages,
                model=model,
                user=str(user_id),
                tools=tools,
                temperature=0,
                timeout=30,
            )
            .choices[0]
            .message
        )
        tool_choices = response.tool_calls

    if counter == max_iterator:
        raise Exception(
            f"Maximum iteration reached ({max_iterator}). Please try again."
        )
    if not response.content:
        raise Exception("No response content from the model")

    print("Final response:", response.content)
    return response.content, temporary_memory

def _gen_open_source_answer(
    user_id: UUID,
    thread_id: UUID,
    messages: list[ChatCompletionMessageParam],
    tools: Iterable[ChatCompletionToolParam],
    max_iterator: int = 5,
    config: OpenSourceModelConfig = _open_source_config,
    temporary_memory: dict = {},
) -> tuple[str, dict[str, str]]:
    """
    Generate answer using open source model
    
    Args:
        user_id: User ID
        thread_id: Thread ID
        messages: List of messages
        tools: List of tools
        max_iterator: Maximum number of tool calling iterations
        config: Configuration for open source model
        temporary_memory: Temporary memory dictionary
        
    Returns:
        Tuple of (response text, temporary memory)
    """
    counter = 0
    
    # Chuẩn bị payload cho API request
    payload = {
        "model": config.model_name,
        "messages": messages,
        "temperature": config.temperature,
        "max_tokens": config.max_tokens,
        "tools": list(tools),  # Convert iterable to list
    }
    
    # Headers cho API request
    headers = {
        "Content-Type": "application/json"
    }
    
    # Thêm API key nếu có
    if config.api_key:
        headers["Authorization"] = f"Bearer {config.api_key}"
    
    # Gọi API
    response = requests.post(
        config.url,
        json=payload,
        headers=headers,
        timeout=60  # Timeout dài hơn cho model open source
    )
    
    # Kiểm tra response
    if response.status_code != 200:
        raise Exception(f"API error: {response.status_code} - {response.text}")
    
    # Parse response
    response_data = response.json()
    message = response_data["choices"][0]["message"]
    content = message.get("content", "")
    tool_calls = message.get("tool_calls", [])
    
    # Nếu không có tool calls, trả về response ngay
    if not tool_calls:
        if not content:
            raise Exception("No response content from the model")
        print("Final response:", content)
        return content, temporary_memory
    
    # Xử lý tool calls
    while tool_calls and counter < max_iterator:
        counter += 1
        
        print("counter:", counter)
        # Thêm message của model vào messages
        messages.append(message)
        print("\n\n==== tool_calls ====\n\n")
        
        for tool in tool_calls:
            print(tool["function"]["name"])
            call_id = tool["id"]
            tool_name = tool["function"]["name"]
            args = json.loads(tool["function"]["arguments"])
            
            tool_response: ChatCompletionToolMessageParam = {
                "role": "tool",
                "tool_call_id": call_id,
                "content": invoke(user_id, thread_id, tool_name, args),
            }
            
            # Thêm tool response vào messages
            messages.append(tool_response)
            # Lưu tool response vào temporary memory
            temporary_memory[tool_name] = tool_response["content"]
            print("Tool response:", tool_response["content"])
        
        # Gọi API lại với messages mới
        payload["messages"] = messages
        response = requests.post(
            config.url,
            json=payload,
            headers=headers,
            timeout=60
        )
        
        if response.status_code != 200:
            raise Exception(f"API error: {response.status_code} - {response.text}")
        
        response_data = response.json()
        message = response_data["choices"][0]["message"]
        content = message.get("content", "")
        tool_calls = message.get("tool_calls", [])
    
    if counter == max_iterator:
        raise Exception(f"Maximum iteration reached ({max_iterator}). Please try again.")
    
    if not content:
        raise Exception("No response content from the model")
    
    print("Final response:", content)
    return content, temporary_memory