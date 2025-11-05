import time
from google.adk.tools.tool_context import ToolContext
from google.adk.sessions import InMemorySessionService


# --- 定义推荐的基于工具的方法 ---
def log_user_login(tool_context: ToolContext) -> dict:
    """
    在用户登录事件时更新会话状态。
    此工具封装了与用户登录相关的所有状态更改。
    参数：
        tool_context：由 ADK 自动提供，提供对会话状态的访问。
    返回：
        确认操作成功的字典。
    """
    # 通过提供的上下文直接访问状态。
    state = tool_context.state

    # 获取当前值或默认值，然后更新状态。
    # 这样更清晰，并且将逻辑集中在一起。
    login_count = state.get("user:login_count", 0) + 1
    state["user:login_count"] = login_count
    state["task_status"] = "active"
    state["user:last_login_ts"] = time.time()
    state["temp:validation_needed"] = True

    print("State updated from within the `log_user_login` tool.")

    return {
        "status": "success",
        "message": f"User login tracked. Total logins: {login_count}."
    }

# --- 使用演示 ---
# 在实际应用中，LLM 智能体会决定调用此工具。
# 在这里，我们模拟直接调用以进行演示。
# 1. 设置

async def main():
    session_service = InMemorySessionService()
    app_name, user_id, session_id = "state_app_tool", "user3", "session3"
    session = await session_service.create_session(
       app_name=app_name,
       user_id=user_id,
       session_id=session_id,
       state={"user:login_count": 0, "task_status": "idle"}
    )
    print(f"Initial state: {session.state}")

    # 2. 模拟工具调用（在实际应用中，ADK Runner 执行此操作）
    # 我们手动创建一个 ToolContext 仅用于此示例。
    from google.adk.tools.tool_context import InvocationContext
    mock_context = ToolContext(
       invocation_context=InvocationContext(session=session, session_service=session_service, invocation_id=session_id)
    )

    # 3. 执行工具
    log_user_login(mock_context)

    # 4. 检查更新后的状态
    updated_session = await session_service.get_session(app_name=app_name, user_id=user_id, session_id=session_id)
    print(f"State after tool execution: {updated_session.state}")

