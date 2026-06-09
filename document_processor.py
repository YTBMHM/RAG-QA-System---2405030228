import os
from typing import List, Dict
import PyPDF2
from docx import Document

class DocumentProcessor:
    SUPPORTED_EXTENSIONS = ['.pdf', '.docx', '.txt']
    
    def __init__(self):
        pass
    
    def extract_text_from_pdf(self, file_path: str) -> str:
        text = ""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            print(f"读取PDF文件失败 {file_path}: {str(e)}")
        return text
    
    def extract_text_from_docx(self, file_path: str) -> str:
        text = ""
        try:
            doc = Document(file_path)
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
        except Exception as e:
            print(f"读取DOCX文件失败 {file_path}: {str(e)}")
        return text
    
    def extract_text_from_txt(self, file_path: str) -> str:
        text = ""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()
        except Exception as e:
            print(f"读取TXT文件失败 {file_path}: {str(e)}")
        return text
    
    def extract_text(self, file_path: str) -> str:
        ext = os.path.splitext(file_path)[1].lower()
        if ext == '.pdf':
            return self.extract_text_from_pdf(file_path)
        elif ext == '.docx':
            return self.extract_text_from_docx(file_path)
        elif ext == '.txt':
            return self.extract_text_from_txt(file_path)
        else:
            print(f"不支持的文件格式: {ext}")
            return ""
    
    def process_directory(self, directory: str) -> List[Dict]:
        documents = []
        if not os.path.exists(directory):
            print(f"目录不存在: {directory}")
            return documents
        
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            ext = os.path.splitext(filename)[1].lower()
            
            if ext in self.SUPPORTED_EXTENSIONS:
                print(f"正在处理: {filename}")
                text = self.extract_text(file_path)
                if text.strip():
                    documents.append({
                        'filename': filename,
                        'content': text,
                        'file_path': file_path
                    })
                else:
                    print(f"警告: 文件内容为空 {filename}")
        
        print(f"共处理 {len(documents)} 个文档")
        return documents
    
    def process_files(self, file_paths: List[str]) -> List[Dict]:
        documents = []
        for file_path in file_paths:
            if os.path.exists(file_path):
                filename = os.path.basename(file_path)
                ext = os.path.splitext(filename)[1].lower()
                
                if ext in self.SUPPORTED_EXTENSIONS:
                    print(f"正在处理: {filename}")
                    text = self.extract_text(file_path)
                    if text.strip():
                        documents.append({
                            'filename': filename,
                            'content': text,
                            'file_path': file_path
                        })
                else:
                    print(f"跳过不支持的文件格式: {filename}")
            else:
                print(f"文件不存在: {file_path}")
        
        return documents

if __name__ == "__main__":
    processor = DocumentProcessor()
    
    test_dir = "./documents"
    docs = processor.process_directory(test_dir)
    
    for doc in docs:
        print(f"\n文件名: {doc['filename']}")
        print(f"内容长度: {len(doc['content'])} 字符")
        print("前200字符:")
        print(doc['content'][:200] + "..." if len(doc['content']) > 200 else doc['content'])