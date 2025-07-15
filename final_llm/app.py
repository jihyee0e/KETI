# app.py
import streamlit as st
from components.file_manager import handle_file_upload
# from pages import dashboard_view, chatbot_view

st.set_page_config(layout="wide")
st.title("Test")

# ───────────────────
# 파일 업로드 (사이드바)
# ───────────────────
with st.sidebar:
    st.header("📂 데이터 업로드")
    uploaded_files = st.file_uploader(
        "업로드 (csv/xls[x]/json/parquet/pdf/txt)",
        type=["csv", "xls", "xlsx", "json", "parquet", "pdf", "txt"],
        accept_multiple_files=True,
    )

# 업로드 처리 → 세션에 저장
df, text_only, file = handle_file_upload(uploaded_files)



# 2️⃣ 파일 업로드 성공 후에만 사이드바 UI 노출
# if load_ok:
#     # ─────────── 사이드바 ───────────
#     with st.sidebar:
#         st.header("⚙️ 설정")

#         # 1️⃣ 모드 선택 (항상 보임)
#         mode = st.radio("모드 선택", ["대시보드", "챗봇"])

#         # 2️⃣ 챗봇 모드일 때만 LLM 모델 선택
#         llm = None
#         if mode == "챗봇":
#             models = ollama.list()["models"]
#             model_names = sorted([m["model"] for m in models])
#             default_model = "llama-3.2-korean-bllossom-3b:latest"
#             selected_model = st.selectbox(
#                 "LLM 모델 선택",
#                 model_names,
#                 index=model_names.index(default_model) if default_model in model_names else 0,
#             )
#             llm = Ollama(
#                 base_url="http://localhost:11434",
#                 model=selected_model,
#                 temperature=0.3
#             )

#     # ─────────── 메인 영역 ───────────
#     if mode == "대시보드":
#         if df is None:
#             st.warning("⚠️ PDF / TXT 파일은 대시보드 시각화를 지원하지 않습니다.  \n사이드바에서 '챗봇' 모드로 전환해 주세요.")
#         else:
#             st.subheader("📊 대시보드")
#             # st.dataframe(df.head(), use_container_width=True)
#             # TODO: 컬럼 선택 + 차트 생성 UI 연결 (dashboard_view.render(df))
#             # 기준, 값 컬럼 선택
#             selected_col = st.selectbox("기준 컬럼 선택", df.columns, index=0)
#             value_col = st.selectbox("값 컬럼 선택", df.select_dtypes(include="number").columns, index=1)
#             agg_fn = st.selectbox("집계 함수", ["count", "sum", "mean"])
#             chart_type = st.radio("차트 종류", ["bar", "line", "pie"])

#             try:
#                 # groupby + agg
#                 grouped = df.groupby(selected_col)[value_col].agg(agg_fn)
#                 grouped.columns = [selected_col, value_col]

#                 # 충돌 방지용: index 이름이 기존 컬럼에 있으면 제거 후 reset
#                 if grouped.index.name in grouped.columns:
#                     grouped.index.name = None
#                 grouped = grouped.reset_index()

#                 # 시각화
#                 fig, ax = plt.subplots()
#                 if chart_type == "bar":
#                     ax.bar(grouped[selected_col], grouped[value_col])
#                 elif chart_type == "line":
#                     ax.plot(grouped[selected_col], grouped[value_col], marker="o")
#                 elif chart_type == "pie":
#                     ax.pie(grouped[value_col], labels=grouped[selected_col], autopct="%1.1f%%")
#                     ax.axis("equal")

#                 ax.set_title(f"{agg_fn.upper()} of {value_col} by {selected_col}")
#                 st.pyplot(fig)

#             except Exception as e:
#                 st.error(f"⚠️ 차트 생성 오류: {e}")

#     elif mode == "챗봇":
#         st.subheader("💬 챗봇")
#         # TODO: 챗봇 UI + agent 호출 (chatbot_view.render(df, text_only, llm))
#         if llm is not None:
#             chatbot_view.render(df, text_only, llm)

