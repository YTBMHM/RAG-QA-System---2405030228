import os
from typing import List, Dict, Optional
from langchain_ollama import OllamaLLM
from langchain_core.documents import Document
try:
    from langchain.chains import ConversationalRetrievalChain
    from langchain.memory import ConversationBufferMemory
    from langchain.prompts import PromptTemplate
except ImportError:
    from langchain_classic.chains import ConversationalRetrievalChain
    from langchain_classic.memory import ConversationBufferMemory
    from langchain_classic.prompts import PromptTemplate

from document_processor import DocumentProcessor
from vector_store import VectorStoreManager

SYSTEM_PROMPT = """
你是一个专业的问答助手，你的任务是基于提供的参考文档回答用户的问题。

请严格遵循以下规则：
1. 仔细阅读并理解用户的问题。
2. 只能使用提供的参考文档中的信息来回答问题。
3. 如果文档中有相关信息，请基于文档内容给出详细、准确的回答。
4. 如果文档中没有找到相关信息，请明确回答"文档中未找到相关答案"。
5. 不要编造信息，不要猜测，不要使用外部知识。
6. 回答要简洁明了，直接针对问题。

参考文档：
{context}

用户问题：{question}
"""

class RAGQASystem:
    def __init__(
        self,
        model_name: str = "deepseek-r1:7b",
        embedding_model: str = "nomic-embed-text",
        persist_directory: str = "./chroma_db",
        documents_dir: str = "./documents"
    ):
        self.model_name = model_name
        self.embedding_model = embedding_model
        self.persist_directory = persist_directory
        self.documents_dir = documents_dir
        
        self.llm = OllamaLLM(model=model_name)
        self.document_processor = DocumentProcessor()
        self.vector_store_manager = VectorStoreManager(
            persist_directory=persist_directory,
            embedding_model=embedding_model
        )
        
        self.prompt = PromptTemplate(
            template=SYSTEM_PROMPT,
            input_variables=["context", "question"]
        )
        
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        self.qa_chain: Optional[ConversationalRetrievalChain] = None
    
    def load_knowledge_base(self):
        self.vector_store_manager.load_vectorstore()
    
    def build_knowledge_base(self, file_paths: Optional[List[str]] = None):
        if file_paths:
            docs = self.document_processor.process_files(file_paths)
        else:
            docs = self.document_processor.process_directory(self.documents_dir)
        
        if docs:
            self.vector_store_manager.create_vectorstore(docs)
            print(f"知识库构建完成，共处理 {len(docs)} 个文档")
        else:
            print("未找到可处理的文档")
    
    def add_documents_to_knowledge_base(self, file_paths: List[str]):
        docs = self.document_processor.process_files(file_paths)
        if docs:
            self.vector_store_manager.add_documents(docs)
            print(f"已添加 {len(docs)} 个文档到知识库")
        else:
            print("未找到可添加的文档")
    
    def _init_qa_chain(self):
        retriever = self.vector_store_manager.get_retriever(k=3)
        if retriever is None:
            raise Exception("向量数据库未初始化，请先构建知识库")
        
        self.qa_chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=retriever,
            memory=self.memory,
            combine_docs_chain_kwargs={"prompt": self.prompt},
            verbose=False
        )
    
    def query(self, question: str) -> str:
        if self.qa_chain is None:
            self._init_qa_chain()
        
        try:
            result = self.qa_chain({"question": question})
            answer = result.get("answer", "").strip()
            
            if not answer or "未找到相关答案" in answer or "无法回答" in answer:
                docs = self.vector_store_manager.similarity_search(question, k=3)
                if docs:
                    context = "\n\n".join([doc.page_content for doc in docs])
                    prompt = SYSTEM_PROMPT.format(context=context, question=question)
                    answer = self.llm.invoke(prompt)
                else:
                    answer = "文档中未找到相关答案"
            
            return answer
        except Exception as e:
            print(f"查询失败: {str(e)}")
            return "文档中未找到相关答案"
    
    def get_knowledge_base_stats(self) -> Dict:
        return self.vector_store_manager.get_collection_stats()
    
    def clear_chat_history(self):
        self.memory.clear()
    
    def get_chat_history(self):
        return self.memory.chat_memory.messages

def main():
    print("RAG问答系统 - 命令行模式")
    print("=" * 50)
    
    qa_system = RAGQASystem()
    
    qa_system.load_knowledge_base()
    
    stats = qa_system.get_knowledge_base_stats()
    print(f"当前知识库状态: {stats['document_count']} 个文档, {stats['chunk_count']} 个文本块")
    
    if stats['chunk_count'] == 0:
        print("知识库为空，正在尝试构建...")
        qa_system.build_knowledge_base()
        stats = qa_system.get_knowledge_base_stats()
        print(f"知识库构建完成: {stats['document_count']} 个文档, {stats['chunk_count']} 个文本块")
    
    print("\n输入问题进行问答（输入 'exit' 退出）")
    print("-" * 50)
    
    while True:
        question = input("提问: ")
        if question.lower() == 'exit':
            break
        
        if not question.strip():
            continue
        
        print("思考中...")
        answer = qa_system.query(question)
        print(f"回答: {answer}")
        print("-" * 50)

if __name__ == "__main__":
    main()