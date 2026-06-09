import os
from typing import List, Dict, Optional
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
try:
    from langchain.text_splitter import RecursiveCharacterTextSplitter
except ImportError:
    from langchain_classic.text_splitter import RecursiveCharacterTextSplitter

class VectorStoreManager:
    def __init__(
        self,
        persist_directory: str = "./chroma_db",
        embedding_model: str = "nomic-embed-text",
        chunk_size: int = 1000,
        chunk_overlap: int = 200
    ):
        self.persist_directory = persist_directory
        self.embedding_model = embedding_model
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        self.embeddings = OllamaEmbeddings(model=embedding_model)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        self.vectorstore: Optional[Chroma] = None
    
    def split_documents(self, documents: List[Dict]) -> List[Document]:
        all_chunks = []
        for doc in documents:
            chunks = self.text_splitter.split_text(doc['content'])
            for i, chunk in enumerate(chunks):
                doc_chunk = Document(
                    page_content=chunk,
                    metadata={
                        'filename': doc['filename'],
                        'chunk_index': i,
                        'total_chunks': len(chunks)
                    }
                )
                all_chunks.append(doc_chunk)
        return all_chunks
    
    def create_vectorstore(self, documents: List[Dict]) -> Chroma:
        chunks = self.split_documents(documents)
        print(f"正在创建向量数据库，共 {len(chunks)} 个文本块")
        
        self.vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=self.embeddings,
            persist_directory=self.persist_directory
        )
        print("向量数据库创建完成")
        return self.vectorstore
    
    def load_vectorstore(self) -> Optional[Chroma]:
        if os.path.exists(self.persist_directory):
            self.vectorstore = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings
            )
            print("向量数据库加载完成")
            return self.vectorstore
        else:
            print("向量数据库不存在")
            return None
    
    def add_documents(self, documents: List[Dict]) -> None:
        if self.vectorstore is None:
            self.load_vectorstore()
        
        if self.vectorstore is None:
            self.create_vectorstore(documents)
        else:
            chunks = self.split_documents(documents)
            print(f"正在添加 {len(chunks)} 个文本块到向量数据库")
            self.vectorstore.add_documents(chunks)
            print("文档添加完成")
    
    def similarity_search(self, query: str, k: int = 3) -> List[Document]:
        if self.vectorstore is None:
            self.load_vectorstore()
        
        if self.vectorstore is None:
            print("向量数据库未初始化")
            return []
        
        results = self.vectorstore.similarity_search(query, k=k)
        return results
    
    def get_retriever(self, k: int = 3):
        if self.vectorstore is None:
            self.load_vectorstore()
        
        if self.vectorstore is None:
            return None
        
        return self.vectorstore.as_retriever(search_kwargs={"k": k})
    
    def get_collection_stats(self) -> Dict:
        if self.vectorstore is None:
            self.load_vectorstore()
        
        if self.vectorstore is None:
            return {'document_count': 0, 'chunk_count': 0}
        
        try:
            docs = self.vectorstore.get()
            chunk_count = len(docs.get('ids', []))
            
            metadatas = docs.get('metadatas', [])
            filenames = set()
            for meta in metadatas:
                if isinstance(meta, dict) and 'source' in meta:
                    filenames.add(meta['source'])
                elif isinstance(meta, dict) and 'filename' in meta:
                    filenames.add(meta['filename'])
            
            doc_count = len(filenames) if filenames else 0
            return {
                'document_count': doc_count,
                'chunk_count': chunk_count
            }
        except Exception as e:
            print(f"获取统计信息失败: {str(e)}")
            return {'document_count': 0, 'chunk_count': 0}
    
    def clear_vectorstore(self):
        if os.path.exists(self.persist_directory):
            import shutil
            shutil.rmtree(self.persist_directory)
            self.vectorstore = None
            print("向量数据库已清空")

if __name__ == "__main__":
    from document_processor import DocumentProcessor
    
    processor = DocumentProcessor()
    docs = processor.process_directory("./documents")
    
    if docs:
        vector_manager = VectorStoreManager()
        vector_manager.create_vectorstore(docs)
        
        stats = vector_manager.get_collection_stats()
        print(f"\n向量数据库统计: {stats}")
        
        query = "什么是自然语言处理？"
        results = vector_manager.similarity_search(query, k=3)
        print(f"\n检索结果 ({len(results)}条):")
        for i, result in enumerate(results):
            print(f"\n结果 {i+1}:")
            print(f"来源: {result.metadata.get('filename', '未知')}")
            print(f"内容: {result.page_content[:150]}...")