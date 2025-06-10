import streamlit as st
import os
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from pyngrok import ngrok
import logging
import zipfile
import io

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load configuration
config = {
    "output_dir": "/content/output",
    "max_file_size": 1048576,  # 1MB
    "model_path": "ibm-granite/granite-3.3-2b-instruct"
}

# Utility functions
def ensure_directory(directory):
    os.makedirs(directory, exist_ok=True)
    return directory

def read_python_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {str(e)}")
        return None

def write_python_file(content, file_path):
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception as e:
        logger.error(f"Error writing file {file_path}: {str(e)}")
        return False

# Granite model integration
@st.cache_resource
def load_granite_model():
    try:
        tokenizer = AutoTokenizer.from_pretrained(config["model_path"])
        model = AutoModelForCausalLM.from_pretrained(
            config["model_path"],
            device_map="auto",
            torch_dtype=torch.bfloat16
        )
        model.eval()
        return model, tokenizer
    except Exception as e:
        logger.error(f"Error loading Granite model: {str(e)}")
        return None, None

def granite_generate(prompt, model, tokenizer, max_tokens=8192):
    try:
        inputs = tokenizer.apply_chat_template(
            [{"role": "user", "content": prompt}],
            return_tensors="pt",
            thinking=True,
            return_dict=True,
            add_generation_prompt=True
        ).to("cuda" if torch.cuda.is_available() else "cpu")
        output = model.generate(**inputs, max_new_tokens=max_tokens)
        return tokenizer.decode(output[0, inputs["input_ids"].shape[1]:], skip_special_tokens=True)
    except Exception as e:
        logger.error(f"Error generating with Granite: {str(e)}")
        return None

def add_docstrings(input_path, output_path, model, tokenizer):
    code = read_python_file(input_path)
    if not code:
        return False
    prompt = f"""Analyze the following Python code and add appropriate docstrings for functions, classes, and modules. Return the modified code with docstrings.

<code>
{code}
</code>"""
    result = granite_generate(prompt, model, tokenizer)
    if result:
        return write_python_file(result, output_path)
    return False

def review_code(input_path, model, tokenizer):
    code = read_python_file(input_path)
    if not code:
        return ["Error reading code file."]
    prompt = f"""Review the following Python code for style, best practices, and potential issues. Provide a list of specific, actionable comments.

<code>
{code}
</code>"""
    result = granite_generate(prompt, model, tokenizer)
    return result.split('\n') if result else ["Error during code review."]

def predict_bugs(input_path, model, tokenizer):
    code = read_python_file(input_path)
    if not code:
        return ["Error reading code file."]
    prompt = f"""Analyze the following Python code and predict potential bugs or logical errors. Provide a list of specific issues with explanations.

<code>
{code}
</code>"""
    result = granite_generate(prompt, model, tokenizer)
    return result.split('\n') if result else ["Error during bug prediction."]

def generate_project_report(input_path, output_dir, file_name, model, tokenizer):
    code = read_python_file(input_path)
    if not code:
        return False, "Error reading code file.", "txt"
    prompt = f"""Generate a concise project report summarizing the code in the provided file. Include an overview, key functionalities, and any notable observations.

<code>
{code}
</code>"""
    report = granite_generate(prompt, model, tokenizer)
    if not report:
        return False, "Error generating report.", "txt"
    report_path = os.path.join(output_dir, "project_report.txt")
    if write_python_file(report, report_path):
        return True, report_path, "txt"
    return False, "Error saving report.", "txt"

# Ensure output directory exists
ensure_directory(config["output_dir"])

# Streamlit app configuration
st.set_page_config(page_title="SmartSDLC", page_icon="🚀", layout="wide")

# App title and description
st.title("SmartSDLC: AI-Powered Software Development Lifecycle Tool")
st.markdown("Upload a Python file or ZIP archive to generate docstrings, review code quality, predict potential bugs, and create a project report using IBM Granite-3.3-2B-Instruct.")

# Load Granite model
model, tokenizer = load_granite_model()
if model is None or tokenizer is None:
    st.error("Failed to load Granite model. Please check your setup.")
    st.stop()

# File uploader
uploaded_file = st.file_uploader("Choose a file", type=["py", "zip"], help="Max file size: 1MB")

if uploaded_file is not None:
    # Check file size
    if len(uploaded_file.getvalue()) > config["max_file_size"]:
        st.error(f"File size exceeds {config['max_file_size'] / 1024 / 1024:.1f}MB limit.")
    else:
        # Save uploaded file temporarily
        input_path = os.path.join(config["output_dir"], f"temp_input.{uploaded_file.name.split('.')[-1]}")
        output_path = os.path.join(config["output_dir"], "temp_output.py")
        
        if uploaded_file.name.endswith('.zip'):
            with zipfile.ZipFile(io.BytesIO(uploaded_file.getvalue()), 'r') as zip_ref:
                zip_ref.extractall(config["output_dir"])
                st.info("ZIP file extracted. Please select a .py file for processing.")
                # List extracted Python files
                py_files = [f for f in os.listdir(config["output_dir"]) if f.endswith('.py')]
                if py_files:
                    selected_file = st.selectbox("Select a Python file", py_files)
                    input_path = os.path.join(config["output_dir"], selected_file)
                else:
                    st.error("No Python files found in the ZIP archive.")
                    st.stop()
        else:
            if not write_python_file(uploaded_file.getvalue().decode("utf-8", errors="ignore"), input_path):
                st.error("Failed to save uploaded file.")
                st.stop()

        # Display uploaded code if it's a Python file
        if input_path.endswith('.py'):
            st.subheader("Uploaded Code")
            st.code(read_python_file(input_path), language="python")
        
        # Create four columns for functionalities
        col1, col2, col3, col4 = st.columns(4)
        
        # Docstring Generation
        with col1:
            st.subheader("Generate Docstrings")
            if st.button("Generate Docstrings"):
                with st.spinner("Generating docstrings..."):
                    if input_path.endswith('.py'):
                        if add_docstrings(input_path, output_path, model, tokenizer):
                            output_code = read_python_file(output_path)
                            st.code(output_code, language="python")
                            st.success("Docstrings generated successfully!")
                            st.download_button(
                                label="Download File with Docstrings",
                                data=output_code,
                                file_name="output_with_docstrings.py",
                                mime="text/x-python"
                            )
                        else:
                            st.error("Failed to generate docstrings.")
                    else:
                        st.error("Docstring generation is only available for .py files.")
        
        # Code Review
        with col2:
            st.subheader("Code Review")
            if st.button("Review Code"):
                with st.spinner("Reviewing code..."):
                    if input_path.endswith('.py'):
                        review_comments = review_code(input_path, model, tokenizer)
                        st.write("**Code Review Comments:**")
                        for comment in review_comments:
                            st.write(f"- {comment}")
                    else:
                        st.error("Code review is only available for .py files.")
        
        # Bug Prediction
        with col3:
            st.subheader("Bug Prediction")
            if st.button("Predict Bugs"):
                with st.spinner("Predicting bugs..."):
                    if input_path.endswith('.py'):
                        bug_predictions = predict_bugs(input_path, model, tokenizer)
                        st.write("**Potential Bugs:**")
                        for bug in bug_predictions:
                            st.write(f"- {bug}")
                    else:
                        st.error("Bug prediction is only available for .py files.")
        
        # Project Report Generation
        with col4:
            st.subheader("Generate Documentation")
            if st.button("Generate Project Report"):
                with st.spinner("Generating project report..."):
                    success, result, report_type = generate_project_report(input_path, config["output_dir"], uploaded_file.name, model, tokenizer)
                    if success:
                        with open(result, "rb") as f:
                            st.success(f"Project report ({report_type.upper()}) generated successfully!")
                            st.download_button(
                                label=f"Download Project Report ({report_type.upper()})",
                                data=f,
                                file_name=f"project_report.{report_type}",
                                mime=f"text/{report_type}"
                            )
                    else:
                        st.error(result)
        
        # Clean up temporary files
        for path in [input_path, output_path]:
            if os.path.exists(path):
                os.remove(path)
                logger.info(f"Cleaned up {path}")
else:
    st.info("Please upload a Python file or ZIP archive to begin.")