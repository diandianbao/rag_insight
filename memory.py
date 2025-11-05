# from google.adk.sessions import InMemorySessionService
# session_service = InMemorySessionService()
import asyncio
import os
# from google.adk.sessions import DatabaseSessionService
# db_url = "sqlite:///./my_agent_data.db"
# session_service = DatabaseSessionService(db_url=db_url)
#
# print("hello memory")

# 从 Google ADK 导入必要的类
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.sessions import InMemorySessionService, Session
from google.adk.runners import Runner
from google.genai.types import Content, Part

# 配置使用本地Ollama提供的Qwen3-coder:30b模型
# 注意：需要确保Ollama服务正在运行，并且已安装qwen3-coder:30b模型

async def main():
    # 使用LiteLlm正确配置Ollama模型
    # 注意：Ollama的API基础URL应该是 http://localhost:11434 而不是 http://localhost:11434/v1
    greeting_agent = LlmAgent(
       name="Greeter",
       model=LiteLlm(
           model="qwen3-coder:30b",
           api_base="http://localhost:11434",  # 修正API基础URL
           custom_llm_provider="ollama"
       ),
       instruction="Generate a short, friendly greeting.",
       output_key="last_greeting",
    )

    app_name, user_id, session_id = "state_app", "user1", "session1"
    session_service = InMemorySessionService()
    runner = Runner(
       agent=greeting_agent,
       app_name=app_name,
       session_service=session_service
    )

    session = await session_service.create_session(
       app_name=app_name,
       user_id=user_id,
       session_id=session_id
    )

    print(f"Initial state: {session.state}")

    user_message = Content(parts=[Part(text="Hello")])
    print("\n--- Running the agent ---")

    for event in runner.run(
            user_id=user_id,
            session_id=session_id,
            new_message=user_message
    ):
        if event.is_final_response():
            print("Agent responded.")

    updated_session = await session_service.get_session(app_name=app_name, user_id=user_id, session_id=session_id)
    print(f"\nState after agent run: {updated_session.state}")

    sessions = await session_service.list_sessions(app_name=app_name, user_id=user_id)
    for session in sessions:
        print(session)

if __name__ == "__main__":
    asyncio.run(main())
