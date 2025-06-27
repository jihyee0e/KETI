import pandas as pd
from pandasai.llm.local_llm import LocalLLM
from pandasai import Agent
import streamlit as st

llm = LocalLLM(
    api_base="http://localhost:11434/v1",
    model="llama3.1:8b",
    temperature=0.3
)

st.set_page_config(layout="wide")

uploaded_files = st.file_uploader("CSV file upload", type=['csv'], accept_multiple_files=True)

if uploaded_files is not None:
    for idx, file in enumerate(uploaded_files):
        data = pd.read_csv(file)
        st.write(f"파일 미리보기:")
        st.write(data.head(3))
        
        # 예시 질문 안내문 추가
        st.markdown("""
            > 💡 **예시 질문**
            > - What is the maximum Salary?
            > - Please filter the data where the department is IT.
            > - Show only the data for the year 2023.
            > 
            > ⚠️ 컬럼명과 질문을 영어로 하면 더 정확한 답변을 받을 수 있습니다.
            """)

        agent = Agent(data, config={
            "llm": llm,
            "use_docker": False,
            "use_error_correction_framework": True,
            "save_charts": False,
            "enable_cache": False,
            "enable_cache_warning": False,
        })

        prompt = st.text_area(f"질문을 입력하세요:", key=f"prompt_{idx}")

        if st.button(f"질문 보내기", key=f"button_{idx}"):
            if prompt:
                with st.spinner("응답 생성중 ...⏱"):
                    st.write(agent.chat(prompt))