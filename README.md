# 基于 RAG 的 AI 知识库问答系统

## 项目简介

本项目是一个基于 RAG（Retrieval-Augmented Generation，检索增强生成）的 AI 知识库问答系统。

用户可以上传本地文档，系统会对文档内容进行解析、切分、向量化和语义检索，并结合 DeepSeek 大模型生成回答。

该项目主要用于学习和实践 AI 应用开发流程，涵盖文档处理、Embedding 向量化、FAISS 向量检索、Prompt 构造和大模型 API 调用。

## 技术栈

- Python
- Streamlit
- FAISS
- SentenceTransformer
- DeepSeek API
- RAG

## 核心功能

- 支持上传 PDF、DOCX、TXT、Markdown 等文档
- 对文档内容进行文本提取和切分
- 使用 SentenceTransformer 生成文本向量
- 使用 FAISS 构建本地向量索引
- 根据用户问题检索相关文档片段
- 调用 DeepSeek API 生成基于文档内容的回答
- 使用 Streamlit 搭建可视化 Web 页面

## 项目流程

```text
上传文档
↓
文本提取
↓
文本切分
↓
文本向量化
↓
FAISS 相似度检索
↓
拼接 Prompt
↓
DeepSeek 生成回答
↓
页面展示结果
运行方式
1. 安装依赖
pip install -r requirements.txt
2. 启动项目
streamlit run rag_web.py
3. 打开页面

浏览器访问：

http://localhost:8501
文件说明
rag_step1.py       RAG 第一步实验代码
rag_step2.py       文本处理和切分代码
rag_step3.py       向量化和检索代码
rag_step4.py       大模型问答整合代码
rag_final.py       命令行版本完整 RAG 流程
rag_web.py         Streamlit Web 页面版本
deepseek_chat.py   DeepSeek API 调用示例
ai_web_chat.py     简单 Web 对话测试代码

配置文件说明

.gitignore

`.gitignore` 用于配置 Git 忽略规则，防止一些不应该上传到 GitHub 的文件被提交到远程仓库。

本项目中主要忽略了 API Key、本地环境配置、Python 缓存文件、VS Code 本地配置、虚拟环境和日志文件。例如：

* `API-KEY.txt`：用于存放本地 API Key，避免敏感信息泄露
* `.env`：用于存放环境变量配置
* `__pycache__/` 和 `*.pyc`：Python 自动生成的缓存文件
* `.vscode/`：VS Code 本地编辑器配置
* `.venv/` 和 `venv/`：Python 虚拟环境目录
* `*.log`：程序运行日志文件

通过 `.gitignore` 可以保证 GitHub 仓库更加干净，同时避免上传敏感信息。

依赖说明
requirements.txt

`requirements.txt` 用于记录项目运行所需的 Python 第三方依赖库。

其他用户从 GitHub 下载项目后，可以通过以下命令快速安装依赖：


pip install -r requirements.txt

本项目中主要依赖如下：

* `streamlit`：用于搭建 Web 可视化交互页面
* `pypdf`：用于读取和解析 PDF 文档
* `python-docx`：用于读取 Word 文档内容
* `sentence-transformers`：用于生成文本向量 Embedding
* `faiss-cpu`：用于构建本地向量索引并进行相似度检索
* `numpy`：用于处理向量数组和数值计算
* `requests`：用于调用 DeepSeek API，获取大模型回答

通过 `requirements.txt`，项目可以更方便地在其他环境中复现和运行。

安全说明

本项目不会上传 API Key。运行时需要用户在本地输入自己的 DeepSeek API Key。

后续优化方向
增加知识库持久化
增加历史问答记录
增加答案来源引用
优化文本切分策略
支持多轮对话
支持更多文档格式
增加用户登录和权限管理