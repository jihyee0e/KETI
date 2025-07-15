# components/file_manager.py
from utils.file_utils import deduplicate_files
import streamlit as st
import pandas as pd
import fitz  # PyMuPDF

def handle_file_upload(uploaded_files):
    """중복 제거 + 최신 파일 미리보기 + 세션 저장 후 df/text/file 반환"""
    df, text_only, file = None, None, None

    if uploaded_files:
        unique_files, duplicates = deduplicate_files(uploaded_files)

        # 중복 경고
        if duplicates:
            st.sidebar.warning(f"⚠️ 중복 파일이 있습니다.: {', '.join(duplicates)}")

        if unique_files:
            file = unique_files[-1]  # 최신 파일
            ext = file.name.split(".")[-1].lower()

            try:
                if ext == "csv":
                    df = pd.read_csv(file)
                elif ext in ["xls", "xlsx"]:
                    df = pd.read_excel(file)
                elif ext == "json":
                    df = pd.read_json(file)
                elif ext == "parquet":
                    df = pd.read_parquet(file)
                elif ext == "pdf":
                    file.seek(0)
                    with fitz.open(stream=file.read(), filetype="pdf") as doc:
                        text_only = "\n".join(p.get_text() for p in doc)
                elif ext == "txt":
                    file.seek(0)
                    text_only = file.read().decode("utf-8", errors="ignore")
            except Exception as e:
                st.error(f"❌ 로딩 실패: {e}")

            # 세션 상태 공유
            st.session_state["uploaded_file"] = file
            st.session_state["uploaded_df"] = df
            st.session_state["uploaded_text"] = text_only

    # ── 미리보기 ──────────────────
    if file:
        st.markdown(f"### ✅ 미리보기: `{file.name}`")
        if df is not None:
            st.dataframe(df.head(), use_container_width=True)
        elif text_only:
            st.text_area("", text_only[:300], height=150)

        # 더보기
        if len(uploaded_files) > 1:
            st.markdown("---")
            st.markdown("📂 더보기")
            for f in unique_files[:-1]:
                with st.expander(f"📄 {f.name}"):
                    ext = f.name.split(".")[-1].lower()
                    try:
                        if ext == "csv":
                            st.dataframe(pd.read_csv(f).head(), use_container_width=True)
                        elif ext in ["xls", "xlsx"]:
                            st.dataframe(pd.read_excel(f).head(), use_container_width=True)
                        elif ext == "json":
                            st.dataframe(pd.read_json(f).head(), use_container_width=True)
                        elif ext == "parquet":
                            st.dataframe(pd.read_parquet(f).head(), use_container_width=True)
                        elif ext == "pdf":
                            f.seek(0)
                            with fitz.open(stream=f.read(), filetype="pdf") as doc:
                                text = "\n".join(p.get_text() for p in doc)
                                st.text_area("", text[:300], height=150)
                        elif ext == "txt":
                            f.seek(0)
                            st.text_area("", f.read().decode("utf-8", errors="ignore")[:300], height=150)
                    except Exception as e:
                        st.error(f"❌ 미리보기 실패: {e}")
    else:
        st.info("파일을 업로드해 주세요.")

    return df, text_only, file
