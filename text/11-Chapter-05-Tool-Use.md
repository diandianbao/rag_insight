# 第五章：工具使用（函数调用）
## Tool Use Pattern Overview | 工具使用模式概述

到目前为止，我们讨论的智能体模式侧重于在大语言模型间协调交互和管理智能体内部的信息流（如提示链、路由、并行化和反思模式）。但如果要让智能体真正有用、能与现实世界或外部系统交互，就必须赋予它们使用工具的能力。

工具使用模式通常通过函数调用（Function Calling）机制实现，使智能体能够与外部 API、数据库、服务交互，甚至直接执行代码。它允许作为智能体核心的大语言模型根据用户请求或当前任务状态，来决定何时以及如何使用特定的外部函数。

这个过程通常包括以下几个步骤：

   <strong>工具定义：</strong>向大语言模型描述外部函数或功能，包括函数的用途、名称，以及所接受参数的类型和说明。

   <strong>大语言模型决策：</strong>大语言模型接收用户的请求和可用的工具定义，并根据对两者的理解判断是否需要调用一个或多个工具来完成请求。

   <strong>生成函数调用：</strong>如果大语言模型决定使用工具，它会生成结构化输出（通常是 JSON 对象），指明要调用的工具名称以及从用户请求中提取的参数。

   <strong>工具执行：</strong>智能体框架或编排层捕获这个结构化输出，识别要调用的工具，并根据给定参数执行相应的外部函数。

   <strong>观察/结果：</strong>工具执行的输出或结果返回给智能体。

   <strong>大语言模型处理（可选，但很常见）：</strong>大语言模型接收工具的输出作为上下文，并用它来生成对用户的最终回复，或决定工作流的下一步（可能涉及调用另一个工具、进行反思或提供最终答案）。

这种模式很关键，因为它突破了大语言模型训练数据的局限，使其能够获取最新信息、执行内部无法处理的计算、访问用户特定的数据，或触发现实世界的动作。函数调用是连接大语言模型推理能力与外部功能的技术桥梁。

虽然「函数调用」这个说法确实能准确描述调用预定义代码函数的过程，但从更广阔的视角理解「工具调用」这一概念更为有益。通过这个更广义的术语，我们看到智能体的能力可以远远超出简单的函数执行。工具可以是传统函数、复杂的 API 接口、数据库请求，甚至是发给另一个智能体的指令。这种视角让我们能够构想更复杂的系统，例如，主智能体可以将复杂的数据分析任务委托给专门的「分析智能体」，或通过 API 查询外部知识库。「工具调用」的思维方式能更好地捕捉智能体作为编排者的全部潜力，使其能够在多样化的数字资源和其他智能生态系统中发挥作用。

LangChain、LangGraph 和 Google ADK 等框架可以很方便地定义工具并将它们集成到智能体工作流中，通常会利用 Gemini 或 OpenAI 等现代大语言模型的原生函数调用功能。在这些框架中，你可以定义工具，并通过设置让智能体识别和使用这些工具。

工具使用是构建强大、可交互且能感知和利用外部资源的智能体的关键模式。

---
## Practical Applications & Use Cases | 实际应用场景

当智能体需要的不只是文本生成，而是执行操作或检索动态信息的时候，工具使用模式几乎都能派上用场。
**1. Information Retrieval from External Sources:** | <strong>从外部来源获取信息：</strong>

获取大语言模型训练数据中未包含的实时数据或信息。

- <strong>用例：</strong>天气信息智能体。
- <strong>工具：</strong>天气查询接口，可输入地点并返回该地的实时天气。
- <strong>智能体流程：</strong>用户提问「伦敦天气怎么样？」，大语言模型识别出需要使用天气工具，并使用「伦敦」作为参数调用该工具，工具返回数据后，大语言模型将这些信息整理并以易懂的方式输出给用户。
**2. Interacting with Databases and APIs:** | <strong>与数据库和接口交互：</strong>

对结构化数据执行查询、更新或其他操作。

- <strong>用例：</strong>电商平台智能体。
- <strong>工具：</strong>通过接口来检查产品库存、查询订单状态或处理支付。
- <strong>智能体流程：</strong>用户提问「产品 X 有货吗？」，大语言模型先调用库存接口，工具返回库存数量后，大语言模型向用户反馈该产品库存情况。
**3. Performing Calculations and Data Analysis:** | <strong>执行计算和数据分析：</strong>

使用计算器、数据分析库或统计工具。

- <strong>用例：</strong>金融领域智能体。
- <strong>工具：</strong>计算器函数、股票行情接口、电子表格工具。
- <strong>智能体流程：</strong>用户提问「苹果公司当前股价是多少？如果我以 150 美元买入 100 股，可能会赚多少钱？」，大语言模型会先调用股票行情接口获取最新价格，然后调用计算器工具计算收益，最后把结果整理并返回给用户。
**4. Sending Communications:** | <strong>发送通知：</strong>

发送电子邮件、消息或调用外部通信服务的接口。

- <strong>用例：</strong>个人助理智能体。
- <strong>工具：</strong>邮件发送接口。
- <strong>智能体流程：</strong>用户说「给约翰发一封关于明天会议的邮件」，大语言模型会从请求中提取收件人、主题和正文，并调用邮件接口发送邮件。
**5. Executing Code:** | <strong>执行代码：</strong>

在受控且安全的环境中运行代码片段以完成特定任务。

- <strong>用例：</strong>编程助理智能体。
- <strong>工具：</strong>代码解释器。
- <strong>智能体流程：</strong>用户提供一段 Python 代码并问「这段代码是做什么的？」，大语言模型会先使用代码解释器运行代码，并据此进行分析和解释。
**6. Controlling Other Systems or Devices:** | <strong>控制其他系统或设备：</strong>

与智能家居设备、物联网平台或其他联网系统交互。

- <strong>用例：</strong>智能家居智能体。
- <strong>工具：</strong>控制智能灯的接口。
- <strong>智能体流程：</strong>用户说「关掉客厅的灯」，大语言模型将带有命令和目标设备信息的请求发送给智能家居工具以执行操作。

工具使用模式将语言模型从文本生成器变成能够在数字或现实世界中感知、推理和行动的智能体（见图 1）。

![Tool Use Examples](/images/chapter05_fig1.jpg)

图 1：智能体使用工具的一些示例

---
## Hands-On Code Example (LangChain) | 实战代码：使用 LangChain

在 LangChain 框架中，使用工具分两个步骤。首先，定义一个或多个工具，通常通过封装现有的 Python 函数或其他可执行组件来完成。随后，将这些工具和大语言模型绑定，这样当大语言模型判断需要调用外部函数来完成用户请求时，就能生成结构化的调用请求并执行相应操作。

以下代码将演示这一原理。首先定义一个简单函数来模拟信息检索工具，然后构建并配置智能体，使其能够利用该工具响应用户输入。运行此示例需要先安装 LangChain 的核心库和相应的模型接入包，并在本地环境中配置好 API 密钥。

# UNCOMMENT
# Prompt the user securely and set API keys as an environment variables
# 安全地提示用户设置 API 密钥作为环境变量

   # A model with function/tool calling capabilities is required.
   # 需要一个具有函数调用能力的模型，这里使用 Gemini 2.0 Flash。

# --- Define a Tool ---
# --- 定义模拟的搜索工具 ---
   # 模拟提供关于特定查询的输出。使用此工具查找类似「法国的首都是哪里？」或「伦敦的天气如何？」这类问题的答案。
   # Simulate a search tool with a dictionary of predefined results.
   # 通过一个字典预定义的结果来模拟搜索工具。

# --- Create a Tool-Calling Agent ---
# --- 创建一个使用工具的智能体 ---
   # This prompt template requires an `agent_scratchpad` placeholder for the agent's internal steps.
   # 这个提示模板需要一个 `agent_scratchpad` 占位符，用于记录智能体的内部步骤。

   # Create the agent, binding the LLM, tools, and prompt together.
   # 使用定义好的大语言模型、工具和提示词模板构建智能体。

   # AgentExecutor is the runtime that invokes the agent and executes the chosen tools.
   # The 'tools' argument is not needed here as they are already bound to the agent.
   # AgentExecutor 负责调用智能体并运行其选择工具的运行时组件。
   # 这里的 'tools' 参数可以不需要了，因为它们已经绑定到智能体上了。

   执行智能体并打印最终输出信息。

   并发运行所有智能体查询任务。

译者注：[Colab 代码](https://colab.research.google.com/drive/1PNsMB2kcCP-iPgpYamG11bGkBiP3QViz#scrollTo=FW3Eh5_OjUea) 已维护在[此处](/codes/Chapter-05-Tool-Use-LangChain-Example.py)，并添加了输出示例。

以上代码使用了 LangChain 库和 Google Gemini 模型构建了一个使用工具的智能体。
首先定义了 <code>search_information</code> 工具，用于模拟检索特定问题的事实答案，比如「伦敦天气怎么样？」、「法国的首都是哪里？」和「地球的人口是多少？」，如果是其他问题就返回一个兜底回复。
接着初始化了一个具备工具调用能力的 <code>ChatGoogleGenerativeAI</code> 模型，并创建了用于引导对话的 <code>ChatPromptTemplate</code>。通过 <code>create_tool_calling_agent</code> 将上述定义的模型、工具和提示组合成智能体，并用 <code>AgentExecutor</code> 负责具体的执行与工具调用任务。
代码中还用异步函数 <code>run_agent_with_tool</code>，用于用指定输入调用智能体，并打印最终输出结果。主异步函数 <code>main</code> 则准备了多条查询，以测试工具 <code>search_information</code> 的输出情况，包括预定义的查询和兜底回复。
执行前代码会检查模型是否成功初始化，最后通过 <code>asyncio.run(main())</code> 启动所有任务。

---
## Hands-On Code Example (CrewAI) | 实战代码：CrewAI

以下代码展示了使用 CrewAI 框架实现函数调用的实际示例。场景很简单：为智能体配备用于查找信息的工具，并通过该智能体和工具来获取模拟的股票价格。

# pip install crewai langchain-openai

# --- Best Practice: Configure Logging ---
# A basic logging setup helps in debugging and tracking the crew's execution.
# --- 最佳实践：配置日志 ---
# 良好的日志设置有助于调试和追踪 crewAI 的执行过程。

# --- Set up your API Key ---
# For production, it's recommended to use a more secure method for key management
# like environment variables loaded at runtime or a secret manager.
# --- 设置你的 API 密钥 ---
# 在生产环境中，推荐使用更安全的密钥管理方法，
# 例如在运行时加载环境变量或使用密钥管理器。
#
# Set the environment variable for your chosen LLM provider (e.g., OPENAI_API_KEY)
# 根据你选择的模型提供商设置环境变量（如 OPENAI_API_KEY）
# os.environ["OPENAI_API_KEY"] = "YOUR_API_KEY"
# os.environ["OPENAI_MODEL_NAME"] = "gpt-4o"

# --- 1. Refactored Tool: Returns Clean Data ---
# The tool now returns raw data (a float) or raises a standard Python error.
# This makes it more reusable and forces the agent to handle outcomes properly.
# --- 1. 重构后的工具 ---
# 该工具现在返回模拟的股价（一个浮点数）或抛出标准的 Python 错误。
# 这样可以提高可重用性，并确保智能体在处理结果时采取适当的处理措施。
    获取指定股票代码的最新模拟股价信息。
    返回该股票的价格（浮点数）。如果找不到该代码，会抛出 ValueError 异常。

        # Raising a specific error is better than returning a string.
        # The agent is equipped to handle exceptions and can decide on the next action.
        # 与其返回一个字符串，不如抛出一个明确的错误，这样更清晰也便于处理。
        # 该智能体具备异常处理能力，能够在发生问题时判断并选择合适的后续动作。

# --- 2. Define the Agent ---
# The agent definition remains the same, but it will now leverage the improved tool.
# --- 2. 定义智能体 ---
# 智能体的定义仍然沿用原有内容，不过现在会使用增强后的工具。
  # Allowing delegation can be useful, but is not necessary for this simple task.
  # 允许委托在某些情况下很有用，但对于这个简单的任务并非必需。

# --- 3. Refined Task: Clearer Instructions and Error Handling ---
# The task description is more specific and guides the agent on how to react
# to both successful data retrieval and potential errors.
# --- 3. 优化后的任务：提供更清晰的指引与更完善的错误处理 ---
# 任务描述更加详尽，能够指导智能体在查询成功和抛出错误时都采取正确的处理。

# --- 4. Formulate the Crew ---
# The crew orchestrates how the agent and task work together.
# --- 4. 构建 Crew 实例 ---
# 由该实例来负责协调智能体和任务。

# --- 5. Run the Crew within a Main Execution Block ---
# Using a __name__ == "__main__": block is a standard Python best practice.
# --- 5. 在主程序中运行 ---
# 使用 __name__ == "__main__": 块是 Python 的最佳实践。
    # Check for API key before starting to avoid runtime errors.
    # 在启动 Crew 之前，检查 OPENAI_API_KEY 环境变量是否已设置。

    # The kickoff method starts the execution.
    # 使用 kickoff 方法启动执行。

译者注：[Colab 代码](https://colab.research.google.com/drive/1TBcatcgnntrm31kfIzENsSMNYwMNLUOh) 已维护在[此处](/codes/Chapter-05-Tool-Use-CrewAI-Example.py)，并添加了输出示例。

以上代码演示了一个使用 Crew.ai 库来模拟金融分析任务的简单应用。
首先定义了工具 <code>get_stock_price</code>，用于模拟查询指定股票代码的价格，当股票代码是预定义的有效代码时返回模拟的价格，如果是其他代码则抛出 <code>ValueError</code> 异常。
接着创建一个名为 <code>financial_analyst_agent</code> 的 Crew.ai 智能体，其被赋予的角色是高级金融分析师，允许使用 <code>get_stock_price</code> 工具进行交互。
随后定义了 <code>analyze_aapl_task</code> 任务，该任务要求智能体使用工具查找苹果（股票代码为 AAPL）的股价，并详细描述了如何处理成功和失败的情形。
然后基于上述的 <code>financial_analyst_agent</code> 智能体和 <code>analyze_aapl_task</code> 任务构建了 <code>Crew</code> 实例，并设置 <code>verbose</code> 为 true 以便在执行期间输出详细日志。
脚本的主体部分在标准的 <code>if __name__ == "__main__":</code> 块内，使用 <code>kickoff()</code> 方法运行 Crew 实例的任务。在启动 Crew 之前，检查 <code>OPENAI_API_KEY</code> 环境变量是否已设置，这是智能体运行所必需的。
Crew 执行的结果最终被打印到控制台。代码中还包括了日志配置，以便能更好地追踪 Crew 的行为和工具调用。它使用环境变量管理 API 密钥，但在生产环境中推荐使用更安全的方法。
简而言之，这个示例展示了如何在 Crew.ai 中定义工具、智能体和任务，以创建协作式的工作流。

---
## Hands-on code (Google ADK) | 实战代码：使用 Google ADK

Google 开发者套件（ADK）内置了丰富的工具，这些工具可以直接整合到智能体中，方便扩展其功能。

<strong>Google 搜索：</strong>Google 搜索工具就是典型的例子，它提供 Google 搜索的接口，可以为智能体提供网络搜索和外部信息检索的功能。

# Define variables required for Session setup and Agent execution
# 定义会话和智能体执行所需的变量

# Define Agent with access to search tool
# 定义一个可以使用搜索功能的智能体
   tools=[google_search] # Google Search is a pre-built tool to perform Google searches. Google Search 是一个内置的工具，用来执行 Google 搜索。

# Agent Interaction
# 智能体调用函数
   辅助函数，传入查询参数调用智能体。

   # Session and Runner
   # 会话和执行器

译者注：[Colab 代码](https://colab.research.google.com/drive/1qFpzmHYomA4vbtuuV1DJrW_cpAZAbY_m) 已维护在[此处](/codes/Chapter-05-Tool-Use-ADK-Example-Google-Search.py)，并添加了输出示例。

以上代码演示了如何使用 Python 版本的 Google ADK 创建一个简单的智能体，该智能体可以通过内置的 Google 搜索工具来回答问题。
首先从 <code>IPython</code>、<code>google.adk</code> 和 <code>google.genai</code> 导入必要的库，并定义应用名称、用户 ID 和会话 ID 等常量。
接着创建一个名为<code>basic_search_agent</code> 的智能体实例，详细描述智能体的功能和指令，同时声明使用 ADK 内预置的 Google 搜索工具。
然后在智能体辅助函数内，先初始化一个 <code>InMemorySessionService</code>（详见第八章）来管理智能体的会话，并使用之前定义的应用、用户和会话 ID 等常量创建新会话。接着创建 <code>Runner</code> 实例，将创建的智能体与上述会话服务连接起来，负责在会话中执行智能体的交互。这个辅助函数 <code>call_agent</code> 封装了向智能体发送查询和处理响应的过程，用户的查询被封装成角色为「user」的 <code>types.Content</code> 对象，该对象和用户 ID、会话 ID 一起传给 <code>runner.run</code> 方法启动执行。该方法随后返回事件列表，代表智能体的行为和响应。代码遍历这些事件以找到最终响应，如果某个事件被识别为最终响应，则提取其文本内容并输出到控制台。
最后代码传入问题「what's the latest ai news?」作为参数调用 <code>call_agent</code> 并来展示智能体的实际运行效果。

<strong>代码执行：</strong>Google ADK 还内置了用于执行动态代码的专门组件。<code>built_in_code_execution</code> 工具为智能体提供 Python 解释器执行的沙箱环境，使模型能够编写并运行代码来完成计算、处理数据和执行脚本。对于需要执行确定性逻辑和精确计算的场景，这个功能非常重要，因为这类问题不是概率性语言生成所能解决的。

# 依赖安装：
# pip install google-adk nest-asyncio python-dotenv

# Define variables required for Session setup and Agent execution
# 定义会话和智能体执行所需的变量

# Agent Definition
# 定义一个可以执行代码的智能体

# Agent Interaction (Async)
# 异步执行智能体

   # Session and Runner
   # 创建会话和执行器

       # Use run_async
       # 使用 run_async 方法异步执行智能体

           # --- Check for specific parts FIRST ---
           # has_specific_part = False
           # 首先检查是否有特定的部分
                       # Access the actual code string via .code
                       # 通过 .code 获取智能体生成的代码
                       # Access outcome and output correctly
                       # 获取代码执行结果并打印输出
                   # Also print any text parts found in any event for debugging
                   # 同时打印其他内容，便于调试
                       # Do not set has_specific_part=True here, as we want the final response logic below
                       # 不要在这里设置 has_specific_part=True，因为我们还想要继续等待最终输出结果

               # --- Check for final response AFTER specific parts ---
               # 然后在特定部分检查之后处理最终结果

# Main async function to run the examples
# 运行示例

# Execute the main async function
# 运行主异步函数以启动程序流程
   # Handle specific error when running asyncio.run in an already running loop (like Jupyter/Colab)
   # 处理在已经运行的循环（如 Jupyter/Colab）中运行 asyncio.run 时的特定错误
       # If in an interactive environment like a notebook, you might need to run:
       # 在交互式环境中（如 Jupyter 笔记本），你可能需要运行：
       # await main()

译者注：[Colab 代码](https://colab.research.google.com/drive/1iF4I_mkV_as0fYoVBuKtf5gfTONEySfK) 已维护在[此处](/codes/Chapter-05-Tool-Use-ADK-Example-Code-Execution.py)，并添加了输出示例。

以上代码演示了如何使用 Google ADK 来创建具有代码执行能力的智能体，它通过编写和执行 Python 代码来解决具体的数学问题。
接着创建一个名为 <code>code_agent</code> 的智能体实例，详细描述智能体的功能和指令，要求它扮演计算器的角色，并可以使用内置的 <code>built_in_code_execution</code> 工具来执行代码。
核心逻辑位于 <code>call_agent_async</code> 函数中，该函数将用户查询发送给智能体的运行器并处理返回的事件。在该函数内部，使用异步循环遍历事件，打印生成的 Python 代码及其执行结果。代码区分了这些中间步骤和包含最终答案的结束事件。
最后，<code>main</code> 函数用两个不同的数学表达式运行智能体，以演示其执行计算的能力。

<strong>企业搜索：</strong>下面这段 Python 代码使用 <code>google.adk</code> 库定义了一个 Google ADK 应用，使用 <code>VSearchAgent</code> 工具搜索 Vertex AI Search 数据来回答问题。
代码先创建了一个名为 <code>q2_strategy_vsearch_agent</code> 的 <code>VSearchAgent</code> 示例，提供详细的描述、使用的模型（gemini-2.0-flash-exp）以及 Vertex AI Search 数据存储的 ID，其中 <code>DATASTORE_ID</code> 需要通过环境变量设置。
接着为智能体设置 <code>Runner</code> 实例，并使用 <code>InMemorySessionService</code> 来管理对话历史。
核心的异步函数 <code>call_vsearch_agent_async</code> 用于与智能体交互，该函数接收查询请求构造为消息对象，并作为参数传给 <code>run_async</code> 方法从而实现将查询请求发送给智能体并等待异步事件返回。
随后该函数以流式方式将智能体的响应输出到控制台，并打印关于最终响应的信息，包括来自数据存储的元数据。代码具备错误处理机制，以捕获智能体执行期间的异常，并提供有价值的上下文信息，如数据存储 ID 不正确或权限缺失等。
另一个异步函数 <code>run_vsearch_example</code> 用于演示如何调用该智能体。主执行块先检查 <code>DATASTORE_ID</code> 是否已设置，然后使用 <code>asyncio.run</code> 运行示例。代码最后还包含一个异常检查，避免在已有运行事件循环的环境（如 Jupyter notebook）中运行代码时出现错误。

# Colab 代码链接：https://colab.research.google.com/drive/1AhF4Jam8wuYMEYU27y22r1uTbixs9MSE

# 依赖安装：
# pip install google-adk nest-asyncio python-dotenv

# --- Configuration ---
# --- 环境变量配置 ---
# Ensure you have set your GOOGLE_API_KEY and DATASTORE_ID environment variables
# 请确认已在环境变量中配置 GOOGLE_API_KEY 和 DATASTORE_ID

# For example:
# os.environ["GOOGLE_API_KEY"] = "YOUR_API_KEY"
# os.environ["DATASTORE_ID"] = "YOUR_DATASTORE_ID"

# --- Application Constants ---
# --- 定义常量 ---

# --- Agent Definition (Updated with the newer model from the guide) ---
# --- 定义一个使用 Vertex AI Search 数据存储的智能体 ---

# --- Runner and Session Initialization ---
# --- 初始化执行器和会话 ---

# --- Agent Invocation Logic ---
# --- 智能体调用逻辑 ---
    初始化会话并使用流式输出智能体的响应。

        # Construct the message content correctly
        # 构造消息对象

        # Process events as they arrive from the asynchronous runner
        # 执行并处理异步事件
            # For token-by-token streaming of the response text
            # 处理流式输出的文本

            # Process the final response and its associated metadata
            # 处理最终输出及其关联的元数据

# --- Run Example ---
# --- 运行示例 ---
    # Replace with a question relevant to YOUR datastore content
    # 请将此处的示例问题替换为与您数据存储内容相关、具体的问题

# --- Execution ---
# --- 执行 ---
            # This handles cases where asyncio.run is called in an environment
            # that already has a running event loop (like a Jupyter notebook).
            # 处理在已经运行的循环（如 Jupyter notebook）中运行 asyncio.run 时的特定错误

译者注：[Colab 代码](https://colab.research.google.com/drive/1AhF4Jam8wuYMEYU27y22r1uTbixs9MSE) 已维护在[此处](/codes/Chapter-05-Tool-Use-ADK-Example-AI-Search.py)。

总结一下，这段代码提供了用于构建对话式 AI 应用的基本框架，该应用通过查询 Vertex AI Search 中的数据来回答问题。示例详细展示了如何定义智能体、配置执行器，以及如何在异步交互中以流式方式接收响应。最终达到了从指定的数据存储中检索信息并将其整合以回答用户提问的目的。

<strong>Vertex 扩展：Vertex AI 扩展是对外部接口的结构化封装，允许模型直接连接外部服务以实现实时数据的处理和操作。扩展提供企业级的安全、数据隐私保护和性能保障，适用于生成与运行代码、查询网站、分析私有数据等场景。Google 提供了诸如代码解释器和 Vertex AI Search 的预置扩展，当然也支持自定义扩展。它们的核心优势是强大的企业控制能力以及与 Google 生态的无缝衔接。与函数调用不同的是，Vertex AI 会自动执行扩展，而函数调用通常需要由用户或客户端来触发和执行。

---
## At a Glance | 要点速览

<strong>问题所在：</strong>大语言模型是强大的文本生成器，但它们本质上与外部世界脱节。它们的知识是静态的，仅限于训练时所用的数据，并且缺乏执行操作或检索实时信息的能力。这种固有的局限性使它们无法完成需要与外部接口、数据库、服务进行交互的任务。如果没有连接这些外部系统的桥梁，它们在解决实际问题的能力将大打折扣。

<strong>解决之道：</strong>工具使用模式（通常通过函数调用机制实现）为这个问题提供了标准化解决方案。它的工作原理是，以大语言模型能理解的方式向其描述可用的外部函数或工具。基于用户请求，具有智能能力的模型可以判断是否需要使用工具，并生成结构化数据对象（如 JSON），指明要调用哪个函数以及使用什么参数。编排层负责执行此函数调用，获取结果，并将其反馈给模型。这使得大语言模型能够将最新的外部信息或操作结果整合到最终响应中，从而有效地赋予了它行动的能力。

<strong>经验法则：</strong>当智能体需要突破大语言模型内部知识局限并与外部世界互动时，就应该使用工具使用模式。这对于需要实时数据（如查询天气、股票价格）、访问私有或专有信息（如查询公司数据库）、执行精确计算、执行代码或在其他系统中触发操作（如发送邮件、控制智能设备）的任务至关重要。
**Visual summary:** | <strong>可视化总结：</strong>

![Tool Use Design Pattern](/images/chapter05_fig2.jpg)

图 2：工具使用模式

---
## Key Takeaways | 核心要点

   工具使用（函数调用）模式使智能体能够与外部系统交互并获取动态信息。

   这包括为工具定义清晰的描述和参数，以便大语言模型能正确使用这些工具。

   大语言模型会决定何时使用工具，并生成结构化的数据以执行这些操作。

   智能体框架负责执行实际的工具调用，并将结果返回给大语言模型。

   工具使用模式对于构建能够执行现实任务并提供最新信息的智能体来说至关重要。

   LangChain 使用 <code>@tool</code> 装饰器简化工具定义，并提供 <code>create_tool_calling_agent</code> 和 <code>AgentExecutor</code> 来构建能够使用工具的智能体。

   Google ADK 提供了多种非常实用的内置工具，比如 Google 搜索、代码执行器和 Vertex AI Search 工具，方便将外部功能直接集成到工作流程中。

---
## Conclusion | 结语

工具使用模式是一种重要的架构原则，用于把大型语言模型的能力扩展到纯文本生成之外。通过让模型能够与外部软件和数据源对接，这一模式使得智能体可以执行操作、完成计算以及从其他系统获取信息。当模型判断需要调用外部工具来满足用户请求时，它会生成一个结构化的调用请求。
像 LangChain、Google ADK 和 Crew AI 这样的框架提供了便于集成外部工具的抽象层和组件，负责向模型暴露工具的定义并解析模型返回的工具调用请求。总体而言，这大大简化了能够在外部数字环境中感知、交互和行动的复杂智能体系统的开发。

---
## References | 参考文献

   LangChain 文档（工具使用）：<https://python.langchain.com/docs/integrations/tools/>

   Google 开发者套件（ADK）文档（工具使用）：<https://google.github.io/adk-docs/tools/>

   OpenAI 函数调用文档：<https://platform.openai.com/docs/guides/function-calling>

   CrewAI 文档（工具使用）：<https://docs.crewai.com/concepts/tools>
