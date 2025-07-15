import streamlit as st
import matplotlib.pyplot as plt

def render():
    st.subheader("📊 대시보드")

    # 1️⃣ 파일 선택 UI
    df_keys = [k for k in st.session_state.keys() if k.endswith("_df")]
    if not df_keys:
        st.warning("⚠️ 시각화 가능한 DataFrame이 없습니다.")
        return

    selected_key = st.selectbox("📄 시각화할 데이터 선택", df_keys)
    df = st.session_state[selected_key]

    # 2️⃣ 컬럼 선택
    selected_col = st.selectbox("기준 컬럼 선택", df.columns)
    value_col = st.selectbox("값 컬럼 선택", df.select_dtypes(include="number").columns)
    agg_fn = st.selectbox("집계 함수", ["count", "sum", "mean"])
    chart_type = st.radio("차트 종류", ["bar", "line", "pie"])

    # 3️⃣ 시각화
    try:
        grouped = df.groupby(selected_col)[value_col].agg(agg_fn)

        if grouped.index.name in df.columns:
            grouped.index.name = None
        grouped = grouped.reset_index()

        fig, ax = plt.subplots()
        if chart_type == "bar":
            ax.bar(grouped[selected_col], grouped[value_col])
        elif chart_type == "line":
            ax.plot(grouped[selected_col], grouped[value_col], marker="o")
        elif chart_type == "pie":
            ax.pie(grouped[value_col], labels=grouped[selected_col], autopct="%1.1f%%")
            ax.axis("equal")

        ax.set_title(f"{agg_fn.upper()} of {value_col} by {selected_col}")
        st.pyplot(fig)

    except Exception as e:
        st.error(f"⚠️ 차트 생성 오류: {e}")
