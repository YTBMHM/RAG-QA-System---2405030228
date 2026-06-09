import streamlit as st
import os
import tempfile

from rag_qa import RAGQASystem

def init_session_state():
    if 'qa_system' not in st.session_state:
        st.session_state.qa_system = RAGQASystem()
        st.session_state.qa_system.load_knowledge_base()
    
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    if 'kb_built' not in st.session_state:
        st.session_state.kb_built = False
    
    if 'uploaded_files' not in st.session_state:
        st.session_state.uploaded_files = []
    
    update_kb_info()

def update_kb_info():
    if 'qa_system' in st.session_state:
        st.session_state.kb_info = st.session_state.qa_system.get_knowledge_base_stats()

def main():
    st.set_page_config(
        page_title="RAG问答系统",
        page_icon="📚",
        layout="wide"
    )
    
    st.markdown("""
    <style>
    .stApp {
        background-color: #FFF8DC;
    }
    section[data-testid="stSidebar"] {
        background-color: #F5DEB3;
        flex: 1;
        min-width: 200px;
        max-width: 280px;
    }
    [data-testid="stSidebar"] > div:first-child {
        width: 100% !important;
    }
    section[data-testid="stMain"] {
        flex: 5;
        background-color: #FFFACD;
    }
    .main .block-container {
        background-color: #FFFACD;
        padding: 2rem;
    }
    .st-emotion-cache-18ni7ap {
        display: flex;
        width: 100%;
    }
    .stInfo, .stSuccess, .stWarning {
        background-color: #FFF8DC;
        border-color: #DEB887;
    }
    .stButton > button {
        background-color: #DEB887;
        color: #8B4513;
        border-color: #D2691E;
    }
    .stButton > button:hover {
        background-color: #F5DEB3;
    }
    h1, h2, h3 {
        color: #8B4513;
    }
    .stTextInput > div > div > input {
        background-color: #FFFACD;
        border-color: #DEB887;
    }
    .stFileUploader {
        background-color: #FFFACD;
    }
    </style>
    """, unsafe_allow_html=True)
    
    init_session_state()
    
    with st.sidebar:
        st.title("📚 RAG问答系统")
        st.markdown("---")
        
        st.subheader("知识库状态")
        update_kb_info()
        st.info(f"📄 文档数量: {st.session_state.kb_info['document_count']}")
        st.info(f"🧩 文本块数量: {st.session_state.kb_info['chunk_count']}")
        
        st.markdown("---")
        
        st.subheader("文档上传")
        uploaded_files = st.file_uploader(
            "选择PDF或DOCX文件",
            type=["pdf", "docx"],
            accept_multiple_files=True,
            key="file_uploader"
        )
        
        if uploaded_files:
            st.session_state.uploaded_files = uploaded_files
            st.success(f"已选择 {len(uploaded_files)} 个文件")
        
        if st.button("🔨 构建/更新知识库", type="primary"):
            if uploaded_files:
                with st.spinner("正在处理文档..."):
                    temp_dir = tempfile.mkdtemp()
                    file_paths = []
                    
                    for uploaded_file in uploaded_files:
                        file_path = os.path.join(temp_dir, uploaded_file.name)
                        with open(file_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                        file_paths.append(file_path)
                    
                    st.session_state.qa_system.build_knowledge_base(file_paths)
                    st.session_state.kb_built = True
                    update_kb_info()
                    st.success("知识库构建完成！")
            else:
                st.warning("请先上传文档")
        
        if st.button("🗑️ 清空知识库"):
            st.session_state.qa_system.vector_store_manager.clear_vectorstore()
            st.session_state.kb_built = False
            st.session_state.chat_history = []
            update_kb_info()
            st.success("知识库已清空")
        
        if st.button("🧹 清空对话历史"):
            st.session_state.chat_history = []
            st.session_state.qa_system.clear_chat_history()
            st.success("对话历史已清空")
        
        st.markdown("---")
        st.markdown("💡 提示: 上传文档后点击'构建知识库'开始使用")
    
    st.title("💬 问答交互")
    
    if st.session_state.chat_history:
        st.subheader("对话历史")
        for i, (question, answer) in enumerate(st.session_state.chat_history):
            with st.chat_message("user"):
                st.markdown(f"**问题:** {question}")
            with st.chat_message("assistant"):
                st.markdown(f"**回答:** {answer}")
            st.markdown("---")
    
    st.subheader("提问")
    question = st.text_input("请输入你的问题:", key="question_input")
    
    if st.button("发送", type="primary"):
        if question.strip():
            if st.session_state.kb_info['chunk_count'] == 0:
                st.warning("知识库为空，请先上传文档并构建知识库")
            else:
                with st.spinner("正在思考..."):
                    answer = st.session_state.qa_system.query(question)
                    st.session_state.chat_history.append((question, answer))
                    st.rerun()
        else:
            st.warning("请输入问题")

if __name__ == "__main__":
    main()