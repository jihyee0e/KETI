# tool.py
from langchain.tools import tool
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from utils.common import stored_dfs  

@tool
def summarize_csv(_: str = "") -> str:
    """업로드된 CSV 파일의 기본 통계 요약을 제공합니다."""
    df = stored_dfs.get("df")
    if df is None:
        return "⚠️ 업로드된 파일이 없습니다."

    try:
        buffer = []
        buffer.append(f"✅ 행 개수: {df.shape[0]}\n")
        buffer.append(f"✅ 열 개수: {df.shape[1]}")
        buffer.append("\n📊 기본 통계 요약:")
        buffer.append(df.describe(include='all').transpose().to_markdown(index=True))
        return str("\n".join(buffer))
    except Exception as e:
        return f"⚠️ 요약 실패: {e}"

@tool
def visualize_from_query(query: str) -> str:
    """쿼리에 따라 시각화된 차트를 이미지(HTML base64)로 반환합니다."""
    df = stored_dfs.get("df")
    if df is None:
        return "⚠️ 업로드된 파일이 없습니다."

    try:
        result = df.query(query)
        if result.empty:
            return "⚠️ 쿼리 결과가 비어 있습니다."

        fig, ax = plt.subplots()
        result.value_counts().plot(kind='bar', ax=ax)
        ax.set_title("Query Result Visualization")

        buf = BytesIO()
        plt.savefig(buf, format="png")
        plt.close(fig)
        buf.seek(0)
        encoded = base64.b64encode(buf.read()).decode()
        return f"<img src='data:image/png;base64,{encoded}'/>"
    except Exception as e:
        return f"⚠️ 시각화 실패: {e}"

@tool
def process_query(query: str) -> str:
    """DataFrame에 Pandas 쿼리 실행 결과를 텍스트로 반환합니다."""
    df = stored_dfs.get("df")
    if df is None:
        return "⚠️ 업로드된 파일이 없습니다."

    try:
        result = df.query(query)
        return result.to_string(index=False)
    except Exception as e:
        return f"⚠️ 쿼리 처리 실패: {e}"

def get_all_tools():
    return [summarize_csv, visualize_from_query, process_query]
