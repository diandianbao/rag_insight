# 第四章：反思
## Reflection Pattern Overview | 反思模式概述

在前面的章节中，我们探讨了智能体的基础模式：用于顺序执行的提示链（Prompt Chaining）、用于动态路径选择的路由（Routing），以及用于并发任务执行的并行模式（Parallelization）。这些模式使智能体能够更高效、更灵活地执行复杂任务。然而，即使工作流设计再精妙，智能体初始输出或计划也未必最优、准确或完整。这正是<strong>反思（Reflection）模式</strong>发挥作用之处。

反思模式是指智能体评估自己的工作、输出和内部状态，并利用评估结果改进性能和优化响应。这是一种自我纠正或自我改进的形式。通过这种形式，智能体可以根据反馈、内部剖析及与期望标准的比较，来不断地优化输出、调整方法。反思有时也可由独立的智能体来承担，其职责是专门分析初始智能体的输出。

反思模式与简单顺序链或路由模式有着本质区别。前者只是将输出直接传给下一步，或是在不同路径中做出选择；而反思模式则引入了反馈循环。在这种模式下，智能体并非简单地产出结果就结束了。它会回过头来审视自己的输出（或其生成过程），找出潜在的问题和改进空间，并依据这些洞察生成更优的版本，或是修正其后续的行动策略。

这个过程通常包括以下步骤：

   <strong>执行：</strong>智能体执行任务或生成初始版本的输出。

   <strong>评估/剖析：</strong>智能体（通常借助另一个大语言模型调用或一组规则）对上一步的结果进行分析。该过程旨在检查其事实准确性、内容连贯性、风格、完整度、是否遵循指令以及其他相关标准。

   <strong>反思/优化：</strong>根据上一轮的剖析结果，智能体将确定具体的改进方向。这可能涉及几个方面：生成一个更为精炼的输出、为后续步骤调整参数，甚至是修正整体计划。

   <strong>迭代（可选，但很常见）：</strong>随后，智能体便会将优化后的输出或调整过的方法付诸执行，并循环往复地进行整个反思过程，直到最终结果令人满意，或满足了预设的停止条件

反思模式的一个关键且高效的实现方式，是将流程拆分为两个独立的逻辑角色：生产者（Producer）和评论者（Critic）。这通常被称为「生成器 - 评论者」（Generator-Critic）或「生产者 - 审查者」（Producer-Reviewer）模型。虽然单个智能体也能进行自我反思，但使用两个专用的智能体（或两个具有不同系统提示的独立大语言模型调用）通常能产出更稳健、更客观的结果。

   <strong>生产者智能体：</strong>主要职责是完成任务的初始执行。它完全专注于生成内容，无论是编写代码、起草博客文章还是制定计划。它会接收初始提示，并据此生成输出的第一个版本。

   <strong>评论者智能体：</strong>该智能体的唯一使命就是评估由生产者生成的输出。它会被赋予一套不同的指令，通常还包含一个独特的角色设定（例如「你是一位高级软件工程师」、「你是一位严谨的事实核查员」）。评论者的指令引导它根据特定标准分析生产者的工作，如事实准确性、代码质量、风格要求和完整性，旨在发现问题、提出改进建议并给出结构化的反馈。

这种职责分离非常有效，因为它避免了智能体自我审查时产生的<strong>认知偏见</strong>。评论者智能体以全新视角审视输出，完全专注于发现错误和改进空间。它的反馈意见随后传回给生产者智能体，生产者据此对内容进行修改和优化。实战部分 LangChain 和 ADK 代码示例都采用了这种双智能体模型：LangChain 使用特定的 <code>reflector_prompt</code> 创建评论者角色，而 ADK 示例明确区分了生产者和审查者两个智能体。

实现反思模式通常需要构建包含反馈循环的智能体工作流。这可以通过在编码实现迭代循环，或使用支持状态管理和根据评估结果进行条件跳转的框架来完成。虽然单步评估和优化可以在 LangChain/LangGraph、ADK 或 Crew.AI 链中实现，但真正的迭代反思通常需要更复杂的编排。

反思模式对于构建能产出高质量结果、应对复杂任务并展现自我意识与适应能力的智能体非常重要。它让智能体不再只是执行指令，而是发展出更成熟的推理与内容生成能力。

需要特别注意反思模式与目标设定和监控（见第 11 章）的联系。目标为智能体的自我评估提供最终基准，监控则跟踪其进度。在许多实际情形中，反思会充当纠偏机制：利用监控反馈分析偏离之处并据此调整策略。这样的协同作用使智能体从单纯执行者变成有目的的、自主适应以实现目标的系统。

此外，当模型能保持对话记忆时，反思模式的有效性显著增强（见第 8 章）。对话历史为评估阶段提供关键上下文，使智能体不仅能孤立评估输出，还能结合先前交互、用户反馈和不断演变的目标进行评估。这使智能体能从过去的评价反馈中学习并避免重复错误。没有记忆，每次反思都是独立事件；有了记忆，反思成为累积性的循环，每个轮次都建立在上一轮基础上，从而实现更智能、更具上下文感知的优化。

---
## Practical Applications & Use Cases | 实际应用场景

当输出质量、准确性或对复杂约束的遵从性至关重要时，反思模式非常有用：
**1. Creative Writing and Content Generation:**  | <strong>创意写作和内容生成：</strong>

对生成的文本、故事、诗歌或营销文案进行润色和改进。

- <strong>用例：</strong>撰写博客文章的智能体。
- <strong>反思：</strong>先写一篇草稿，再从流畅性、语气和表达清晰度等方面进行检查，随后根据反馈重写草稿。反复进行，直到文章符合质量要求。
- <strong>好处：</strong>产生更精致、更有效的内容。
**2. Code Generation and Debugging:** | <strong>代码生成和调试：</strong>

编写代码、识别错误并修复它们。

- <strong>用例：</strong>编写 Python 函数的智能体。
- <strong>反思：</strong>编写初始代码，运行测试或静态分析，识别错误或低效之处，然后基于这些发现优化代码。
- <strong>好处：</strong>生成更健壮、功能更完整的代码。
**3. Complex Problem Solving:** | <strong>复杂问题解决：</strong>

在多步推理任务中，对中间步骤或所提出的解决方案进行评估和审查。

- <strong>用例：</strong>解决逻辑推理类谜题的智能体。
- <strong>反思：</strong>提出一个行动步骤，评估该步骤是否有助于推进问题的解决或引入矛盾；如发现问题，则回退并尝试其他步骤。
- <strong>好处：</strong>增强智能体在复杂问题情境中分析和解决问题的能力。
**4. Summarization and Information Synthesis:** | <strong>摘要和信息综合：</strong>

对摘要进行润色，使其更准确、完整且简明。

- <strong>用例：</strong>总结长文档的智能体。
- <strong>反思：</strong>先生成一份初步摘要，再将其与原文的要点对照，找出遗漏或不准确之处，随后对摘要进行修订，补充缺失信息并提高准确性。
- <strong>好处：</strong>生成更准确、更全面的摘要。
**5. Planning and Strategy:** | <strong>规划和策略：</strong>

评估所提计划，找出存在的问题并提出改进建议。

- <strong>用例：</strong>规划一系列行动以实现特定任务的智能体。
- <strong>反思：</strong>制定计划，模拟执行或根据限制评估可行性，然后根据评估结果对计划进行改进与调整。
- <strong>好处：</strong>制定更有效、更符合实际的计划。
**6. Conversational Agents:** | <strong>对话智能体：</strong>

回顾对话中的前几轮交流，以保持上下文连贯、纠正误会并提升回答的质量。

- <strong>用例：</strong>客户支持聊天机器人。
- <strong>反思：</strong>在用户回复后，回顾整个对话和上一次生成的内容，确认信息前后连贯并针对用户的最新输入做出准确回应。
- <strong>好处：</strong>实现更自然、更高效的沟通。

反思模式为智能体系统增加了一层元认知能力，使其能从自己处理过程和输出中学习，从而产生更智能、更可靠、更高质量的结果。

---
## Hands-On Code Example (LangChain) | 实战示例：使用 LangChain

要实现完整的迭代反思流程，需要具备状态管理和循环执行的机制。虽然诸如 LangGraph 这类基于图的框架，或自定义的过程式代码可以原生支持这些功能，但通过 LCEL（LangChain 表达式语言）的组合语法，就能清晰地演示反思模式的核心原理。

本示例使用 Langchain 库和 OpenAI 的 <code>GPT-4o</code> 模型实现反思循环，迭代生成并优化一个计算阶乘的 Python 函数。流程从任务提示开始，生成初始代码，然后由扮演高级软件工程师角色的智能体提出改进建议并反复迭代，直到确定代码已无可改进或达到最大迭代次数时结束，最终输出完善后的代码。

首先确保已安装必要的库：

还需要为选择的语言模型（例如 OpenAI、Google Gemini、Anthropic）设置 <code>API</code> 密钥。

# Colab 代码链接：https://colab.research.google.com/drive/1xnL6Rky6nsm4iAhomLnUK3kgwSyyYZfb

# 安装依赖
# pip install langchain langchain-community langchain-openai

# --- Configuration ---
# Load environment variables from .env file (for OPENAI_API_KEY)
# 从 .env 文件加载环境变量（如 OPENAI_API_KEY）

# Check if the API key is set
# 检查 API 密钥是否设置

# Initialize the Chat LLM. We use a powerful model like gpt-4o for better reasoning.
# A lower temperature is used for more deterministic and focused outputs.
# 使用 gpt-4o 或其他模型，并设置较低的温度值以获得更稳定的输出

    展示了通过多步骤反思循环，逐步改进 Python 函数的方法。

    # --- The Core Task ---
    # --- 核心任务的提示词 ---

    # --- The Reflection Loop ---
    # --- 反思循环 ---
    # We will build a conversation history to provide context in each step.
    # 构建对话历史，为每一步提供必要的上下文信息。

        # --- 1. GENERATE / REFINE STAGE ---
        # In the first iteration, it generates. In subsequent iterations, it refines.
        # 在第一次迭代时，生成初始代码；在后续迭代时，基于上一步的反馈优化代码。
            # The first message is just the task prompt.
            # 第一次迭代时，只需要任务提示词。
            # The message history now contains the task, the last code, and the last critique.
            # We instruct the model to apply the critiques.
            # 后续迭代时，除了任务提示词，还包含上一步的代码和反馈。
            # 然后要求模型根据反馈意见优化代码。

        # --- 2. REFLECT STAGE ---
        # --- 反思阶段 ---

        # Create a specific prompt for the reflector agent.
        # This asks the model to act as a senior code reviewer.
        # 创建一个特定的提示词，要求模型扮演高级软件工程师的角色，对代码进行仔细的审查。

        # --- 3. STOPPING CONDITION ---
        # 如果代码完美符合要求，则结束反思循环。

        # Add the critique to the history for the next refinement loop.

译者注：[Colab 代码](https://colab.research.google.com/drive/1xnL6Rky6nsm4iAhomLnUK3kgwSyyYZfb) 已维护在[此处](/codes/Chapter-04-Reflection-LangChain-Example.py)，同时补充了输出结果作为参考。

代码首先设置环境、加载 API 密钥，并初始化 GPT-4o 模型，使用低温度值以获得稳定的输出。核心任务由一个提示定义，要求创建一个计算阶乘的 Python 函数，要求包含完整的文档、处理边界情况（如 0 的阶乘）、以及对负数输入的错误处理。
<code>run_reflection_loop</code> 函数负责协调整个迭代优化过程。在循环中，第一次迭代由大语言模型基于任务提示生成初始代码；之后的迭代则根据上一步给出的建议优化代码。
还有一个独立的「反思者」角色，同样由大语言模型扮演但使用不同系统提示。它以高级软件工程师的身份来评审生成的代码是否符合原始需求，并以问题列表的形式提供反馈意见，或在没有发现问题时返回 <code>CODE_IS_PERFECT</code>。循环会持续进行，直到评审认为代码已无可改进或达到最大迭代次数。
会话历史在每一步都会保留并传递给语言模型，为生成、改进和反思阶段提供上下文。最后，脚本在循环结束时打印出最终代码版本。

---
## Hands-On Code Example (Google ADK) | 实战示例：使用 Google ADK

现在我们来看一个使用 Google ADK 实现的示例。具体来说，代码采用「生成器 - 评论者」架构来演示反思模式，其中一个组件（生成器）产生初始结果或方案，另一个组件（评论者）提出反馈建议，帮助生成器不断改进，最终得到更完善、更准确的输出。

# Colab 代码链接：https://colab.research.google.com/drive/1nwE2GH6c08dGlvAv7T28uF1xe2qeu2q_

# The first agent generates the initial draft.
# 第一个智能体生成初始草稿。

# The second agent critiques the draft from the first agent.
# 第二个智能体评审第一个智能体的草稿。

# The SequentialAgent ensures the generator runs before the reviewer.
# 确保生成者在评论者之前运行。

# Execution Flow:
# 1. generator runs -> saves its paragraph to state['draft_text'].
# 2. reviewer runs -> reads state['draft_text'] and saves its dictionary output to state['review_output'].
# 执行流程：
# 1. 生成者运行 -> 将其段落保存到 state['draft_text']。
# 2. 评论者运行 -> 读取 state['draft_text'] 并将其字典输出保存到 state['review_output']。

译者注：[Colab 代码](https://colab.research.google.com/drive/1nwE2GH6c08dGlvAv7T28uF1xe2qeu2q_) 已维护在[此处](/codes/Chapter-04-Reflection-ADK-Example.py)。

该示例展示了在 Google ADK 中使用顺序智能体管道来生成和审查文本。它定义了两个 <code>LlmAgent</code> 实例：<code>generator</code> 和 <code>reviewer</code>。生成器智能体负责根据指定主题撰写一段简短且信息量高的初稿，并将结果存为状态键 <code>draft_text</code>。审查者智能体则作为事实核查者，从 <code>draft_text</code> 读取内容并核实事实准确性。审查者的输出是一个结构化字典，包含两个键：<code>status</code> 和 <code>reasoning</code>，其中状态的值包括 <code>ACCURATE</code> 和 <code>INACCURATE</code>，而 <code>reasoning</code> 字段是对状态判断的补充说明，具体的值保存在状态键 <code>review_output</code>。
然后通过名为 <code>review_pipeline</code> 的 <code>SequentialAgent</code> 来控制两个智能体的执行顺序，确保先执行生成器智能体，再执行审查者智能体。整体流程是生成器先生成并保存文本，然后审查者读取状态并执行事实核查，再将核查发现的内容保存回状态。这种管道化的设计便于用独立的智能体完成结构化的内容创作与审查。<strong>注意：</strong>对于感兴趣的用户，还可使用 ADK 的 <code>LoopAgent</code> 实现类似功能。

在结束前需要注意，虽然反思模式能显著提升输出质量，但也有重要的权衡。其迭代过程虽有效，却可能带来更高的成本和更长的延迟，因为每次改进往往都要发起一次新的模型调用，因此对时间敏感的场景并不适合。另外，该模式占用的内存也会较多，因为随着每轮迭代的进行，会话历史会不断增长，包含最初的输出、评价意见和后续的改进内容。

---
## At a Glance | 要点速览

<strong>问题所在：</strong>智能体的初始输出通常不够理想，存在不准确、不完整或未能满足复杂要求的问题。基本智能体工作流缺乏内置过程让智能体识别和修复自己的错误。为了解决这一点，可以让智能体先自我评估，或通过引入独立的智能体来审查和指出问题，确保初始回答不会直接作为最终结果。

<strong>解决之道：</strong>反思模式通过引入自我纠错和改进机制来解决问题。它建立反馈循环，其中「生产者」智能体生成输出，然后「评论者」智能体（或生产者本身）根据预定义标准评估输出。相关的反馈建议随后用于生成改进版本。这种生成、评估和优化的迭代过程逐步提高最终结果的质量，产生更准确、连贯和可靠的结果。

<strong>经验法则：</strong>当最终输出的质量、准确性和细节比速度和成本更重要时应考虑使用反思模式。它对于生成高质量的长篇内容、编写和调试代码、创建详细计划等任务非常有效。当任务需要更高的客观性或涉及专业评估（常规生产者可能会遗漏），建议采用独立的评论者智能体以提高输出质量。
**Visual summary** | <strong>可视化总结</strong>

![Reflection Pattern - Self-Reflection](/images/chapter04_fig1.png)

图 1：反思设计模式之自我反思

![Reflection Pattern - Producer and Critic](/images/chapter04_fig2.png)

图 2：反思设计模式之生产者和评论者智能体

---
## Key Takeaways | 核心要点

   反思模式的主要优势在于它可以通过反复自我修正和改进输出，显著提高质量、准确性和遵循更复杂的指令。

   它包括执行、评估/评价和改进的反馈循环。对于需要高质量、准确性或细腻表述的任务，反思是不可或缺的。

   一个有效的方法是采用「生产者 - 评论者」模型，由一个独立的智能体（或基于提示的不同角色）来评估初始输出。通过职责分离可以提高评判的客观性，并提供更专业、更有条理的反馈。

   然而，这些好处以增加延迟和成本为代价，同时还有超出模型上下文窗口或被 <code>API</code> 服务限流的风险。

   虽然完整的迭代反思通常依赖有状态的工作流（例如 LangGraph），但在 LangChain 中也可以用 LCEL 实现一次性的反思步骤，将生成的输出传给评论者以进行评审并据此改进。

   Google ADK 可以通过一系列串联的工作流程来促进反思：一个智能体生成输出，另一个智能体对其进行评审，并据此进行后续改进。

   该模式使智能体能够自我修正，并随着时间不断提高表现。

---
## Conclusion | 结语

反思模式为智能体的工作流程提供了自我修正的关键手段，使其能通过多次迭代而不是一次性完成任务来持续改进。具体做法是形成一个循环：系统先生成初稿，然后按照既定标准对其进行评估，最后根据评估结果生成更完善的输出。这种评估既可以由智能体自己完成（自我反思），也可以由一个专门的评论者智能体来执行。通常后一种方式更有效，也是该模式的一个重要架构决策。

虽然要实现完全自主的多步骤反思需要可靠的状态管理架构，但其核心思想可以通过「生成—评审—改进」的循环清晰地呈现。作为一种控制结构，反思可以与其他基础模式结合使用，从而构建更稳健、功能更强大的智能体系统。

---
## References | 参考文献

以下是有关反思模式和相关概念的进一步阅读资源：

   使用强化学习训练语言模型以实现自我纠正，[https://arxiv.org/abs/2409.12917](https://arxiv.org/abs/2409.12917)

   LangChain 表达式语言文档：[https://python.langchain.com/docs/introduction/](https://python.langchain.com/docs/introduction/)

   LangGraph 文档：[https://www.langchain.com/langgraph](https://www.langchain.com/langgraph)

   Google 智能体开发套件 (ADK) 文档（多智能体系统）：[https://google.github.io/adk-docs/agents/multi-agents/](https://google.github.io/adk-docs/agents/multi-agents/)
