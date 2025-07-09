import streamlit as st
import pandas as pd
from langchain_community.llms import Ollama  
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import io
import contextlib
import matplotlib.pyplot as plt
import re
import fitz  # PyMuPDF

# Ollama LLM 연결
llm = Ollama(
      base_url="http://localhost:11434",
    #   model="qwen2.5:14b",
    model="llama3.2:latest",
      temperature=0.3
)

st.set_page_config(layout="wide")
st.title("Local LLM Analysis Agent")

uploaded_files = st.file_uploader("📂 Upload your files", type=['csv', 'pdf', 'txt'], accept_multiple_files=True)

def extract_text_from_file(file):
    if file.name.endswith(".csv"):
        try:
            df = pd.read_csv(file)
            st.success(f"✅ CSV 파일 업로드 성공: {file.name}")
            st.write("Top 3 rows preview")
            st.dataframe(df.head(3), use_container_width=True)
            return df, df.to_csv(index=False), 'csv'
        except Exception as e:
            st.error("❌ CSV 로딩 실패")
            return None, None, None

    elif file.name.endswith(".pdf"):
        try:
            with fitz.open(stream=file.read(), filetype="pdf") as doc:
                text = "\n".join(page.get_text() for page in doc)
            st.success(f"✅ PDF 파일 업로드 성공: {file.name}")
            st.text_area("📄 추출된 텍스트", text[:100], height=200)
            return None, text, 'pdf'
        except Exception as e:
            st.error("❌ PDF 로딩 실패")
            return None, None, None

    elif file.name.endswith(".txt"):
        try:
            # 1차 시도: UTF-8 디코딩
            text = file.read().decode("utf-8")
            st.success(f"✅ TXT 파일 업로드 성공: {file.name}")
            st.text_area("📄 파일 내용", text[:100], height=200)
            return None, text, 'txt'
        except UnicodeDecodeError:
            try:
                # 2차 시도: CP949 (윈도우 한글 인코딩)
                file.seek(0)  # read 이후 포인터 리셋
                text = file.read().decode("cp949")
                st.success(f"✅ TXT 파일 업로드 성공: {file.name}")
                st.text_area("📄 파일 내용", text[:100], height=200)
                return None, text, 'txt'
            except Exception as e:
                st.error("❌ TXT 로딩 실패")
                return None, None, None
        except Exception as e:
            st.error("❌ TXT 로딩 실패")
            return None, None, None

    
    else:
        st.warning(f"⚠️ 지원하지 않는 파일 형식입니다: {file.name}")
        return None, None, None

def robust_code_extractor(llm_output):
    code_blocks = re.findall(r"```(?:python)?\n(.*?)```", llm_output, re.DOTALL)
    if code_blocks:
        return code_blocks[0].strip()
    lines = llm_output.splitlines()
    code_lines = []
    for line in lines:
        l = line.strip()
        if l and (l.startswith(("import", "def", "for", "if", "print", "df", "max", "min", "plt", "return")) or "=" in l):
            code_lines.append(line)
    return "\n".join(code_lines).strip()

if uploaded_files:
    for idx, file in enumerate(uploaded_files):
        df, content, filetype = extract_text_from_file(file)
        if not content:
            continue

        st.markdown("""
        > 💡 **Example Questions**
        > - What is the maximum Salary?
        > - Please filter the data where the department is IT.
        > - Show only the data for the year 2023.
        """)

        prompt = st.text_area("💬 Ask a question about your data:", key=f"question_{idx}")

        template = """
        You are a skilled data analyst. The user will ask a question in Korean.

        Below is the user's data:
        {data}

        Below is the user's question:
        {question}

        Write Python code using pandas to answer the question.
        Store the main result in a variable named 'result'.
        If the answer is a plot, use matplotlib and show the plot.
        Only output the code, do not explain.
        """

        if st.button(f"질문 보내기", key=f"button_{idx}"):
            if prompt:
                with st.spinner("응답 생성중 ...⏱"):
                    chain = LLMChain(
                        llm=llm,
                        prompt=PromptTemplate.from_template(template)
                    )

                    if f"input_text_{idx}" not in st.session_state:
                        if filetype == 'csv' and len(content) > 16000:
                            content = df.sample(100).to_csv(index=False)
                        st.session_state[f"input_text_{idx}"] = content
                    else:
                        content = st.session_state[f"input_text_{idx}"]

                    llm_output = chain.run({"data": content, "question": prompt})
                    code = robust_code_extractor(llm_output)
                    code = re.sub(r".*pd\.read_csv\(.*\)\s*", "", code)  

                    try:
                        local_vars = {"df": df, "pd": pd}
                        with contextlib.redirect_stdout(io.StringIO()) as f:
                            exec(code, local_vars)
                        output = f.getvalue()

                        if "result" in local_vars:
                            result = local_vars["result"]
                            if isinstance(result, pd.DataFrame):
                                st.write("📊 **분석 결과:**")
                                st.dataframe(result, use_container_width=True)
                            elif isinstance(result, (int, float, str)):
                                st.write("📊 **분석 결과:**")
                                st.write(result)
                            else:
                                st.write("📊 **분석 결과:**")
                                st.write(result)

                        if plt.get_fignums():
                            st.write("📈 **시각화 결과:**")
                            st.pyplot(plt.gcf())
                            plt.clf()

                        elif output.strip():
                            st.write("📋 **출력 결과:**")
                            st.write(output)

                    except Exception as e:
                        st.error(f"❌ 코드 실행 중 오류 발생: {e}")
                        st.write("**생성된 코드:**")
                        st.code(code, language="python")
