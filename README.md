# RAG-QA-System - 检索增强生成问答系统

## 项目简介

本项目是一个基于RAG（Retrieval-Augmented Generation）技术的智能问答系统，能够基于用户上传的文档内容进行精准问答。系统使用Ollama作为本地大模型服务，结合LangChain框架和Chroma向量数据库，实现文档的检索、向量化和智能问答功能。

## 环境要求与安装步骤

### 1. 安装Ollama

**Windows系统：**
- 下载地址：https://ollama.com/download/OllamaSetup.exe
- 安装完成后，在命令行运行：
  ```bash
  ollama pull deepseek-r1:7b
  ollama pull nomic-embed-text
  ```

**验证安装：**
```bash
ollama serve
```

### 2. Python环境要求

- Python 3.10+

### 3. 安装依赖库

```bash
pip install streamlit langchain langchain-community langchain-ollama chromadb pypdf2 python-docx tiktoken pyinstaller
```

## 使用说明

### 运行Web应用

```bash
streamlit run app.py
```

### 使用流程

1. **上传文档**：在侧边栏的"文档上传"区域选择PDF或DOCX文件
2. **构建知识库**：点击"构建/更新知识库"按钮，系统会自动解析文档并构建向量数据库
3. **提问**：在主界面的输入框中输入问题，点击"发送"按钮获取答案
4. **查看历史**：系统会自动保存对话历史，支持多轮连续问答

### 命令行模式

```bash
python rag_qa.py
```

## 关键技术点说明

### RAG流程

1. **文档解析**：支持PDF、DOCX、TXT等多种格式文档的文本提取
2. **文本分块**：使用RecursiveCharacterTextSplitter进行文本切分（chunk_size=1000, chunk_overlap=200）
3. **向量化**：使用Ollama内置的nomic-embed-text模型将文本块转换为向量
4. **向量存储**：使用Chroma向量数据库存储和管理向量数据
5. **检索**：基于用户查询进行相似性检索，返回最相关的3个文本块
6. **生成**：将检索到的上下文输入大模型，生成基于文档内容的回答

### 所用模型

- **语言模型**：deepseek-r1:7b（或qwen2:7b）
- **嵌入模型**：nomic-embed-text

### 系统提示词设计

系统提示词要求模型：
- 只能使用提供的参考文档中的信息回答问题
- 如果文档中没有相关信息，明确回答"文档中未找到相关答案"
- 不编造信息，不使用外部知识

## 项目结构

```
RAG-QA-System/
├── app.py                 # Streamlit Web应用主入口
├── rag_qa.py              # RAG问答系统核心模块
├── vector_store.py        # 向量数据库管理器
├── document_processor.py  # 文档处理器
├── requirements.txt       # 依赖列表
├── .gitignore             # Git忽略配置
├── run.bat               # 启动脚本
├── start_app.bat         # 应用启动批处理
└── documents/             # 示例文档目录
```

## 功能特点

- ✅ 支持PDF、DOCX、TXT文档上传
- ✅ 批量文档处理与知识库构建
- ✅ 基于文档内容的精准问答
- ✅ 多轮对话记忆功能
- ✅ 对话历史展示
- ✅ 知识库状态实时显示
- ✅ 支持清空知识库和对话历史

## 问答示例

**问题1：** 什么是自然语言处理？
**回答：** 自然语言处理（Natural Language Processing，简称NLP）是人工智能领域的一个重要分支，它致力于使计算机能够理解、处理和生成人类语言。

**问题2：** RAG的优势是什么？
**回答：** 相比传统的LLM，RAG具有以下优势：1. 时效性：可以使用最新的知识；2. 准确性：基于文档内容回答，减少幻觉；3. 可解释性：可以追溯回答的来源；4. 灵活性：无需重新训练模型即可更新知识。

**问题3：** BERT有哪些应用场景？
**回答：** BERT在多个NLP任务上取得了突破性进展：问答系统（QA）、文本分类、命名实体识别（NER）、语义相似度计算、自然语言推理。

**问题4：** Word2Vec有哪些训练方法？
**回答：** Word2Vec包含两种训练方法：1. Skip-gram：给定中心词预测周围的上下文词；2. CBOW（Continuous Bag of Words）：给定上下文词预测中心词。

**问题5：** NLP在哪些场景有应用？
**回答：** NLP技术广泛应用于：智能客服系统、文本分类与情感分析、机器翻译、信息抽取、语音助手、文档摘要、知识图谱等领域。

**无关问题1：** 明天天气怎么样？
**回答：** 文档中未找到相关答案

**无关问题2：** 如何制作蛋糕？
**回答：** 文档中未找到相关答案

## 打包部署

使用PyInstaller打包成独立exe文件：

```bash
pyinstaller --onefile --windowed app.py
```

## 许可证

本项目仅供学习和研究使用。

---

**项目作者：** 学生姓名  
**学号：** 2405030227  
**日期：** 2024年