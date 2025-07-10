import streamlit as st
import pandas as pd
from langchain_community.llms import Ollama
from analysis_utils import extract_text_from_file, robust_code_extractor, run_analysis, display_uploaded_files
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import io
import contextlib
import matplotlib.pyplot as plt
import re
import fitz  # PyMuPDF
from analysis_utils import get_file_hash

st.set_page_config(layout="wide")
st.title("Local LLM Analysis Agent")

st.sidebar.title("✅ Select version")
mode = st.sidebar.radio("모드를 선택하세요", ["Combined View", "Split View"])
st.sidebar.markdown("<br>", unsafe_allow_html=True)

llm = Ollama(
    base_url="http://localhost:11434",
    model="llama3.2:latest",
    temperature=0.3,
)

def deduplicate_files(files):
    seen_hashes = set()
    unique = []
    duplicates = []

    for file in files:
        file_hash = get_file_hash(file)
        if file_hash not in seen_hashes:
            seen_hashes.add(file_hash)
            unique.append(file)
        else:
            duplicates.append(file.name)
    return unique, duplicates

# ------------------------------
# Combined view
# ------------------------------
if mode == "Combined View":
    if "dedup_files" not in st.session_state:
        st.session_state["dedup_files"] = []
    if "duplicates" not in st.session_state:
        st.session_state["duplicates"] = []

    uploaded_files = st.file_uploader(
        "📂 Upload your files", type=["csv", "pdf", "txt"], accept_multiple_files=True
    )

    if not uploaded_files:
        st.session_state["dedup_files"] = []
        st.session_state["duplicate_names"] = []
    else:
        # dedup 갱신: 해시 기준 중복 제거
        unique_files, duplicates = deduplicate_files(uploaded_files)
        st.session_state["dedup_files"] = unique_files
        st.session_state["duplicate_names"] = list(set(duplicates))

    # 중복 경고 출력
    for dup in st.session_state.get("duplicate_names", []):
        st.warning(f"⚠️ 이미 존재하는 파일입니다: {dup}")

    if st.session_state.get("dedup_files"):
        display_uploaded_files(st.session_state["dedup_files"], llm, key_prefix="combined")

# ------------------------------
# Split view
# ------------------------------
# ------------------------------
# Split view
# ------------------------------
elif mode == "Split View":
    if "dedup_files_split" not in st.session_state:
        st.session_state["dedup_files_split"] = []
    if "duplicates_split" not in st.session_state:
        st.session_state["duplicates_split"] = []

    uploaded_files = st.sidebar.file_uploader(
        "📂 Upload your files", type=["csv", "pdf", "txt"], accept_multiple_files=True
    )
    if uploaded_files:
        unique_files, duplicates = deduplicate_files(uploaded_files)
        st.session_state["dedup_files_split"] = unique_files
        st.session_state["duplicates_split"] = list(set(duplicates))
    else:
        st.session_state["dedup_files_split"] = []
        st.session_state["duplicates_split"] = []

    for dup in st.session_state.get("duplicates_split", []):
        st.sidebar.warning(f"⚠️ 이미 존재하는 파일입니다: {dup}")

    if st.session_state["dedup_files_split"]:
        display_uploaded_files(
            st.session_state["dedup_files_split"],
            llm,
            key_prefix="split",
            sidebar_mode=True
        )