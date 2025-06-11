import gradio as gr # type: ignore
import os
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
import logging
import zipfile
import time
import gc
import shutil

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load configuration
config = {
    "output_dir": "/content/output",
    "max_file_size": 1048576,  # 1MB
    "model_path": "ibm-granite/granite-3.3-2b-instruct",
    "use_quantization": True  # Enable 4-bit quantization
}

# Utility functions
def ensure_directory(directory):
    """Create directory if it doesn't exist."""
    try:
        os.makedirs(directory, exist_ok=True)
        return directory
    except Exception as e:
        logger.error(f"Error creating directory {directory}: {str(e)}")
        return None

def read_python_file(file_path):
    """Read content of a Python file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {str(e)}")
        return None

def write_python_file(content, file_path):
    """Write content to a Python file."""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception as e:
        logger.error(f"Error writing file {file_path}: {str(e)}")
        return False

# Granite model integration
def load_granite_model():
    """Load the Granite model and tokenizer."""
    try:
        tokenizer = AutoTokenizer.from_pretrained(config["model_path"])
        model_kwargs = {
            "device_map": "auto",
            "torch_dtype": torch.float16 if torch.cuda.is_available() else torch.float32
        }
        if config["use_quantization"]:
            model_kwargs["quantization_config"] = BitsAndBytesConfig(load_in_4bit=True)
        model = AutoModelForCausalLM.from_pretrained(config["model_path"], **model_kwargs)
        model.eval()
        return model, tokenizer
    except Exception as e:
        logger.error(f"Error loading Granite model: {str(e)}")
        return None, None
    finally:
        gc.collect()
        torch.cuda.empty_cache()

def granite_generate(prompt, model, tokenizer, max_tokens=4096):
    """Generate text using the Granite model."""
    try:
        inputs = tokenizer(prompt, return_tensors="pt").to("cuda" if torch.cuda.is_available() else "cpu")
        output = model.generate(**inputs, max_new_tokens=max_tokens, temperature=0.7)
        result = tokenizer.decode(output[0], skip_special_tokens=True)
        return result
    except Exception as e:
        logger.error(f"Error generating with Granite: {str(e)}")
        return None
    finally:
        gc.collect()
        torch.cuda.empty_cache()

def handle_upload(file):
    """Handle uploaded Python or ZIP files."""
    if file is None:
        return "No file uploaded.", None
    file_path = file.value  # Get file path from NamedString
    file_name = os.path.basename(file_path)

    if file_name.endswith('.py'):
        return f"Python file '{file_name}' received successfully.", file_path
    elif file_name.endswith('.zip'):
        try:
            zip_path = os.path.join(config["output_dir"], f"temp_{int(time.time())}.zip")
            ensure_directory(config["output_dir"])
            # Copy the uploaded file to the temporary ZIP path
            shutil.copy(file_path, zip_path)
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(config["output_dir"])
            os.remove(zip_path)
            py_files = [os.path.join(config["output_dir"], f) for f in os.listdir(config["output_dir"]) if f.endswith('.py')]
            if py_files:
                return f"ZIP file extracted. Found {len(py_files)} Python files.", py_files[0]
            else:
                return "No Python files found in ZIP.", None
        except Exception as e:
            return f"Error processing ZIP: {str(e)}", None
    else:
        return "Unsupported file type.", None

# Additional functionalities
def generate_docstrings(file):
    """Generate Google-style docstrings for the uploaded Python file."""
    status, path = handle_upload(file)
    if path is None:
        return status
    code = read_python_file(path)
    if code is None:
        return "Error reading file content."
    prompt = f"Add Google-style docstrings to the following Python code:\n\n{code}"
    model, tokenizer = load_granite_model()
    if model is None or tokenizer is None:
        return "Model loading failed."
    result = granite_generate(prompt, model, tokenizer)
    return result or "Docstring generation failed."

def review_code(file):
    """Review the uploaded Python code for PEP8 issues, logic errors, and improvements."""
    status, path = handle_upload(file)
    if path is None:
        return status
    code = read_python_file(path)
    if code is None:
        return "Error reading file content."
    prompt = f"Review the following Python code for PEP8 issues, logic errors, and improvements:\n\n{code}"
    model, tokenizer = load_granite_model()
    if model is None or tokenizer is None:
        return "Model loading failed."
    result = granite_generate(prompt, model, tokenizer)
    return result or "Code review failed."

def predict_bugs(file):
    """Predict bugs or potential issues in the uploaded Python code."""
    status, path = handle_upload(file)
    if path is None:
        return status
    code = read_python_file(path)
    if code is None:
        return "Error reading file content."
    prompt = f"Find and explain bugs or potential issues in this Python code:\n\n{code}"
    model, tokenizer = load_granite_model()
    if model is None or tokenizer is None:
        return "Model loading failed."
    result = granite_generate(prompt, model, tokenizer)
    return result or "Bug prediction failed."

def generate_report(file):
    """Generate a project report summarizing the uploaded Python code."""
    status, path = handle_upload(file)
    if path is None:
        return status
    code = read_python_file(path)
    if code is None:
        return "Error reading file content."
    prompt = f"Summarize this Python project. Include purpose, major functions, structure, and suggestions:\n\n{code}"
    model, tokenizer = load_granite_model()
    if model is None or tokenizer is None:
        return "Model loading failed."
    result = granite_generate(prompt, model, tokenizer)
    return result or "Project report failed."

# Gradio interface
with gr.Blocks(title="SmartSDLC: AI-Powered Software Development Lifecycle Tool") as demo:
    gr.Markdown("# 🚀 SmartSDLC: AI-Powered Software Development Assistant")
    gr.Markdown("Upload a Python (.py) or ZIP file to process with IBM Granite.")
    
    file_input = gr.File(label="📂 Upload a Python (.py) or ZIP File", file_types=[".py", ".zip"])
    status_text = gr.Textbox(label="Status")
    output = gr.Textbox(label="🧠 AI Output", lines=20)
    
    with gr.Row():
        doc_btn = gr.Button("📝 Generate Docstrings")
        review_btn = gr.Button("🔍 Review Code")
        bug_btn = gr.Button("🐞 Predict Bugs")
        report_btn = gr.Button("📊 Generate Project Report")
    
    file_input.change(
        fn=handle_upload,
        inputs=[file_input],
        outputs=[status_text, file_input]  # Update to store file path
    )
    
    doc_btn.click(fn=generate_docstrings, inputs=file_input, outputs=output)
    review_btn.click(fn=review_code, inputs=file_input, outputs=output)
    bug_btn.click(fn=predict_bugs, inputs=file_input, outputs=output)
    report_btn.click(fn=generate_report, inputs=file_input, outputs=output)

demo.launch(share=True)