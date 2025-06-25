import streamlit as st
import pandas as pd
from langchain_community.llms import Ollama  
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import io
import contextlib
import matplotlib.pyplot as plt
import re

# Ollama LLM 연결
llm = Ollama(
      base_url="http://localhost:11434",
      model="qwen2.5:14b",
      temperature=0.3
  )

st.set_page_config(layout="wide")
st.title("CSV-based Local LLM Analysis Agent")

uploaded_files = st.file_uploader("Upload CSV files", type=['csv'], accept_multiple_files=True)

def robust_code_extractor(llm_output):
    # 코드 블록이 있으면 그 안만 추출
    code_blocks = re.findall(r"```(?:python)?\n(.*?)```", llm_output, re.DOTALL)
    if code_blocks:
        return code_blocks[0].strip()
    # 코드 블록이 없으면, 전체에서 코드로 보이는 부분만 추출
    # (import, def, for, if, print, df, plt 등으로 시작하는 라인)
    lines = llm_output.splitlines()
    code_lines = []
    for line in lines:
        l = line.strip()
        if l and (l.startswith(("import", "def", "for", "if", "print", "df", "max", "min", "plt", "return")) or "=" in l):
            code_lines.append(line)
    return "\n".join(code_lines).strip()

if uploaded_files is not None:
    for idx, file in enumerate(uploaded_files):
        try:
            df = pd.read_csv(file)
            st.success(f"⭕️ Success File uploaded: '{file.name}'")
            st.write("Top 3 rows preview")
            st.dataframe(df.head(3), use_container_width=True)
        except Exception as e:
            st.error(f"❌ Failed to load file '{file.name}': {e}")
            continue  # 다음 파일로 넘어감

        st.markdown("""
        > 💡 **Example Questions**
        > - What is the maximum Salary?
        > - Please filter the data where the department is IT.
        > - Show only the data for the year 2023.
        """)

        prompt = st.text_area("💬 Ask a question about your data:", key=f"question_{idx}")

        template = """
            You are a skilled data analyst. The user will ask a question in Korean.

            Below is the CSV data:
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
                    # data_str = df.head(10).to_csv(index=False)
                    if f"csv_text_{idx}" not in st.session_state:
                        csv_text = df.to_csv(index=False)
                        if len(csv_text) > 16000:
                            csv_text = df.sample(100).to_csv(index=False)
                        st.session_state[f"csv_text_{idx}"] = csv_text
                    else:
                        csv_text = st.session_state[f"csv_text_{idx}"]

                    llm_output = chain.run({"data": csv_text, "question": prompt})

                    # 후처리: 코드만 추출
                    code = robust_code_extractor(llm_output)
                    code = re.sub(r".*pd\.read_csv\(.*\)\s*", "", code)  
                    
                    # 코드 실행 및 결과 출력
                    try:
                        local_vars = {"df": df, "pd": pd}
                        with contextlib.redirect_stdout(io.StringIO()) as f:
                            exec(code, local_vars)
                        output = f.getvalue()
                        
                        # 결과 출력
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
                        
                        # matplotlib 그래프 출력
                        if plt.get_fignums():
                            st.write("📈 **시각화 결과:**")
                            st.pyplot(plt.gcf())
                            plt.clf()
                        
                        # print 출력이 있으면 표시
                        elif output.strip():
                            st.write("📋 **출력 결과:**")
                            st.write(output)
                            
                    except Exception as e:
                        st.error(f"❌ 코드 실행 중 오류 발생: {e}")
                        st.write("**생성된 코드:**")
                        st.code(code, language="python")