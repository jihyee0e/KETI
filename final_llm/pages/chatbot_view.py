# chatbot_view.py
import streamlit as st
from components.file_manager import handle_file_upload
from agent.chatbot_agent import create_agent  # agent 생성 함수
import ollama
from langchain_ollama import ChatOllama
from utils.common import stored_dfs

def run_agent(agent, user_input: str) -> str:
    try:
        result = agent.invoke({"input": user_input}, return_intermediate_steps=True)
        steps = result.get("intermediate_steps", [])
        final_output = result.get("output", "").strip()
        response_parts = []

        # intermediate_steps 결과 먼저 수집
        for step in steps:
            tool_result = step[1]
            if isinstance(tool_result, str):
                cleaned = tool_result.strip()
                if cleaned and cleaned != final_output:
                    response_parts.append(cleaned)

        # 최종 응답 추가 (중복 방지됨)
        if final_output:
            response_parts.append(final_output)

        if not response_parts:
            return "⚠️ 도구가 실행되지 않았습니다. 모델이 툴을 호출하지 않았거나, 지시를 따르지 않았습니다."

        return "\n\n".join(response_parts)

    except Exception as e:
        return f"❌ 오류 발생: {e}"

# 사이드바 파일 업로드
with st.sidebar:
    st.header("🤖 모델 선택")
    models_info = ollama.list()
    models = models_info.get("models", [])
    if not models:
        st.error("사용 가능한 LLM 모델이 없습니다. Ollama 서버를 확인하세요.")
        st.stop()
    model_names = [m.model for m in models] 
    model_names.sort()

    # 세션 상태 초기화
    if "selected_model" not in st.session_state:
        st.session_state["selected_model"] = model_names[1]  # 한국어 최적화 모델

    selected_model = st.selectbox(
        "LLM 모델을 선택해주세요.",
        model_names,
        index=model_names.index(st.session_state["selected_model"]),
    )

    st.header("📂 데이터 업로드")
    uploaded_files = st.file_uploader(
        "업로드 (csv/xls[x]/json/parquet/pdf/txt)",
        type=["csv", "xls", "xlsx", "json", "parquet", "pdf", "txt"],
        accept_multiple_files=True,
    )
    df, text_only, file = handle_file_upload(uploaded_files)

    # 디버깅
    st.sidebar.text(f"[DEBUG] df is {'loaded' if df is not None else 'missing'}")

    if df is not None:
        stored_dfs["df"] = df

        if "agent_executor" not in st.session_state:
            llm = ChatOllama(model=selected_model, temperature=0)
            st.session_state["agent_executor"] = create_agent(llm, df=df)

    if selected_model != st.session_state["selected_model"]:
        st.session_state["selected_model"] = selected_model
        llm = ChatOllama(model=st.session_state["selected_model"], temperature=0)
        st.session_state["agent_executor"] = create_agent(ChatOllama(model=selected_model, temperature=0), df=df)
        st.session_state["messages"] = []

# 챗봇 UI
st.subheader("💬 LLM 챗봇")
if "messages" not in st.session_state:
    st.session_state["messages"] = []

for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("무엇을 도와드릴까요?")
if user_input:
    st.session_state["messages"].append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                agent = st.session_state["agent_executor"]
                output = run_agent(agent, user_input)
            except Exception as e:
                output = f"❌ 오류 발생: {e}"

            st.markdown(output)
            st.session_state["messages"].append({"role": "assistant", "content": output})


# import streamlit as st
# from langchain.agents import AgentExecutor
# from langchain_core.messages import AIMessage, HumanMessage
# from langchain_experimental.tools.python.tool import PythonREPLTool
# from langchain.agents import create_json_chat_agent
# from langchain import hub
# import os
# from dotenv import load_dotenv
# from agent.tool import get_all_tools  # 사용자가 정의한 커스텀 tool 모음
# from utils.common import stored_dfs    # df 저장소 (session 유지용)
# from langchain_community.llms import Ollama  # or ChatOllama
# from components.file_manager import handle_file_upload
# import streamlit as st

# st.set_page_config(page_title="챗봇", layout="wide")

# load_dotenv()

# os.environ["LANGCHAIN_TRACING_V2"] = "true"
# os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
# langchain_key = os.getenv("LANGCHAIN_API_KEY")   # .env 등록

# with st.sidebar:
#     st.header("📂 데이터 업로드")
#     uploaded_files = st.file_uploader(
#         "업로드 (csv/xls[x]/json/parquet/pdf/txt)",
#         type=["csv", "xls", "xlsx", "json", "parquet", "pdf", "txt"],
#         accept_multiple_files=True,
#     )
#     # 파일 처리 함수 호출 (app.py의 handle_file_upload 재사용)
#     df, text_only, file = handle_file_upload(uploaded_files)

# st.subheader("💬 LLM 챗봇")

# if "message" not in st.session_state:
#     st.session_state("messages") = []

# # 기존 메시지 출력
# for msg in st.session_state["messages"]:
#     with st.chat_message(msg["role"]):
#         st.markdown(msg["content"])

# user_input = st.chat_input("무엇을 도와드릴까요?")
# if user_input:
#     st.session_state["messages"].append({"role": "user", "content": user_input})
#     with st.chat_message("user"):
#         st.markdown(user_input)

# if user_input:
#     with st.chat_message("assistant"):
#         with st.spinner("Thinking..."):
#             try:
#                 # 업로드된 데이터가 있으면 agent에 넘김
#                 agent = create_agent(llm, df=df)
#                 result = agent.invoke({"input": user_input})
#                 output = result.get("output", "⚠️ 응답 없음")
#             except Exception as e:
#                 output = f"❌ 오류 발생: {e}"

#             st.markdown(output)
#             st.session_state["messages"].append({"role": "assistant", "content": output})


# def create_agent(llm, df=None):
#     tools = get_all_tools()

#     if df is not None:
#         stored_dfs["df"] = df
#         tools.append(PythonREPLTool(locals={"df": df}))

#     prompt = hub.pull("test-template")
#     agent = create_json_chat_agent(llm, tools, prompt)

#     return AgentExecutor(
#         agent=agent,
#         tools=tools,
#         verbose=True,
#         max_iterations=5,
#         max_execution_time=300,
#         handle_parsing_errors=True,
#         return_intermediate_steps=False,
#     )

# def render(df, text_only, llm):
#     st.subheader("💬 LLM 챗봇")

#     if "messages" not in st.session_state:
#         st.session_state["messages"] = []

#     for msg in st.session_state["messages"]:
#         with st.chat_message(msg["role"]):
#             st.markdown(msg["content"])

#     user_input = st.chat_input("무엇을 도와드릴까요?")
#     if user_input:
#         st.session_state["messages"].append({"role": "user", "content": user_input})
#         with st.chat_message("user"):
#             st.markdown(user_input)

#         with st.chat_message("assistant"):
#             with st.spinner("Thinking..."):
#                 try:
#                     agent = create_agent(llm, df=df)
#                     result = agent.invoke({"input": user_input})
#                     output = result.get("output", "⚠️ 응답 없음")
#                 except Exception as e:
#                     output = f"❌ 오류 발생: {e}"

#                 st.markdown(output)
#                 st.session_state["messages"].append({"role": "assistant", "content": output})
