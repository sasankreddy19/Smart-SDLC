# SmartSDLC - AI-Enhanced Software Development Lifecycle

## Overview
**SmartSDLC** is a tool designed to streamline the software development lifecycle by automating repetitive tasks such as code reviews, documentation generation, and bug detection.  
It leverages the **IBM Granite language model** (via Hugging Face) for AI-powered analysis, combined with static analysis tools like `pylint`, to enhance developer productivity, improve code quality, and accelerate project timelines.

---

## Features
- **Automated Code Reviews**: Combines `pylint` static analysis with AI-driven feedback to identify syntax issues, style improvements, and optimizations.
- **Documentation Generation**: Automatically generates Markdown documentation from Python code, including function descriptions, parameters, and examples.
- **Bug Detection**: Uses AI and anomaly detection to identify potential bugs early, improving software reliability.
- **Git Integration**: Analyzes all Python files in a local Git repository for batch processing.
- **User Interface**: Streamlit-based web UI for easy interaction, file uploads, and result visualization.

---

## Prerequisites
- **Python**: Version 3.8+ ([Download](https://www.python.org/))
- **Git**: For repository analysis ([Download](https://git-scm.com/))
- **Hardware**: 16GB+ RAM and 20GB free disk space (CUDA-enabled GPU recommended)
- **Text Editor / IDE**: VS Code, PyCharm, etc.
- **Internet Connection**: Required to download Granite model from Hugging Face

---

## Project Structure
SmartSDLC/
├── app.py # Main Streamlit application
├── code_analyzer.py # Code review and bug detection logic
├── doc_generator.py # Documentation generation logic
├── utils.py # Helper functions for file operations
├── requirements.txt # Python dependencies
├── README.md # This file


---

## Installation

### Clone or Create Project Directory
```bash
# Option 1: Manually
mkdir SmartSDLC
# Place app.py, code_analyzer.py, doc_generator.py, utils.py, requirements.txt inside

# Option 2: Clone from GitHub
git clone <repository-url>
cd SmartSDLC

## Set Up Virtual Environment

python -m venv venv

# Activate environment:
# On Linux/macOS:
source venv/bin/activate

# On Windows:
venv\Scripts\activate

### Running the Application
Start Streamlit

streamlit run app.py
This starts a local server, typically at:
📍 http://localhost:8501

