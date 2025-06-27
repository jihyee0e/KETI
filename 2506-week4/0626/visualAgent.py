# 사용자가 업로드한 CSV를 바탕으로, 자연어로 질문하면 Agent가 요약·시각화 등의 결과를 반환
import streamlit as st
import pandas as pd
from langchain.agents import AgentExecutor
from langchain.tools.python.tool import PythonAstREPLTool
from langchain.agents import AgentType
from langchain.chat_models import ChatOpenAI
from tools import get_all_tools
import matplotlib.pyplot as plt

# 초기 상태 설정
if "messages" not in st.session_state:
    st.session_state["messages"] = []  # 사용자-에이전트 메시지 기록

if "history" not in st.session_state:
    st.session_state["history"] = []  # chat_history 형식 (("human", "질문"), ("ai", "응답"))

if "df" not in st.session_state:
    st.session_state["df"] = None  # 사용자가 업로드한 DataFrame

if "agent_executor" not in st.session_state:
    st.session_state["agent_executor"] = None  # 나중에 AgentExecutor 생성 시 저장

if "selected_model" not in st.session_state:
    st.session_state["selected_model"] = None  # 모델명 (예: "qwen:7b", "mistral")
    

def create_agent(model_name: str, df: pd.DataFrame) -> AgentExecutor:
    # 실행기 - df 연결
    repl = PythonAstREPLTool(locals={"df": df})
    
    # LLM
    llm = ChatOpenAI(temperature=0)  
    
    # 툴 리스트 구성
    tools = [repl] + [i for i in get_all_tools() if i.name != repl.name]
    # AgentExecutor 생성
    agent_executor = AgentExecutor(
        tools=tools,
        llm=llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=False,
        handle_parsing_errors=True,
    )
    
    return agent_executor
    
# 1) 사용자에게 CSV 파일 업로드 UI 제공
st.set_page_config(layout="wide")
st.title("CSV Analysis Agent")
uploaded_files = st.file_uploader("Upload files", accept_multiple_files=True)

if uploaded_files is not None:
    for idx, file in enumerate(uploaded_files):
        try:
            df = pd.read_csv(file)
            st.success(f"⭕️ Success File uploaded: '{file.name}'")
            st.write("Top 3 rows preview")
            st.dataframe(df.head(3), use_container_width=True)
            
            st.markdown("""
                > 💡 **Example Questions**
                > - What is the maximum Salary?
                > - Please filter the data where the department is IT.
                > - Show only the data for the year 2023.
                """)

            # 파일별로 DataFrame 저장
            st.session_state[f"df_{idx}"] = df

            # 파일별로 agent 생성 및 저장
            agent_key = f"agent_executor_{idx}"
            if agent_key not in st.session_state:
                st.session_state[agent_key] = create_agent(model_name="qwen:7b", df=df)
            agent = st.session_state[agent_key]

            # 파일별로 질문 입력창
            prompt = st.text_area("💬 Ask a question about your data:", key=f"question_{idx}")
            
            # 1-2) prompt 실행
            if st.button("질문 보내기", key=f"button_{idx}"):
                if prompt.strip():
                    with st.spinner("🤖 LLM 분석 중..."):
                        try:
                            # 실행
                            result = agent.run(prompt)
                            
                            # 일반 출력
                            if result:
                                st.markdown("**📋 결과:**")
                                st.write(result)

                            # 시각화가 있는 경우만 출력
                            if plt.get_fignums():  # figure가 하나라도 있으면
                                st.markdown("**📊 시각화 결과:**")
                                st.pyplot(plt.gcf())
                                plt.clf()

                        except Exception as e:
                            st.error(f"❌ 실행 중 오류 발생: {e}")
            
        except Exception as e:
            st.error(f"❌ Failed to load file '{file.name}': {e}")
            continue  # 다음 파일로 넘어감