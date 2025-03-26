import os
from typing import ClassVar
from openai import AsyncOpenAI
from openai.types.chat.chat_completion_user_message_param import (
    ChatCompletionUserMessageParam,
)
from pydantic import BaseModel, Field

from chatgit.services.github import Github


class ChatMessageChunk(BaseModel):
    reasoning_content: str | None = Field(default=None)
    content: str | None = Field(default=None)


class ChatService:
    PROMPT: ClassVar[
        str
    ] = """我已获得一个开源项目的README文档，但无法快速理解其核心价值。请根据以下结构分析并解释该项目，要求：

用非技术语言翻译技术概念

突出实际应用价值

对模糊表述进行合理性推测并标注

缺失信息时主动询问

请按以下框架输出分析报告：

一、项目速览（30秒看懂）
项目本质：用比喻的方式说明（例："相当于AI领域的瑞士军刀"）

解决痛点：解释它解决了什么现实问题

核心能力：不超过3个技术关键词

适用对象：适合哪些人/企业使用？

二、关键技术拆解
架构图示：用文字描述系统架构流向（例："用户输入→云端处理→智能分发→结果可视化"）

创新点分析：对比传统方案的改进（列表呈现）

技术依赖：必须的基础设施/工具链

三、实用价值评估
效率提升：预计可节省的时间/资源比例

成本优势：与传统方案的财务对比

风险提示：部署时需注意的技术债/兼容性问题

四、上手实操指引
环境准备清单：分操作系统说明依赖项

配置避坑指南：常见安装错误的预防措施

场景化用例（至少2个）：

基础用例：小白用户操作路径

高级用例：开发者定制方案

五、深度追问建议
需补充的技术细节：______

应验证的性能指标：______

推荐延伸学习资料：______

请直接提供项目README内容，我将按此框架生成解读报告，并用🛠️/⚠️/💡符号标注技术难点、风险点和创新点。
示例段落（供参考）：
💡 创新点分析
传统方案需手动标注数据（耗时2-3天/项目），本项目通过____技术实现自动标注，准确率提升40%的同时，处理速度达到每秒300帧，相当于人工效率的50倍。

⚠️ 风险提示
当前版本在Windows环境下的____模块存在内存泄漏风险，连续运行超过48小时需重启服务（详见Issues #23）

仓库README内容：
{readme}
"""

    def __init__(
        self,
        *,
        model: str | None = None,
        api_key: str | None = None,
        base_url: str | None = None,
        timeout: int = 600,
    ):
        if api_key is None:
            api_key = os.environ.get("OPENAI_API_KEY")
        if base_url is None:
            base_url = os.environ.get("OPENAI_BASE_URL")
        if model is None:
            model = os.environ.get("OPENAI_MODEL")
        self.client = AsyncOpenAI(
            api_key=api_key, base_url=base_url, timeout=timeout, max_retries=3
        )
        self.model = model

    async def chat(self, messages: list[ChatCompletionUserMessageParam]):
        response = await self.client.chat.completions.create(
            model=self.model, messages=messages, stream=True
        )
        async for chunk in response:
            if not chunk.choices:
                continue
            if hasattr(chunk.choices[0].delta, "reasoning_content"):  # type: ignore
                yield ChatMessageChunk(
                    reasoning_content=chunk.choices[0].delta.reasoning_content
                )  # type: ignore
            else:
                yield ChatMessageChunk(
                    content=chunk.choices[0].delta.content, reasoning_content=None
                )  # type: ignore

    async def repo_chat(self, repo_url: str, github_token: str | None = None):
        readme = await Github(token=github_token).get_readme(repo_url)
        messages: list[ChatCompletionUserMessageParam] = [
            {"role": "user", "content": self.PROMPT.format(readme=readme)}
        ]
        async for item in self.chat(messages):
            yield item

    async def get_title(
        self, repo: str, messages: list[ChatCompletionUserMessageParam]
    ):
        prompt = """基于对话历史,生成3-5字的标题,要求:
1. 直击项目核心功能/最大亮点  
2. 开头或结尾加1个精准匹配emoji  
3. 禁用总结/分析等附加内容  
4. 输出仅保留最终标题  
5. 使用给定对话历史的语言
6. 结合项目名称: {repo}

如: 项目名称为ruff
标题: ruff: ⚡️超快代码检查

对话历史:
{memory}
"""
        messages[
            0
        ].content = (
            f"请基于该项目的readme介绍一下该项目的优势, 仓库地址: {messages[0].content}"
        )
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": prompt.format(
                        repo=repo, memory="\n".join((msg.content for msg in messages))
                    ),
                }
            ],
            stream=False,
        )
        return response.choices[0].message.content
