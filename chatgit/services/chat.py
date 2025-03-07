import os
from typing import ClassVar
from openai import AsyncOpenAI
from openai.types.chat.chat_completion_user_message_param import ChatCompletionUserMessageParam
from pydantic import BaseModel, Field

from chatgit.services.github import Github

class ChatMessageChunk(BaseModel):
    reasoning_content: str | None = Field(default=None)
    content: str | None = Field(default=None)

class ChatService:
    PROMPT: ClassVar[str] = """**角色**：你是一个资深开源项目分析师，擅长通过文档结构、技术描述和社区规范评估项目质量。

**任务**：对用户提供的GitHub仓库README进行多维度解析，需包含但不限于以下分析框架：

### 1. 基础信息扫描
- [ ] 项目标题清晰度
- [ ] 项目徽章(Badges)完整性（构建状态、版本号、下载量、依赖状态等）
- [ ] 多语言支持情况
- [ ] 最后更新时间
- [ ] 文档目录(TOC)有效性

### 2. 内容结构解构
▌核心模块分析：
- 项目背景（问题陈述/解决方案/技术选型）
- 功能特性列表完整度
- 架构图/流程图等可视化资源
- 安装部署指南（多环境支持、系统要求）
- 配置说明（环境变量/配置文件模板）
- API文档完整性
- 使用示例丰富度（代码片段/使用场景）
- 测试方案描述
- 路线图(Roadmap)清晰度

▌协作规范检查：
- 贡献指南详细程度（PR规范/代码风格/测试要求）
- Issue模板合理性
- 行为准则(Code of Conduct)存在性
- 版本更新记录(CHANGELOG)

▌法律信息核验：
- 开源许可证类型及合规性
- 免责声明完整性
- 安全相关说明

### 3. 文档质量评估
- 技术术语解释充分性
- 中英双语支持情况
- 链接有效性检测（外部资源/内部锚点）
- 截图/示意图清晰度
- 移动端阅读适配性
- 可访问性(A11y)设计

### 4. 维护活性诊断
- 文档与代码同步程度
- 弃用警告/迁移指南
- 社区支持渠道（Discord/Slack/论坛）
- 常见问题覆盖度
- 文档更新频率

**输出要求**：
1. 按[通过/警告/缺失]三级标记关键项
2. 生成可读性评分（1-5★）
3. 提供模块化优化建议
4. 标注需要维护者澄清的内容
5. 总结文档体现的项目成熟度

仓库README内容：
{readme}
"""

    def __init__(self, model: str, *, api_key: str | None= None, base_url: str | None = None, timeout: int = 60):
        if api_key is None:
            api_key = os.environ.get("OPENAI_API_KEY")
        if base_url is None:
            base_url = os.environ.get("OPENAI_API_BASE")
        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url, timeout=timeout, max_retries=3)
        self.model = model

    async def chat(self, repo_url: str, github_token: str | None = None):
        readme = await Github(token=github_token).get_readme(repo_url)
        messages: list[ChatCompletionUserMessageParam] = [{"role": "user", "content": self.PROMPT.format(readme=readme)}]
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            stream=True
        )
        async for chunk in response:
            if hasattr(chunk.choices[0].delta, "reasoning_content"): # type: ignore
                yield ChatMessageChunk(reasoning_content=chunk.choices[0].delta.reasoning_content) # type: ignore
            else: 
                yield ChatMessageChunk(content=chunk.choices[0].delta.content, reasoning_content=None) # type: ignore