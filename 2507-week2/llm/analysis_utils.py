# analysis_utils.py
import streamlit as st
import pandas as pd
import io
import contextlib
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import re
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import fitz  # PyMuPDF
import hashlib

# 사용자 폰트 경로
font_path = "/home/jihye0e/.fonts/NanumGothicCoding.ttf"
fontprop = fm.FontProperties(fname=font_path)
# 한글 폰트 적용
plt.rcParams['font.family'] = fontprop.get_name()
# 마이너스(-) 깨짐 방지
plt.rcParams['axes.unicode_minus'] = False

def get_file_hash(file):
    file.seek(0)
    file_bytes = file.read()
    file.seek(0)
    return hashlib.md5(file_bytes).hexdigest()

def extract_text_from_file(file, sidebar_mode=False, idx=None, warn_duplicate=True):
    ui = st.sidebar if sidebar_mode else st

    try:
        file.seek(0)
    except Exception:
        pass  # 일부 Streamlit 파일 객체는 seek 불가할 수 있음

    # CSV 파일 처리
    if file.name.endswith(".csv"):
        try:
            df = pd.read_csv(file)
            if warn_duplicate:
                ui.success(f"✅ CSV file upload successful: {file.name}")
            ui.write("Top 3 rows preview")
            ui.dataframe(df.head(3), use_container_width=True, key=f"csv_preview_{file.name}_{str(id(idx))}")
            return df, df.to_csv(index=False), "csv"
        except Exception as e:
            ui.error(f"❌ Failed to load CSV file: {e}")
            return None, None, None

    # PDF 파일 처리
    elif file.name.endswith(".pdf"):
        try:
            file.seek(0)  
            with fitz.open(stream=file.read(), filetype="pdf") as doc:
                text = "\n".join(page.get_text() for page in doc)
            if warn_duplicate:
                ui.success(f"✅ PDF file upload successful: {file.name}")
                ui.text_area("📄 Extracted text", text[:100], height=200, key=f"pdf_preview_{file.name}_{idx}_{str(id(file))}")
            return None, text, "pdf"
        except Exception as e:
            ui.error(f"❌ Failed to load pdf file: {e}")
            return None, None, None

    # TXT 파일 처리
    elif file.name.endswith(".txt"):
        try:
            file.seek(0)
            text = file.read().decode("utf-8")
            if warn_duplicate:
                ui.success(f"✅ TXT file upload successful: {file.name}")
                ui.text_area("📄 File content", text[:100], height=200, key=f"txt_preview_{file.name}_{idx}_{str(id(file))}")
            return None, text, "txt"
        except UnicodeDecodeError:
            try:
                file.seek(0)
                text = file.read().decode("cp949")
                if warn_duplicate:
                    ui.success(f"✅ TXT file upload successful: {file.name}")
                    ui.text_area("📄 File content", text[:100], height=200, key=f"txt_preview_{file.name}_{idx}_{str(id(file))}")
                return None, text, "txt"
            except Exception as e:
                ui.error(f"❌ Failed to load txt file: {e}")
                return None, None, None
        except Exception as e:
            ui.error(f"❌ Failed to load txt file: {e}")
            return None, None, None

    # 지원하지 않는 포맷
    else:
        ui.warning(f"⚠️ Unsupported file format: {file.name}")
        return None, None, None


def robust_code_extractor(llm_output):
    code_blocks = re.findall(r"```(?:python)?\n(.*?)```", llm_output, re.DOTALL)
    if code_blocks:
        return code_blocks[0].strip()
    lines = llm_output.splitlines()
    code_lines = []
    for line in lines:
        l = line.strip()
        if l and (l.startswith(("import","def", "for", "if", "print", "df", "max", "min", "plt", "return")) or "=" in l):
            code_lines.append(line)
    return "\n".join(code_lines).strip()

def run_analysis(df, content, filetype, llm, prompt_key="default", button_key="default", unique_id=""):
    st.markdown("### 💬 Ask a question about your data:")
    st.markdown(
            """
            > 💡 **Example Questions**
            > - What is the maximum Salary?
            > - Please filter the data where the department is IT.
            > - 2023년 데이터만 보여줘.
            """
    )

    # prompt = st.text_area(" ", key=prompt_key)
    prompt = st.text_area(" ", value=st.session_state.get(prompt_key, ""), key=prompt_key)
    template = """
        You are a skilled data analyst. The user will ask a question in Korean.

        Below is the user's data:
        {data}

        Below is the user's question:
        {question}

        If the user's question is a general greeting, small talk, or not related to data analysis, generate a polite Korean response 
        and assign it to a variable named `result_text`, and set `result = None`.
        Otherwise, write Python code using pandas to answer the question.
        Use the provided variable 'df' directly. Do NOT reload or redefine the data.

        Store the main result in a variable named `result`.
        Also generate a Korean explanation string and store it in `result_text`. 
        The explanation should describe the exact process of how the result was calculated (e.g., filtering conditions, aggregation, groupings, etc). 
        Do not guess—base it strictly on the actual values in `result`.
        Make sure the values used in the explanation exactly match what’s shown in `result`.

        If the answer includes a plot, use matplotlib and show the plot.
        Only output the code, do not explain.
        """


    st.markdown("""
        <style>
        .stButton > button {
            white-space: nowrap;
            margin-right: 8px;
        }
        </style>
    """, unsafe_allow_html=True)

    col1, col2, _ = st.columns([1, 1, 6])
    with col1:
        # submit_clicked = st.button("Submit", key=button_key)
        submit_clicked = st.button("Submit", key=f"{button_key}_submit_{unique_id}")
    with col2:
        # reset_clicked = st.button("Reset conversation", key=f"reset_{button_key}")
        reset_clicked = st.button("Reset conversation", key=f"reset_{button_key}_{unique_id}")

    if reset_clicked:
        for k in [prompt_key, f"input_text_{prompt_key}"]:
            if k in st.session_state:
                del st.session_state[k]
        st.rerun()

    if submit_clicked and prompt:
        # if st.button("Submit question", key=button_key):
        # if st.button("Submit", key=f"{button_key}_question_{unique_id}"):
        if prompt:
            with st.spinner("Generating response...⏱"):
                chain = LLMChain(
                    llm=llm, prompt=PromptTemplate.from_template(template)
                )

                if f"input_text_{prompt_key}" not in st.session_state:
                    if filetype == "csv" and len(content) > 16000:
                        content = df.sample(100).to_csv(index=False)
                    st.session_state[f"input_text_{prompt_key}"] = content
                else:
                    content = st.session_state[f"input_text_{prompt_key}"]

                llm_output = chain.run({"data": content, "question": prompt})
                code = robust_code_extractor(llm_output)
                code = re.sub(r".*pd\\.read_csv\\(.*\\)\\s*", "", code)

                try:
                    local_vars = {"df": df, "pd": pd}
                    with contextlib.redirect_stdout(io.StringIO()) as f:
                        exec(code, local_vars)
                    output = f.getvalue()

                    if "result" in local_vars:
                        result = local_vars["result"]
                        st.write("📊 **Analysis result:**")
                        if isinstance(result, pd.DataFrame):
                            st.dataframe(result, use_container_width=True)
                        else:
                            st.write(result)
                    if "result_text" in local_vars:
                        st.markdown("📝 **설명 결과:**")
                        st.write(local_vars["result_text"])

                    if plt.get_fignums():
                        st.write("📈 **Visualization result:**")
                        st.pyplot(plt.gcf())
                        plt.clf()

                    elif output.strip():
                        st.write("📋 **Output result:**")
                        st.write(output)

                except Exception as e:
                    st.error(f"❌ Error during code execution: {e}")
                    st.write("**Generated code:**")
                    st.code(code, language="python")

def display_uploaded_files(uploaded_files, llm, key_prefix="default", sidebar_mode=False):
    ui = st.sidebar if sidebar_mode else st

    if not uploaded_files:
        return

    latest = uploaded_files[-1]
    previous = uploaded_files[:-1]  

    # 확인용
    print("latest:", latest.name)
    print("previous:", [f.name for f in previous])

    latest_idx = 0
    df, content, filetype = extract_text_from_file(
        latest, sidebar_mode=sidebar_mode, idx=latest_idx, warn_duplicate=True
    )

    if previous:
        st.markdown("📂 View previous uploaded files")
        for idx, file in enumerate(reversed(previous), start=1):
            with st.expander(f"📄 Open {file.name}"):
                # st.write(f"이전 파일: {file.name}")
                extract_text_from_file(file, sidebar_mode=False, idx=idx, warn_duplicate=True)

    if content:
        run_analysis(
            df, content, filetype, llm,
            # prompt_key=f"question_{key_prefix}",
            # button_key=f"button_{key_prefix}"
            prompt_key=f"question_{key_prefix}_{latest.name}_{latest_idx}",
            button_key=f"button_{key_prefix}_{latest.name}_{latest_idx}",
            unique_id=f"{latest.name}_{latest_idx}"
        )

# test 
# 총 금액과 가장 비싼 물품 알려줘.