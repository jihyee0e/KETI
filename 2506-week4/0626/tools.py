# csv 불러오기 - pandas로 정리하기 - 필요한 연산하기 - 그래프 보여주기
# 이에 맞는 도구 필요
import streamlit as st
from langchain.tools.python.tool import PythonAstREPLTool
from langchain.agents import initialize_agent, AgentType
from langchain.chat_models import ChatOpenAI
from langchain.tools import tool

# 공통 유틸: CSV 가져오기
def get_csv():
    """
    세션에서 업로드된 csv 가져오기. 없으면 예외 발생
    """
    if "df" not in st.session_state:  # 데이터프레임이 없는 경우 처리
        raise ValueError("No csv file has been uploaded yet.")
    # 사용자가 업로드한 csv 파일 pandas로 읽음
    return st.session_state.df  # 파일 매번 새로 읽거나 전달하지 않고 계속 참조

# Python 실행기 + LLM Agent 초기화 (공통)
# langchain에서 제공하는 파이썬 실행기 -> LLM이 생성할 코드 안에서 df라는 이름을 쓸 수 있게 연결해주는 부분
repl = PythonAstREPLTool()
# langchain agent 구성
llm = ChatOpenAI(temperature=0)  # LLM이 코드를 생성하고 실행기를 사용할 수 있도록 연결
agent = initialize_agent(tools=[repl], llm=llm, 
                        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
                        verbose=True)


@tool
# 기능1. csv 파일에 대한 요약 정보 반환
def summarize_csv() -> str:
    """
    업로드된 csv 파일에 대한 요약 정보를 반환합니다.
    - 행/열 수, 열 이름
    - 결측치 존재 여부
    - 수치형 컬럼의 통계 요약 포함
    """
    try:
        df = get_csv()
    except ValueError as e:
        return "먼저 CSV 파일을 업로드해주세요."
    
    summarize_lines = []  # 출력할 문장 모아둘 리스트
    
    # 기능1-1. 기본 정보 요약: 행/열 수, 열 이름
    summarize_lines.append(f"총 {df.shape[0]}개의 행과 {df.shape[1]}개의 열이 있습니다.")
    summarize_lines.append(f"열 목록: {', '.join(df.columns)}")

    # 기능1-2. 결측치 여부; 있다면 각 열에 얼마나 있는지
    null_counts = df.isnull().sum()
    null_info = null_counts[null_counts > 0]
    
    if not null_info.empty:
        summarize_lines.append("\n 결측치가 있는 열: ")
        for col, cnt in null_info.items():
            summarize_lines.append(f"  - {col}: {cnt}개")
    else:
        summarize_lines.append("\n 해당 파일에는 결측치는 없습니다.")
        
    
    # 기능2. 데이터프레임 간단 통계 요약 제공 (수치형 컬럼)
    numeric_cols = df.select_dtypes(include="number")
    
    if not numeric_cols.empty:
        stats = numeric_cols.describe().T[["mean", "std", "max", "min"]]
        summarize_lines.append("\n 주요 수치형 열 요약: ")
        for col in stats.index:
            s = stats.loc[col]
            summarize_lines.append(f"  - {col}: 평균={s['mean']: .2f}, 
                                표준편차={s['std']: .2f},
                                최대={s['max']: .2f}.
                                최소={s['min']: .2f}")
    else:
        summarize_lines.append("\n 해당 파일에는 수치형 데이터가 없습니다.")
    
    # 하나의 리스트로 반환해서 Agent에 등록
    return "\n".join(summarize_lines)
        
        
@tool
# 자연어 설명을 기반으로 시각화 코드 생성 + 실행
def visualize_from_query(query: str) -> str:
    """
    사용자의 자연어 요청을 바탕으로 시각화 코드를 생성하고 실행합니다.
    ex) '연도별 판매량을 꺾은선 그래프로 보여줘.'
    """
    try:
        df = get_csv()
    except ValueError as e:
        return "먼저 CSV 파일을 업로드해주세요."
    
    repl.locals = {"df": df}  # df를 코드 내부에서 쓸 수 있게 전달
    
    try:
        response = agent.run(query)
        return response
    except Exception as e:
        return f"[오류] 시각화 실행 실패: {str(e)}"


# 모든 tool 묶어서 반환
def get_all_tools():
    return [summarize_csv, visualize_from_query]