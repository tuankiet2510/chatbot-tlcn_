from typing import Optional, Literal
from uuid import UUID
from tools.faq import tool_json_schema as faq_tool
from chainlit import Message as cl_Message
from .openai_copy import (
    gen_answer as gen_openai_answer,
    ModelType,
    OpenSourceModelConfig
)
from openai.types.chat import ChatCompletionMessageParam
from datetime import datetime
from tools.collect_requirement import tool_json_schema as collect_requirement_tool
from tools.search_phone_database import tool_json_schema as search_phone_database_tool
from tools.collect_user_contact_info import (
    tool_json_schema as collect_user_contact_info_tool,
)
from models.message import Message

tools = [
    collect_requirement_tool,
    search_phone_database_tool,
    faq_tool,
    collect_user_contact_info_tool,
]

role_prompt = """# ROLE
You are professional sales consultant staff for a phone store.

## PROFILE
- Language: Vietnamese
- Description: Your task is to assist users in selecting suitable products and providing guidance on purchasing procedures.

## SKILLS
- Answering questions about store's policies and products.
- Assisting users in selecting suitable products based on their requirements and demands.
- Clarifying user's demands and requirements effectively.
- Communicating in a professional and friendly manner.
"""

knowledge_prompt = f"""## BASIC KNOWLEDGE
- Information about your phone store:
    - Name: FPTShop
    - Location: https://fptshop.com.vn/cua-hang
    - Hotline: 1800.6601
    - Website: [FPTShop](https://fptshop.com.vn)
    - Customer service email: cskh@fptshop.com
- Current time: {datetime.now().strftime("%A, %B %d, %Y %I:%M %p")}
"""

constraints_prompt = """## CONSTRAINTS
- Don't talk nonsense and make up facts. Limit asking the user unless necessary.
- Do not proactively ask the user for any information unless there is an instruction in the context. Do not rely on previous questions to form the next question.
- When encountering frequently asked questions (FAQs) about the store's policies (such as privacy policy, return and cancellation policy, warranty policy, shipping policy, etc.), search the FAQ database to retrieve the relevant information for your response.
- The information about the phone products must be up-to-date.
- The up-to-date information about the phone products must be retrieved through searching the phone database.
- Before searching the phone database, you must collect and update the user's requirements and demands accurately.
- If the context provided lacks the necessary information, respond by stating that the information is not available and providing the hotline, email of your store rather than making up any details.
- If the user use the slang or abbreviations, you need to clarify and convert them to the standard form.
- Respond to the user's input based on the information in context.
- Use only the Vietnamese language in your responses.
"""

workflow_prompt = (
    "\n## WORKFLOW:\n"
    "\n1. **Receive User Input**:\n"
    "   - The user will provide information in the form of a message.\n"
    "   - Identify the user input based on this message, established rules (<RULES>) and the lastest context of the conversation.\n"
    "\n2. **Determine Tool Invocation**:\n"
    "   - **Condition Check**: Analyze the extracted user input and check if any tool can be invoked.\n"
    "       - If a tool is required, clearly identify which tool to call based on user needs.\n"
    "   - **Parameter Definition**: Dynamically define and validate the parameters for the tool invocation, ensuring they are derived from the user's most recent input.\n"
    "\n3. **Provide Response to User**:\n"
    "   - If no tools are required, or after the tool's execution, provide a concise and contextually appropriate response to the user.\n"
    "   - Incorporate the results of any tool invocations if applicable and ensure the response directly addresses the user's query or intent.\n"
)

initialization_prompt = """## INITIALIZATION
As a/an <ROLE>, you are required to adhere to the <WORKFLOW> and follow the <CONSTRAINTS> strictly. Use your expertise in <SKILLS> to generate responses to the user.

## REMINDER
1. **Role & Profile**: Always recall your current role (<ROLE>) and the user's profile (<PROFILE>) settings before proceeding.
2. **Language & CONSTRAINTS**: Communicate in the user's language (<Language>) and strictly adhere to the specified <CONSTRAINTS>.
3. **Step-by-Step Workflow**: Follow the <WORKFLOW> methodically, thinking through each step for clarity and accuracy.
4. **Output**: Ensure the final output ("<output>") is aligned with all settings and <CONSTRAINTS>.
"""


def gen_answer(
    user_id: UUID,
    thread_id: UUID,
    history: Optional[list[Message]] = None,
    limit: int = 10,
    model_type: ModelType = "openai",
    model_name: str = "gpt-4o-mini",
    open_source_config: Optional[OpenSourceModelConfig] = None,
) -> Message:
    temporary_memory = dict()
    # init messages with system prompts
    formatted_messages = []
    formatted_messages.append({"role": "system", "content": role_prompt})
    formatted_messages.append({"role": "system", "content": knowledge_prompt})
    
    # format history messages
    if history:
        if len(history) > limit:
            history = history[-limit:] #limit lại {limit=10} messages cuối trong history
        for message in history:
            if message.author == "user":
                formatted_message: ChatCompletionMessageParam = {
                    "role": "user",
                    "content": message.content,
                }
            else:
                formatted_message: ChatCompletionMessageParam = {
                    "role": "assistant",
                    "content": message.content,
                }
            formatted_messages.append(formatted_message)

    formatted_messages.append({"role": "system", "content": constraints_prompt})
    formatted_messages.append({"role": "system", "content": workflow_prompt})
    formatted_messages.append({"role": "system", "content": initialization_prompt})

    try:
        response_text, temporary_memory = gen_openai_answer(
            user_id=user_id,
            thread_id=thread_id,
            messages=formatted_messages,
            tools=tools,
            model=model_name,
            model_type=model_type,
            open_source_config=open_source_config,
        )
    except Exception as e:
        response_text = f"An error occurred: {e}"
    respone_message = Message(
        content=response_text, 
        author="model", 
        metadata={
            **temporary_memory,
            "model_type": model_type,
            "model_name": model_name if model_type == "openai" else open_source_config.model_name if open_source_config else "unknown"
        }
    )
    return respone_message

def gen_answer_for_messenger(
    user_id: UUID,
    thread_id: UUID,
    messages: list[ChatCompletionMessageParam],
    model_type: ModelType = "openai",
    model_name: str = "gpt-4o-mini",
    open_source_config: Optional[OpenSourceModelConfig] = None,
) -> str:
    formatted_messages = []
    formatted_messages.append({"role": "system", "content": role_prompt})
    formatted_messages.append({"role": "system", "content": knowledge_prompt})
    
    for message in messages:
        formatted_messages.append(message)
    
    formatted_messages.append({"role": "system", "content": constraints_prompt})
    formatted_messages.append({"role": "system", "content": workflow_prompt})
    formatted_messages.append({"role": "system", "content": initialization_prompt})

    try:
        response_text, _ = gen_openai_answer(
            user_id=user_id,
            thread_id=thread_id,
            messages=formatted_messages,
            tools=tools,
            model=model_name,
            model_type=model_type,
            open_source_config=open_source_config,
        )
    except Exception as e:
        response_text = f"Đã xảy ra lỗi: {e}"

    return response_text


'''
config = OpenSourceModelConfig(
    url="https://api.your-model-provider.com/v1/chat/completions",
    model_name="llama-3-70b-instruct",
    api_key="your-api-key",
    max_tokens=4096,
    temperature=0.1
)

response = gen_answer(
    user_id=user_id,
    thread_id=thread_id,
    history=history,
    model_type="open_source",
    open_source_config=config
)   
'''

'''
Các model open source phù hợp để so sánh với GPT-4o:
Llama 3 70B - Hỗ trợ function calling và RAG tốt
Mistral Large - Hiệu suất cao, xưng hô tốt trong tiếng Việt
Claude 3 Sonnet - Tốt cho việc tuân thủ hướng dẫn và xưng hô
4. Gemma 2 27B - Model mới của Google, hỗ trợ function calling
Lưu ý: Bạn cần đảm bảo API của model open source hỗ trợ format tương tự OpenAI để function calling hoạt động đúng.
'''