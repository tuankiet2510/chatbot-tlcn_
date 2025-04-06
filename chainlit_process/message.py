from uuid import UUID #handle unique ID
import chainlit as cl
from models.message import Message
from service.store_chatbot import gen_answer

#decorator chainlit handle new message from user
@cl.on_message
async def main(message: cl.Message):
    conversation = cl.chat_context.get() #get context chat message
    message.author = "user"
    user_id = UUID(cl.context.session.user.metadata["user_id"])  # type: ignore
    thread_id = UUID(cl.context.session.thread_id) # chat session
    conversation = [
        Message(content=msg.content, author=msg.author) for msg in conversation
    ]
    print("User ID:", user_id)
    print("Thread ID:", thread_id)
    # gen response and send to chainlit UI
    return (
        await gen_answer(user_id, thread_id, conversation).to_chainlit_message().send()
    )

# decorator handle 1 chat được khôi phục
@cl.on_chat_resume
async def on_chat_resume(thread: cl.types.ThreadDict):
    pass
