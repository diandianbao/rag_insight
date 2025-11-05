# 第 10 章：模型上下文协议

要让大语言模型（LLM）成为一个高效的智能体，仅具备多模态生成的能力是不够的。还需要能够与外部环境进行交互，比如获取最新的数据信息、使用各种外部软件工具，以及完成特定的操作任务。为此，模型上下文协议（Model Context Protocol，MCP）提供了一个标准化的接口，通过为 LLM 提供与外部资源交互的标准化接口来满足这一需求。该协议是促进一致且可预测集成的关键机制。

## MCP Pattern Overview | MCP 模式概览

想象一下，如果有一个通用适配器，能让任何大语言模型（LLM）轻松接入各种外部系统、数据库或工具，而无需为每个系统单独开发定制集成方案。这正是模型上下文协议（MCP）的核心价值。作为一个开放标准，旨在统一规范化 Gemini、OpenAI GPT 模型、Mixtral 和 Claude 等 主流大语言模型与外部应用程序、数据源和工具之间的通信方式。也可以将它理解为一种通用连接机制，它极大地简化了LLM获取上下文信息、执行操作任务以及与各类系统进行交互的过程。

MCP基于客户端-服务器架构运行。这个协议清晰地定义了MCP服务器如何向外部提供三类核心元素：数据（称为资源）、交互模板（本质上就是提示词）以及可执行功能（称为工具）。这些元素随后会被MCP客户端所使用——这里的客户端可以是承载LLM的应用程序，也可以是AI智能体本身。通过这种标准化的架构设计，MCP极大地简化了将大语言模型集成到各种不同操作环境中的复杂度。

不过需要认识到，MCP本质上是一个「智能体接口」的协议规范，其实际效果很大程度上取决于底层API的设计质量。这里存在一个潜在风险：开发者可能只是简单地将现有的遗留API进行封装，而没有针对智能体的使用场景进行优化改造。举个例子，假如某个票务系统的API只能逐个查询完整的工单详情，那么当智能体需要汇总高优先级工单时，面对大量数据就会变得效率低下且准确率不高。
为了让智能体真正发挥效能，底层API需要进行针对性的改进，增加诸如过滤、排序等确定性功能，这样才能帮助非确定性的智能体更高效地工作。这个例子很好地说明了一个重要观点：智能体并不能神奇地取代传统的确定性工作流程；相反，它们往往需要更强大的确定性基础设施支持才能取得成功。

还需要注意的是，MCP虽然能够封装各种API，但这些API的输入输出格式可能仍然超出智能体的固有理解范围。一个API要真正有用，其数据格式必须对智能体友好——这一点MCP协议本身是无法强制保证的。
举个具体的例子：如果你为文档存储系统创建了一个MCP服务器，但它返回的都是PDF格式的文件，而使用这个服务的智能体并不具备解析PDF内容的能力，那么这样的设计基本上就失去了意义。更好的做法是，首先构建一个能够返回文档文本版本（比如Markdown格式）的API，这样智能体才能真正读取并处理其中的内容。这个例子很好地说明了一个重要原则：开发者在设计MCP集成时，不能只关注连接机制的实现，更需要深入考虑数据交换的实质内容，只有这样才能确保真正的兼容性和实用性。

## MCP vs. Tool Function Calling | MCP 与工具函数调用

模型上下文协议（MCP）与工具函数调用是两种不同的技术机制，它们都能够让大语言模型与外部能力（包括各类工具）进行交互并执行具体操作。尽管这两种技术都致力于扩展LLM的能力边界，使其不再局限于单纯的文本生成，但它们在实现方法和抽象层级上存在着显著差异。

工具函数调用本质上可以理解为大语言模型向特定预定义工具或功能发出的直接调用请求。需要说明的是，在这个技术语境下，「工具」和「函数」这两个术语通常可以互换使用，指的是同一类可执行的外部能力。这种交互模式的核心特征在于其一对一的通信架构：LLM首先基于对用户意图的深度理解（特别是那些需要借助外部能力才能完成的请求），按照既定格式构造调用请求；随后，应用程序代码接收并执行这个请求，最终将执行结果返回给LLM进行处理。当前工具函数调用的具体实现机制往往是各个LLM平台厂商的专有技术方案，不同提供商之间的实现方式和接口规范存在着明显的差异性和不兼容性。

相比之下，模型上下文协议（MCP）作为标准化接口运作，使LLM能够发现、通信和利用外部能力。它作为开放协议，促进与广泛工具和系统的交互，旨在建立生态系统，让任何兼容工具都可以被任何兼容LLM访问。这促进了不同系统和实现之间的互操作性、可组合性和可重用性。
通过采用联邦模型，显著提高了互操作性并释放了现有资产的价值。这一策略允许仅通过将异构和遗留服务封装在符合MCP的接口中，就能将它们带入现代生态系统。这些服务继续独立运行，但现在可以被组合成新的应用程序和工作流，其协作由LLM编排。这在不需要对基础系统进行昂贵重写的情况下促进了敏捷性和可重用性。

以下是 MCP 与工具函数调用之间基本区别的详细分析：

| 特性       | 工具函数调用                                    | 模型上下文协议（MCP）                           |
标准化程度
功能范围
系统架构
发现机制
可复用性

可以将工具函数调用类比为一套为 AI 专门定制的工具，比如特定的扳手和螺丝刀。这种方案对于执行固定任务集合的工作环境来说十分高效。相比之下，模型上下文协议（MCP）则类似于建立一套通用化、标准化的电源接口系统。MCP本身并不直接提供具体工具，而是构建了一个开放的基础设施——允许任何厂商生产的兼容设备都能接入并正常工作，从而打造出一个能够动态扩展、持续演进的工作生态体系。

简而言之，函数调用提供对有限特定功能的直接访问权限，而MCP则构建了一个标准化的通信框架，使LLM能够发现并利用广泛的外部资源生态系统。对于功能需求简单的应用场景，专用工具集已经足够满足要求；但对于需要高度适应性、具备复杂互联特性的AI系统而言，采用MCP这样的通用标准协议是构建可持续演进架构的必备基础。

## Additional considerations for MCP | MCP 的其他考虑因素

虽然 MCP 框架提供了强大的功能，但要在特定场景中充分评估其适用性，我们还需要考虑几个关键因素。让我们来详细了解一下这些方面：

- <strong>工具 vs. 资源 vs. 提示词：</strong>理解这些组件各自的角色很关键。资源指的是静态数据（比如 PDF 文件或数据库记录），工具则是可以执行操作的功能（比如发送邮件或调用 API），而提示词就像是指导 LLM 如何与资源或工具进行交互的模板，确保整个交互过程既规范又高效。
- <strong>可发现性：</strong>MCP 的一大亮点在于，客户端能够实时查询服务器，动态了解它提供了哪些工具和资源。这种"即用即发现"的机制特别适合那些需要灵活适应新功能而无需重新部署的智能体。
- <strong>安全性：</strong>无论通过什么协议来开放工具和数据，都需要有完善的安全保障。MCP 的实现必须包含身份验证和权限控制，确保只有特定的客户端才能访问相应的服务器，并且明确限定它们可以执行的操作范围。
- <strong>实现：</strong>虽尽管 MCP 是一个开放标准，但实际落地可能会比较复杂。好在现在有一些厂商正在努力简化这个过程，比如 Anthropic 和 FastMCP 这样的模型提供商都推出了 SDK，帮开发者处理了大量的模板代码，让创建和连接 MCP 客户端与服务器变得更加轻松。
- <strong>错误处理：</strong>一套完善的错误处理机制非常重要。协议需要明确规定如何将各种错误情况（比如工具执行失败、服务器无法连接或者请求格式有误）清晰地反馈给 LLM，这样它才能理解问题所在，并尝试其他的解决方案。
- <strong>本地 vs. 远程服务器：</strong>MCP 服务器既可以部署在智能体所在的本地机器上，也可以放在远程服务器中。选择本地部署通常是为了追求更快的响应速度和更好地保护敏感数据；而远程架构则更适合需要在整个组织内共享工具资源，并且能够弹性扩展的场景。
- <strong>按需 vs. 批处理：</strong>MCP 既支持实时交互的按需调用，也能应对大规模的批量处理。具体选择哪种方式要看实际应用需求——可能是需要即时反馈的对话型智能体，也可能是对数据记录进行批处理的分析流程。
- <strong>传输机制：</strong>MCP 既支持实时交互的按需调用，也能应对大规模的批量处理。具体选择哪种方式要看实际应用需求——可能是需要即时反馈的对话型智能体，也可能是对数据记录进行批处理的分析流程。

模型上下文协议使用客户端-服务器模型来标准化信息流。理解组件交互是理解 MCP 高级智能体行为的关键：

   <strong>大语言模型（LLM）：</strong>作为整个系统的智能核心，它负责处理用户请求、制定执行计划，并判断何时需要调用外部资源或执行具体操作。

   <strong>MCP 客户端：</strong>这是围绕 LLM 构建的一层应用或封装，扮演着中间人的角色——将 LLM 的意图转化为符合 MCP 标准的规范化请求。它的主要职责包括发现可用的 MCP 服务器、建立连接并维护通信。

   <strong>MCP 服务器：</strong>相当于通往外部世界的桥梁，向经过授权的 MCP 客户端开放一系列工具、资源和提示模板。每个服务器通常专注于某个特定领域，比如对接企业内部的数据库系统、邮件服务平台或者公共 API 接口。

   <strong>可选第三方（3P）服务：</strong>这些是 MCP 服务器实际管理和对接的外部工具、应用或数据源，也是最终执行具体操作的终端。无论是查询专有数据库、与 SaaS 平台进行交互，还是调用天气 API 获取实时数据，都是通过这些第三方服务来完成的。

交互流程如下：

   <strong>发现阶段：</strong>MCP 客户端会代表 LLM 去查询 MCP 服务器，了解它具体提供哪些能力。服务器会返回一份清单，详细列出可用的工具（例如 <code>send_email</code>）、资源（例如 <code>customer_database</code>）和提示词。

   <strong>请求构建：</strong> LLM 根据需求决定要使用哪个工具，比如说想要发送邮件。它会构建一个具体的请求，明确指定要调用的工具（<code>send_email</code>）以及必要的参数信息（收件人、邮件主题、正文内容等）。

   <strong>客户端通信：</strong>MCP 客户端拿到 LLM 构建好的请求后，会按照标准格式将这个调用请求发送给对应的 MCP 服务器。

   <strong>服务器执行：</strong>MCP 服务器收到请求后，会先进行客户端身份验证和请求合法性检查，确认无误后才会通过底层软件接口（比如调用邮件 API 的 <code>send()</code> 函数）来执行具体的操作。

   <strong>响应和上下文更新：</strong>操作执行完成后，MCP 服务器会按照标准格式将响应结果返回给 MCP 客户端。这个响应会告诉客户端操作是否成功，并附带相关的输出信息（比如发送邮件后得到的确认编号）。客户端随后将这些结果反馈给 LLM，帮助它更新当前的任务上下文，为下一步操作做好准备。

## Practical Applications & Use Cases | 实际应用与案例

MCP 极大地扩展了 AI 和大语言模型的能力边界，让它们变得更加灵活强大。以下是九个典型的应用场景：

- <strong>数据库集成：</strong>通过 MCP，LLM 和智能体能够轻松对接数据库中的结构化数据并进行交互。比如借助 MCP 数据库工具箱，智能体可以直接用自然语言指令来查询 Google BigQuery 数据集，实时获取信息、生成报表或者更新记录。
- <strong>生成式媒体编排：</strong>MCP 让智能体能够整合各类先进的生成式媒体服务。通过 MCP 媒体生成工具，智能体可以协调整个工作流程——调用 Google Imagen 生成图片、使用 Google Veo 制作视频、通过 Google Chirp 3 HD 合成逼真语音、或者利用 Google Lyria 创作音乐，为 AI 应用带来动态内容创作能力。
- <strong>外部 API 交互：</strong>MCP 为 LLM 提供了一套标准化的方式来调用外部 API 并接收响应。这意味着智能体不仅可以获取实时天气、查询股价、发送邮件，还能与 CRM 系统等业务平台对接，大大扩展了其核心语言模型之外的能力范围。
- <strong>基于推理的信息提取：</strong>借助 LLM 强大的推理能力，MCP 实现了比传统搜索检索更高效的信息提取方式。不同于简单返回整篇文档的传统搜索，智能体能够深入分析文本内容，精准提取出直接回答用户复杂问题的具体条款、数据或关键陈述。
- <strong>自定义工具开发：</strong> 开发者可以基于实际需求构建专属工具，并通过 MCP 服务器（比如使用 FastMCP）对外开放。这样就能把企业内部的专业功能或私有系统以标准化、易用的方式提供给 LLM 和各种智能体，无需对 LLM 本身进行任何修改。
- <strong>标准化通信桥梁：</strong>MCP 在 LLM 和应用程序之间建立了一个统一的通信层，不仅降低了系统集成的复杂度，还促进了不同 LLM 提供商和应用平台之间的互操作性，让开发复杂的智能体系统变得更加简单高效。
- <strong>复杂工作流编排：</strong>通过整合多个 MCP 开放的工具和数据源，智能体能够协调执行高度复杂的多步骤工作流程。例如，它可以从数据库提取客户信息，自动生成个性化的营销图片，撰写定制化的邮件内容，最后完成发送——整个过程通过调用不同的 MCP 服务来实现。
- <strong>物联网设备控制：</strong> MCP 还可以帮助 LLM 与物联网设备进行交互。智能体能够通过 MCP 向智能家居设备、工业传感器或机器人发送控制指令，实现对物理系统的自然语言控制和自动化管理。
- <strong>金融服务自动化：</strong>在金融领域，MCP 让 LLM 能够对接各种金融数据源、交易平台和合规系统。智能体可以分析市场行情、执行交易指令、提供个性化的理财建议，或者自动完成监管报表，同时确保所有通信都符合安全标准和规范要求。

简而言之，模型上下文协议（MCP）让智能体能够实时获取来自数据库、API 和网络资源的信息，还能够通过整合处理多方数据来执行发送邮件、更新记录、控制设备、完成复杂任务等操作。此外，MCP 还支持各类媒体生成工具，为 AI 应用提供更丰富的能力支撑。

## Hands-On Code Example with ADK | 使用 ADK 的实战代码示例

本节内容概述了如何连接到提供文件系统操作的本地 MCP 服务器，让 ADK 智能体能够和本地文件系统进行交互。
### Agent Setup with MCPToolset | 使用 MCPToolset 设置智能体

想要让智能体具备文件系统交互能力，需要先创建一个 <code>agent.py</code> 文件（例如在 <code>./adk_agent_samples/mcp_agent/agent.py</code>）。<code>MCPToolset</code> 在 <code>LlmAgent</code> 对象的 <code>tools</code> 列表中实例化。这里有个特别需要注意的地方：记得把 <code>args</code> 列表里的 <code>"/path/to/your/folder"</code> 替换成你本地系统上一个真实存在的目录绝对路径，而且要确保 MCP 服务器有权限访问这个目录。这个目录会作为智能体进行文件操作时的根目录。

# Create a reliable absolute path to a folder named 'mcp_managed_files'
# within the same directory as this agent script.
# This ensures the agent works out-of-the-box for demonstration.
# For production, you would point this to a more persistent and secure location.

# Ensure the target directory exists before the agent needs it.

                   # This MUST be an absolute path to a folder.
           # Optional: You can filter which tools from the MCP server are exposed.
           # For example, to only allow reading:
           # tool_filter=['list_directory', 'read_file']

<code>npx</code>（（Node Package Execute）是随着 npm（Node Package Manager）5.2.0 及更高版本一起提供的一个实用工具，它让我们能够直接运行 npm registry 里的 Node.js 包，省去了全局安装的麻烦。本质上，<code>npx</code> 就是一个 npm 包的运行器，现在很多社区开发的 MCP 服务器都是以 Node.js 包的形式发布的。

为了让智能体开发套件（ADK）能够正确识别 <code>agent.py</code> 文件作为可发现的 Python 包，我们需要创建一个 <code>__init__.py</code> 文件。这个文件需要和 <code>agent.py</code>  放在同一个目录下。

当然，还有其他支持的命令可供使用。例如，可以按如下方式连接到 <code>python3</code>：

在 Python 上下文中，UVX 是一个很实用的命令行工具，它借助 uv 这个工具来创建临时的、隔离的 Python 环境并执行命令。本质上，你可以在不进行全局安装或者污染项目环境的情况下，直接运行各种 Python 工具和第三方包。而且你可以通过 MCP 服务器来调用它。

MCP 服务器搭建完成之后，下一步就是建立连接了。
### Connecting the MCP Server with ADK Web | 使用 ADK Web 连接 MCP 服务器

首先，执行「adk web」。在终端中导航到 <code>mcp_agent</code> 的父目录（例如 <code>adk_agent_samples</code>）并运行：

等浏览器里显示出 ADK Web 的操作界面后，从智能体菜单里选择 <code>filesystem_assistant_agent</code>。接下来你可以试试下面这些指令：

- 「显示此文件夹的内容。」
- 「读取 <code>sample.txt</code> 文件。」（假设 <code>sample.txt</code> 位于 <code>TARGET_FOLDER_PATH</code>。）
- 「<code>another_file.md</code> 里有什么？」

## Creating an MCP Server with FastMCP | 使用 FastMCP 创建 MCP 服务器

FastMCP 是一个专门为简化 MCP 服务器开发而设计的高级 Python 框架。它通过提供抽象层来封装协议的复杂性，让开发者能够把精力集中在核心业务逻辑上。

这个库最大的特点是可以用简单的 Python 装饰器来快速定义工具、资源和提示模板。特别值得一提的是它的自动模式生成功能——它会智能地解析 Python 函数的签名、类型注解和文档字符串，自动生成 AI 模型所需的接口规范。这种自动化机制大大减少了手动配置的工作量，也降低了出错的可能性。

除了基础的工具创建功能，FastMCP 还支持像服务器组合和代理这样的高级架构模式。这意味着你可以用模块化的方式开发复杂的多组件系统，还能把现有的服务无缝对接到 AI 可访问的框架里。另外，FastMCP 还内置了对高效、分布式、可扩展的 AI 驱动应用的优化支持。
### Server setup with FastMCP | 使用 FastMCP 设置服务器

举个简单的例子，假设服务器提供了一个基础的「问候」功能。等服务器启动运行后，ADK 智能体和其他 MCP 客户端就能通过 HTTP 协议来调用这个功能了。

# This script demonstrates how to create a simple MCP server using FastMCP.
# It exposes a single tool that generates a greeting.

# 1. Make sure you have FastMCP installed:
# pip install fastmcp

# Initialize the FastMCP server.

# Define a simple tool function.
# The `@mcp_server.tool` decorator registers this Python function as an MCP tool.
# The docstring becomes the tool's description for the LLM.

# Or if you want to run it from the script:

这个 Python 脚本里定义了一个叫做 <code>greet</code> 的单一函数，它的作用是根据人名生成个性化的问候语。在函数上面加的 <code>@tool()</code> 装饰器很巧妙，它能自动把这个函数注册成 AI 或其他程序可以调用的工具。FastMCP 会利用函数的文档字符串和类型注解，自动告诉智能体这个工具该怎么用、需要什么参数、会返回什么结果。

当我们运行这个脚本的时候，它会启动一个 FastMCP 服务器，这个服务器会在 localhost:8000 这个地址监听请求。这样一来， <code>greet</code> 函数就变成了一个可以通过网络访问的服务。我们可以配置智能体连接到这个服务器，在完成更复杂任务的过程中调用这个问候功能。服务器会一直运行，直到我们手动把它停掉。
### Consuming the FastMCP Server with an ADK Agent | 使用 ADK 智能体连接 FastMCP 服务器

我们可以把 ADK 智能体配置成 MCP 客户端，让它能够使用正在运行的 FastMCP 服务器。具体做法是用 FastMCP 服务器的网络地址（通常是[http://localhost:8000。](http://localhost:8000。/)）来设置 <code>HttpServerParameters</code> 

还可以加上 <code>tool_filter</code> 这样就能限制智能体只能使用服务器提供的特定工具，比如只让它用<code>greet</code>这个问候功能。当用户发出"问候 John Doe"这样的请求时，智能体内置的大语言模型会识别到通过 MCP 可用的 <code>greet</code>工具，然后用"John Doe"作为参数去调用它，最后把服务器的响应返回给用户。这个过程很好地展示了如何把通过 MCP 暴露的自定义工具集成到 ADK 智能体里。

要实现这样的配置，我们需要准备一个智能体配置文件（比如放在 <code>./adk_agent_samples/fastmcp_client_agent/</code> 目录下的  <code>agent.py</code>）。这个文件会创建一个 ADK 智能体实例，并通过 <code>HttpServerParameters</code> 来和正在运行的 FastMCP 服务器建立连接。

# Define the FastMCP server's address.
# Make sure your fastmcp_server.py (defined previously) is running on this port.

           # Optional: Filter which tools from the MCP server are exposed
           # For this example, we're expecting only 'greet'

该脚本定义了一个名为 <code>fastmcp_greeter_agent</code> 的智能体，它基于 Gemini 语言模型。我们给它的设定是一个友好的助手，专门负责问候别人。最关键的是，代码为这个智能体配备了执行任务所需的工具——它配置了  <code>MCPToolset</code> 来连接到运行在 localhost:8000 的独立服务器，也就是我们之前示例中的那个 FastMCP 服务器。智能体被特别授权可以使用该服务器上的  <code>greet</code> 问候工具。简单来说，这段代码搭建了整个系统的客户端部分，创建了一个既明白自己任务是问候别人，又清楚该用哪个外部工具来完成任务的智能体。

记得要在 <code>fastmcp_client_agent</code> 目录下创建一个 <code>**init**.py</code> 文件，这样才能让 ADK 把这个智能体识别为一个可发现的 Python 包。

具体操作步骤是：先新开一个终端窗口，运行  <code>python fastmcp_server.py</code> 启动 FastMCP 服务器。然后回到终端，进入 <code>fastmcp_client_agent</code> 的上级目录（例如 <code>adk_agent_samples</code>），执行 <code>adk web</code>命令。等浏览器里显示出 ADK Web 界面后，从智能体菜单里选择 <code>fastmcp_greeter_agent</code>。这时候你就可以测试了，输入"问候 John Doe"这样的指令，智能体就会调用 FastMCP 服务器上的 <code>greet</code> 工具来生成回应。

## At a Glance | 要点速览

<strong>问题所在：</strong>要让大语言模型真正成为有效的智能体，它们不能只停留在文本生成层面，还需要具备与外部环境交互的能力——既能获取实时数据，又能调用外部软件。如果没有统一的通信标准，每次把大语言模型和外部工具或数据源对接都要从头定制开发，既复杂又难以复用。这种临时凑合的做法严重限制了系统的扩展性，也让构建复杂互联的 AI 系统变得异常困难和低效。

<strong>解决之道：</strong>模型上下文协议（MCP）提供了一个标准化的解决方案，它就像是大语言模型和外部系统之间的通用接口。这个开放的标准化协议明确定义了如何发现和使用外部能力。MCP 采用客户端-服务器架构，让服务器能够向所有兼容的客户端提供工具、数据资源和交互提示。由大语言模型驱动的应用作为客户端，可以按需发现并使用这些资源，整个过程都是可预测的。这种标准化方式促成了一个可互操作、可复用组件的生态系统，大大简化了复杂智能体工作流的开发难度。

<strong>经验法则：</strong>当你需要构建复杂、可扩展的企业级智能体系统，而且这些系统要和各种各样的外部工具、数据源、API 打交道时，就应该考虑使用 MCP 协议。特别是在不同大语言模型和工具之间的互操作性很重要，或者智能体需要动态发现新功能而不用重新部署的情况下，MCP 是最佳选择。但如果你的应用比较简单，只需要调用有限几个固定功能，那直接用工具函数调用可能就够用了。

<strong>可视化总结</strong>

![image-20251021100220540](C:\Users\TAO\AppData\Roaming\Typora\typora-user-images\image-20251021100220540.png)

<strong>图 1：</strong>模型上下文协议

## Key Takeaways | 核心要点

以下是核心要点：

- 模型上下文协议（MCP）是一个开放标准，它为大语言模型和外部应用、数据源、工具之间的通信提供了统一的规范。
- 这个协议采用客户端-服务器架构，明确定义了如何对外提供和使用各种资源、提示模板和工具。
- 智能体开发套件（ADK）既支持连接现有的 MCP 服务器，也支持把 ADK 里的工具通过 MCP 服务器对外提供。
- FastMCP 这个框架让 MCP 服务器的开发和管理变得更简单，特别适合把用 Python 写的工具封装成服务。
- 通过 MCP Tools for Genmedia Services，智能体可以很方便地调用 Google Cloud 的各种生成式媒体能力，比如 Imagen、Veo、Chirp 3 HD 和 Lyria。
- MCP 让大语言模型和智能体不再局限于文本生成，而是能够真正与现实世界系统交互，获取动态信息，执行具体操作。

## Conclusion | 结语

模型上下文协议（MCP）是一个开放标准，它为大语言模型和外部系统之间的通信提供了一套通用规范。这个协议采用客户端-服务器架构，使 LLM 能够通过标准化工具访问资源、利用提示词并执行操作。MCP 允许 LLM 与数据库交互、管理生成式媒体工作流、控制物联网设备以及自动化金融服务。实际示例演示了设置智能体与 MCP 服务器通信，包括文件系统服务器和使用 FastMCP 构建的服务器，说明了其与智能体开发套件（ADK）的集成。MCP 是开发扩展到基本语言能力之外的交互式 AI 智能体的关键组件。

## References | 参考文献

1. 模型上下文协议（MCP）文档（最新）。模型上下文协议（MCP）。https://google.github.io/adk-docs/mcp/

2. FastMCP 文档。FastMCP。https://github.com/jlowin/fastmcp

3. MCP Tools for Genmedia Services。MCP Tools for Genmedia Services。https://google.github.io/adk-docs/mcp/#mcp-servers-for-google-cloud-genmedia

4. MCP Toolbox for Databases 文档。（最新）。MCP Toolbox for Databases。https://google.github.io/adk-docs/mcp/databases/