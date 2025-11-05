# 第 15 章: 智能体间通信 (A2A)

单个 AI 智能体在处理复杂、多方面的问题时, 即使能力很强, 也常常面临局限性。为了克服这一挑战, 智能体间通信 (Inter-Agent Communication, A2A) 使基于不同框架构建的 AI 智能体能够有效协作。这种协作涉及无缝的协调、任务委派和信息交换。Google 的 A2A 协议是旨在促进这种通用通信的开放标准。本章将探讨 A2A、其实际应用及其在 Google ADK 中的实现。
## Inter-Agent Communication Pattern Overview ｜ 智能体间通信模式概述

Agent2Agent (A2A) 协议是旨在实现不同 AI 智能体框架之间通信与协作的开放标准。它确保了互操作性, 允许使用 LangGraph、CrewAI 或 Google ADK 等技术开发的 AI 智能体协同工作, 而不受其来源或框架差异的影响。A2A 得到了众多技术公司和服务提供商的支持, 包括 Atlassian、Box、LangChain、MongoDB、Salesforce、SAP 和 ServiceNow。Microsoft 计划将 A2A 集成到 Azure AI Foundry 和 Copilot Studio 中, 表明了其对开放协议的承诺。此外, Auth0 和 SAP 正在将 A2A 支持集成到其平台和智能体中。作为开源协议, A2A 欢迎社区贡献, 以促进其发展和广泛采用。
## Core Concepts of A2A ｜ A2A 的核心概念

A2A 协议为智能体交互提供了结构化方法, 建立在几个核心概念之上。深入理解这些概念对于开发或集成 A2A 兼容系统至关重要。A2A 的基础组成部分包括核心参与者、智能体卡片、智能体发现、通信与任务、交互机制以及安全性, 接下来将对这些核心组成部分进行详细介绍。
### Core Actors ｜ 核心参与者

核心参与者: A2A 涉及三个主要实体:

-  用户 (User): 发起智能体协助请求。

- A2A 客户端 (客户端智能体): 代表用户请求操作或信息的应用程序或 AI 智能体。

- A2A 服务器 (远程智能体): 提供 HTTP 端点以处理客户端请求并返回结果的 AI 智能体或系统。远程智能体作为「不透明」系统运行, 这意味着客户端无需了解其内部操作细节。

### Agent Card
智能体卡片

智能体卡片: 智能体的数字身份由其智能体卡片 (Agent Card) 定义, 通常是 JSON 文件。该文件包含用于客户端交互和自动发现的关键信息, 包括智能体的身份、端点 URL 和版本。它还详细说明了支持的功能 (如流式传输或推送通知)、特定技能、默认输入/输出模式以及身份验证要求。以下是 WeatherBot 的智能体卡片示例。

### Agent discovery | 智能体发现

智能体发现 (Agent discovery): 它允许客户端找到描述可用 A2A 服务器能力的智能体卡片。此过程存在多种策略:

Well-Known URI: 智能体在标准化路径 (例如/.well-known/agent.json) 上托管其智能体卡片。这种方法为公共或特定领域的使用提供了广泛且通常是自动化的可访问性。

托管注册中心 (Curated Registries): 这些注册中心提供了一个集中的目录, 智能体卡片在此发布, 并可根据特定标准进行查询。这非常适合需要集中管理和访问控制的企业环境。

直接配置 (Direct Configuration): 智能体卡片信息被嵌入或私下共享。此方法适用于动态发现不那么重要的紧密耦合或私有系统。

无论选择哪种方法, 保护智能体卡片端点都很重要。这可以通过访问控制、双向 TLS (mutual TLS, mTLS) 或网络限制来实现, 特别是当卡片包含敏感 (尽管非机密) 信息时。
## Communications and Tasks | 通信与任务

在 A2A 框架中, 通信围绕异步任务构建, 异步任务是长时间运行流程的基本工作单元。每个任务都被分配唯一标识符, 并经历一系列状态——例如已提交、处理中或已完成——这种设计支持复杂操作中的并行处理。智能体之间的通信通过消息 (Message) 进行。

消息包含 <code>attributes</code> 和一个或多个 <code>part</code>。<code>attributes</code> 是描述消息的键值元数据, 如其优先级或创建时间。<code>part</code> 承载实际交付的内容, 如纯文本、文件或结构化 JSON 数据。智能体在任务期间生成的具体输出被称为 <code>artifacts</code>。与消息类似, <code>artifacts</code> 也由一个或多个部分组成, 并且可以在结果可用时以增量方式流式传输。A2A 框架内的所有通信都通过 HTTP(S) 进行, 并使用 JSON-RPC 2.0 协议作为负载。为了在多次交互中保持连续性, 使用服务器生成的 <code>contextId</code> 来对相关任务进行分组并保留上下文。
## Interaction Mechanisms | 交互机制

A2A 提供了多种交互方法以适应各种 AI 应用需求, 每种方法都有其独特的机制:

- 同步请求/响应: 用于快速、即时的操作。在这种模型中, 客户端发送请求并主动等待服务器处理, 服务器在单个同步交换中返回完整响应。
- 异步轮询: 适用于需要较长时间处理的任务。客户端发送一个请求, 服务器立即以 “处理中” 状态和任务 ID 进行确认。然后客户端可以自由执行其他操作, 并可以通过发送新请求定期轮询服务器以检查任务状态, 直到任务被标记为 “已完成” 或 “失败”。
- 流式更新 (服务器发送事件-SSE): 非常适合接收实时、增量的结果。此方法建立了一个从服务器到客户端的持久性单向连接。它允许远程智能体持续推送更新, 例如状态变更或部分结果, 而无需客户端发出多个请求。
- 推送通知 (Webhooks): 专为运行时间很长或资源密集型的任务设计, 在这些任务中维持长连接或频繁轮询效率低。客户端可以注册 webhook URL, 当任务状态发生重大变化 (例如完成时), 服务器将向该 URL 发送异步通知 (「推送」)。

智能体卡片指定了智能体是否支持流式传输或推送通知功能。此外, A2A 是模态无关 (modality-agnostic) 的, 这意味着它不仅可以提供文本的交互模式, 还可以支持音频和视频等其他数据类型, 从而实现丰富的多模态 AI 应用。流式传输和推送通知功能都在智能体卡片中指定。

# 同步请求示例

同步请求示例使用 <code>sendTask</code> 方法, 客户端发起请求并期望得到单一、完整的响应。相比之下, 流式请求使用 <code>sendTaskSubscribe</code> 方法建立持久连接, 允许智能体随时间推移发回多个增量更新或部分结果。

# 流式请求示例
## Security | 安全性

智能体间通信 (A2A): 智能体间通信 (A2A) 是系统架构的重要组成部分, 它实现了智能体之间安全、无缝的数据交换。通过多种内置机制, 它确保了系统的稳健性和完整性。

双向传输层安全 (TLS): 建立加密和认证的连接, 以防止未经授权的访问和数据拦截, 确保通信安全。

全面的审计日志: 所有智能体间的通信都被详细记录, 包括信息流、涉及的智能体和执行的操作。这个审计跟踪对于问责、故障排查和安全分析至关重要。

智能体卡片声明: 身份验证要求在智能体卡片中明确声明, 这是概述智能体身份、能力和安全策略的配置工件。这使得身份验证管理得以集中和简化。

凭证处理: 智能体通常使用安全的凭证 (如 OAuth 2.0 令牌或 API 密钥) 进行身份验证, 这些凭证通过 HTTP 标头传递。这种方法可以防止凭证在 URL 或消息体中暴露, 从而增强整体安全性。

## A2A vs. MCP
A2A 与 MCP 的对比

A2A 是与 Anthropic 模型上下文协议 (Model Context Protocol, MCP) 互补的协议 (见图 1)。MCP 侧重于为智能体及其与外部数据和工具的交互构建上下文, 而 A2A 则促进智能体之间的协调与通信, 从而实现任务委派和协作。

![Comparison A2A and MCP Protocols](/images/chapter15_fig1.png)
图 1: A2A 和 MCP 协议的比较

A2A 的目标是在开发复杂的多智能体 AI 系统时提高效率、降低集成成本, 并促进创新和互操作性。因此, 深入理解 A2A 的核心组件和操作方法对于在构建协作和互操作的 AI 智能体系统中有效设计、实施和应用至关重要。
## Practical Applications & Use Cases | 实际应用与使用场景

智能体间通信对于在不同领域构建复杂的 AI 解决方案是不可或缺的, 它能实现模块化、可扩展性并增强智能。

**多框架协作**: A2A 的主要使用场景是使独立 AI 智能体能够进行通信和协作, 无论其底层框架如何 (例如 ADK、LangChain、CrewAI)。这对于构建复杂多智能体系统至关重要, 在这些系统中, 不同智能体专注于问题的不同方面。

**自动化工作流编排**: 在企业环境中, A2A 可以通过使智能体能够委派和协调任务来促进复杂的工作流。例如, 一个智能体可能负责初始数据收集, 然后委派给另一个智能体进行分析, 最后再委派给第三个智能体生成报告, 所有这些都通过 A2A 协议进行通信。

**动态信息检索**: 智能体可以通信以检索和交换实时信息。主智能体可能会向专门的「数据获取智能体」请求实时市场数据, 该智能体随后使用外部 API 收集信息并将其发回。
## Hands-On Code Example | 动手代码示例

让我们来研究一下 A2A 协议的实际应用。位于 [https://github.com/google-a2a/a2a-samples/tree/main/samples](https://github.com/google-a2a/a2a-samples/tree/main/samples) 的代码仓库提供了 Java、Go 和 Python 的示例, 展示了各种智能体框架 (如 LangGraph、CrewAI、 Azure AI Foundry 和 AG2) 如何使用 A2A 进行通信。该仓库中的所有代码均在 Apache 2.0 许可下发布。为了进一步说明 A2A 的核心概念, 我们将回顾一些代码片段, 重点介绍如何使用基于 ADK 的智能体和经过 Google 认证的工具来设置 A2A 服务器。请看 [https://github.com/google-a2a/a2a-samples/blob/main/samples/python/agents/birthday_planner_adk/calendar_agent/adk_agent.py](https://github.com/google-a2a/a2a-samples/blob/main/samples/python/agents/birthday_planner_adk/calendar_agent/adk_agent.py)

这段 Python 代码定义了异步函数 <code>create_agent</code>, 用于构建 ADK <code>LlmAgent</code>。它首先使用提供的客户端凭据初始化 <code>CalendarToolset</code> 以访问 Google Calendar API。随后, 创建 <code>LlmAgent</code> 实例, 配置指定的 Gemini 模型、描述性名称以及管理用户日历的指令。该智能体配备了来自 <code>CalendarToolset</code> 的日历工具, 使其能够与 Calendar API 交互, 并响应用户关于日历状态或修改的查询。智能体的指令动态地包含了当前日期以提供时间上下文。

为了说明如何构建智能体, 让我们看一下 GitHub 上 A2A 示例中 <code>calendar_agent</code> 的关键部分。下面的代码展示了如何使用特定指令和工具定义智能体。请注意, 这里只显示了解释此功能所需的代码; 完整文件可以在此处访问: [https://github.com/a2aproject/a2a-samples/blob/main/samples/python/agents/birthday_planner_adk/calendar_agent/__main__.py](https://github.com/a2aproject/a2a-samples/blob/main/samples/python/agents/birthday_planner_adk/calendar_agent/__main__.py)

   # Verify an API key is set.
   # Not required if using Vertex AI APIs.

这段 Python 代码演示了如何设置符合 A2A 规范的「日历智能体」, 用于使用 Google 日历检查用户空闲状态。它涉及验证 API 密钥或 Vertex AI 配置以进行身份验证。智能体的能力, 包括 <code>check_availability</code> 技能, 都在 <code>AgentCard</code> 中定义, 该卡片还指定了智能体的网络地址。随后, 创建 ADK 智能体, 并配置了用于管理工件、会话和内存的内存服务。然后, 代码初始化 Starlette Web 应用程序, 集成了身份验证回调和 A2A 协议处理器, 并使用 Uvicorn 启动它, 通过 HTTP 暴露该智能体。

这些示例说明了构建符合 A2A 规范智能体的过程, 从定义其能力到将其作为 Web 服务运行。通过利用智能体卡片和 ADK, 开发人员可以创建能够与 Google 日历等工具集成的可互操作 AI 智能体。这种实用方法展示了 A2A 在建立多智能体生态系统中的应用。

建议通过 [https://www.trickle.so/blog/how-to-build-google-a2a-project](https://www.trickle.so/blog/how-to-build-google-a2a-project) 上的代码演示进一步探索 A2A。该链接提供的资源包括 Python 和 JavaScript 的 A2A 客户端和服务器示例、多智能体 Web 应用程序、命令行界面以及各种智能体框架的实现示例。
## At a Glance | 概览

问题: 单个 AI 智能体, 特别是那些基于不同框架构建的智能体, 通常难以独立解决复杂、多方面的问题。主要挑战在于缺乏使这些智能体能够有效沟通和协作的通用语言或协议。智能体间的孤立状态阻碍了复杂系统的创建, 在这些系统中, 多个专业智能体本可以结合其独特技能来解决更大的任务。如果没有标准化方法, 集成这些异构智能体的成本高昂、耗时, 并让更强大、更有凝聚力的 AI 解决方案开发变得困难。

解决方案: 智能体间通信 (A2A) 协议为这个问题提供了开放、标准化的解决方案。它是基于 HTTP 的协议, 可实现互操作性, 允许不同 AI 智能体无缝协调、委派任务和共享信息, 而不受其底层技术限制。其核心组件是智能体卡片, 这是描述智能体能力、技能和通信端点的数字身份文件, 便于发现和交互。A2A 定义了各种交互机制, 包括同步和异步通信, 以支持不同的使用场景。通过为智能体协作创建通用标准, A2A 为构建复杂多智能体系统提供了模块化和可扩展的生态系统。

经验法则: 当需要协调两个或多个 AI 智能体之间的协作时, 尤其是在它们使用不同框架 (例如 Google ADK、LangGraph、CrewAI) 构建的情况下, 请使用此模式。它非常适合构建复杂模块化应用程序, 其中专门的智能体处理工作流的特定部分, 例如将数据分析委派给一个智能体, 将报告生成委派给另一个智能体。当智能体需要动态发现和使用其他智能体的能力来完成任务时, 此模式也至关重要。

## Visual summary
可视化摘要

![A2A inter-agent communication pattern](/images/chapter15_fig2.png)
图 2: A2A 智能体间通信模式
## Key Takeaways | 关键要点
关键要点
- Google A2A 协议是一个开放的、基于 HTTP 的标准, 它促进了由不同框架构建的 AI 智能体之间的通信和协作。

- 智能体卡片作为智能体的数字标识符, 允许其他智能体自动发现和理解其能力。

- A2A 提供同步请求-响应交互 (使用 <code>tasks/send</code>) 和流式更新 (使用 <code>tasks/sendSubscribe</code>), 以适应不同的通信需求。

- 该协议支持多轮对话, 包括 <code>input-required</code> 状态, 允许智能体在交互过程中请求额外信息并保持上下文。

- A2A 鼓励采用模块化架构, 其中专门的智能体可以在不同端口上独立运行, 从而实现系统的可扩展性和分布式部署。

- 像 Trickle AI 这样的工具有助于可视化和跟踪 A2A 通信, 帮助开发人员监控、调试和优化多智能体系统。

- A2A 是一个用于管理不同智能体之间任务和工作流的高级协议, 而模型上下文协议 (MCP) 则为 LLM 与外部资源交互提供了一个标准化的接口。
## Conclusions | 结论

智能体间通信 (A2A) 协议建立了至关重要的开放标准, 克服了单个 AI 智能体固有的孤立性。通过提供通用的基于 HTTP 的框架, 它确保了在不同平台 (如 Google ADK、LangGraph 或 CrewAI) 上构建的智能体之间的无缝协作和互操作性。其核心组件是智能体卡片, 它作为数字身份, 清晰地定义了智能体的能力, 并使其他智能体能够动态发现。该协议的灵活性支持各种交互模式, 包括同步请求、异步轮询和实时流式传输, 满足了广泛的应用需求。这使得创建模块化和可扩展的架构成为可能, 其中专门的智能体可以组合起来编排复杂的自动化工作流。安全性是最基础的能力, 内置了 mTLS 和明确的身份验证要求等机制来保护通信。虽然 A2A 与 MCP 等其他标准互补, 但其独特的重点在于智能体之间的高层协调和任务委派。来自主流技术公司的强大支持和实际实现的可用性凸显了其日益增长的重要性。该协议为开发人员构建更复杂、分布式和智能的多智能体系统铺平了道路。最终, A2A 是促进协作式 AI 的创新和互操作生态系统的基础支柱。
## References | 参考文献

