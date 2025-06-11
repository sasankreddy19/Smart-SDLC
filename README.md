# SmartSDLC: AI-Powered Software Development Assistant 🚀

**SmartSDLC** is an AI-powered tool designed to streamline the software development lifecycle by providing automated assistance for common coding tasks. Built with **Python**, **Gradio**, and the **IBM Granite model** (`ibm-granite/granite-3.0-2b-instruct`), this tool helps developers by generating docstrings, reviewing code, predicting bugs, and creating project reports—all with a simple upload of a Python file.

---

## Features ✨

- **Generate Docstrings**: Automatically add Google-style docstrings to your Python code.
- **Review Code**: Get feedback on PEP8 compliance, logic errors, potential bugs, and improvement suggestions.
- **Predict Bugs**: Identify potential bugs, security vulnerabilities, and issues in your code.
- **Generate Project Report**: Create a comprehensive report summarizing your project's purpose, key functions, structure, and areas for improvement.

---
## Demo 🎥

Check out this video for a full demo of SmartSDLC in action!  
[Watch the demo on Google Drive](https://drive.google.com/file/d/1Lge_G28Yta5R3c4Mv-LZHI2Pl-RWmYXQ/view?usp=drive_link)

---

## Installation 🛠️

SmartSDLC can be run in a **Google Colab** environment or locally. Follow these steps to set it up:

### Prerequisites

- Python 3.8 or higher
- A Google Colab account (recommended for easy setup) or a local Python environment
- A GPU runtime (recommended for faster model loading and inference)

### Step 1: Clone the Repository

```bash
git clone https://github.com/sasankreddy19/smart-sdlc.git
cd smart-sdlc
```

### Step 2: Install Dependencies

Install the required Python packages using pip:

```bash
pip install transformers torch bitsandbytes gradio timeout-decorator
```  

### Step 3: Run in Google Colab (Recommended)

1. Open the `smartsdlc_colab_ngrok_(2).ipynb` notebook in [Google Colab](https://colab.research.google.com/).  
2. Go to **Runtime > Change runtime type**, and select **GPU** (e.g., T4).  
3. Run all the cells to install dependencies and launch the Gradio interface.

### Step 4: Run Locally (Optional)

Make sure your system has a GPU with at least **8GB VRAM** for optimal performance.  
Then run the main script in your terminal:

```bash
python smart_sdlc.py
```

Usage 📖
--------

### Launch the Application

*   **In Colab**: Run the notebook cells to start the Gradio interface.
    
*   **Locally**: Run python smart\_sdlc.py to launch the interface in your browser.
    

### Upload a Python File

*   Use the file upload button to upload a .py file (e.g., example.py).
    

### Select a Functionality

*   Click one of the buttons: **"Generate Docstrings"**, **"Review Code"**, **"Predict Bugs"**, or **"Generate Project Report"**.
    
*   The AI output will appear in the text box below.
    

Example Input File (example.py)
-------------------------------
def add_numbers(a, b):      return a + b  def multiply_numbers(a, b):      result = a * b      return result   `

Example Outputs
---------------

### Generate Docstrings

def add_numbers(a, b):      """Add two numbers and return their sum.      Args:          a: The first number.          b: The second number.      Returns:          The sum of the two numbers.      """      return a + b  def multiply_numbers(a, b):      """Multiply two numbers and return their product.      Args:          a: The first number.          b: The second number.      Returns:          The product of the two numbers.      """      result = a * b      return result   `

### Review Code
Review:  - PEP8: Add two blank lines before `multiply_numbers`. Add docstrings.  - Logic: No errors found.  - Bugs: No type checking; `add_numbers("1", 2)` will raise TypeError.  - Suggestions: Use type hints, e.g., `def add_numbers(a: float, b: float) -> float`.   ``

### Predict Bugs
 pythonCopyEditIssues:  - Type Safety: No input validation. Non-numeric inputs will raise TypeError.  - Suggestion: Add type checking, e.g., `if not isinstance(a, (int, float)):` .  - Security: No vulnerabilities detected.   ``

### Generate Project Report
Project Report:  Purpose: Basic arithmetic operations (addition, multiplication).  Key Functions: `add_numbers(a, b)`, `multiply_numbers(a, b)`.  Structure: Simple, lacks error handling and documentation.  Improvements: Add input validation, docstrings, type hints.   ``

Model Details 🤖
----------------

SmartSDLC uses the ibm-granite/granite-3.0-2b-instruct model from IBM, hosted on Hugging Face.This 2-billion-parameter model is optimized for instruction-following tasks and is well-suited for code-related analysis.The model is loaded with **4-bit quantization** to reduce memory usage, making it feasible to run in Colab with a GPU.

Troubleshooting 🐞
------------------

### Model Loading Takes Too Long

*   Ensure you're using a GPU runtime in Colab.
    
*   The model may take a few minutes to download the first time (cached afterward).
    
*   If it times out, check your internet connection or try a smaller model like ibm-granite/granite-3.0-1b-base.
    

### Error: "AI model is not loaded"

*   Verify that the model path (ibm-granite/granite-3.0-2b-instruct) is accessible.
    
*   You may need a Hugging Face token if the model is gated.
    
*   Check the Colab output for detailed error messages (debug=True).
    

### Gradio Interface Issues

*   Ensure all dependencies are installed: transformers, torch, bitsandbytes, gradio, timeout-decorator.
    
*   If running locally, make sure your browser allows the Gradio interface to load.
