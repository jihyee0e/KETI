# chatbot_agent.py
from operator import truediv
from .tool import get_all_tools
from langchain_experimental.tools.python.tool import PythonAstREPLTool
from utils.common import stored_dfs    # df 저장소 (session 유지용)
from langchain import hub
import os
from dotenv import load_dotenv
import streamlit as st
from langchain.agents import AgentExecutor, create_json_chat_agent

load_dotenv()
print("LANGCHAIN_API_KEY:", os.getenv("LANGCHAIN_API_KEY"))

os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
api_key = os.getenv("LANGCHAIN_API_KEY")

# 파이썬 코드를 실행하는 도구 생성
python_tool = PythonAstREPLTool()
if "messages" not in st.session_state:
    st.session_state["messages"] = []

def create_agent(llm, df=None):
    tools = get_all_tools()
    python_tool = PythonAstREPLTool(locals={"df": stored_dfs.get("df")})
    tools = tools + [python_tool]

    prompt = hub.pull("test-template")
    print("[prompt input_variables]", prompt.input_variables)

    agent = create_json_chat_agent(llm, tools, prompt)

    return AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        max_iterations=3,
        max_execution_time=300,
        handle_parsing_errors=True,
        return_intermediate_steps=True,
        # early_stopping_method="generate"  
    )