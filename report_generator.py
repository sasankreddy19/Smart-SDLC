import os
import zipfile
import tempfile
import shutil
import subprocess
from datetime import datetime
import ast
from utils import read_python_file, write_python_file, ensure_directory, logger
from doc_generator import add_docstrings
from code_review import review_code
from bug_predictor import predict_bugs

def escape_latex(text):
    """
    Escape special LaTeX characters to prevent compilation errors.
    
    Args:
        text (str): Text to escape.
    
    Returns:
        str: Escaped text safe for LaTeX.
    """
    latex_special_chars = {
        '#': r'\#', '$': r'\$', '%': r'\%', '&': r'\&', 
        '_': r'\_', '{': r'\{', '}': r'\}', '~': r'\~{}', 
        '^': r'\^{}', '\\': r'\textbackslash{}', '<': r'\textless{}', 
        '>': r'\textgreater{}', '|': r'\textbar{}'
    }
    return ''.join(latex_special_chars.get(c, c) for c in text)

def calculate_code_metrics(file_path):
    """
    Calculate code metrics using AST analysis.
    
    Args:
        file_path (str): Path to the Python file.
    
    Returns:
        dict: Metrics including line count, function count, class count, and complexity.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            code = f.read()
        tree = ast.parse(code)
        
        metrics = {
            "line_count": len(code.splitlines()),
            "function_count": 0,
            "class_count": 0,
            "complexity": 0  # Simplified cyclomatic complexity
        }
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                metrics["function_count"] += 1
                # Count decision points (if, for, while, etc.) for complexity
                metrics["complexity"] += sum(
                    1 for n in ast.walk(node) 
                    if isinstance(n, (ast.If, ast.For, ast.While, ast.Try))
                )
            elif isinstance(node, ast.ClassDef):
                metrics["class_count"] += 1
        
        metrics["complexity"] += 1  # Base complexity
        return metrics
    except Exception as e:
        logger.error(f"Error calculating metrics for {file_path}: {str(e)}")
        return {"line_count": 0, "function_count": 0, "class_count": 0, "complexity": 0}

def generate_text_fallback(python_files, output_dir, file_name):
    """
    Generate a plain text report as a fallback if PDF compilation fails.
    
    Args:
        python_files (list): List of Python file paths to process.
        output_dir (str): Directory to store the text report.
        file_name (str): Name of the input file for report metadata.
    
    Returns:
        tuple: (bool, str) - Success status and path to text file or error message.
    """
    try:
        text_content = f"Project Report: {file_name}\n"
        text_content += "=" * 50 + "\n"
        text_content += f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        for py_file in python_files:
            file_base = os.path.basename(py_file)
            text_content += f"\nAnalysis of {file_base}\n"
            text_content += "-" * 50 + "\n"
            
            # Code Metrics
            metrics = calculate_code_metrics(py_file)
            text_content += "Code Metrics:\n"
            text_content += f"  Lines of Code: {metrics['line_count']}\n"
            text_content += f"  Functions: {metrics['function_count']}\n"
            text_content += f"  Classes: {metrics['class_count']}\n"
            text_content += f"  Cyclomatic Complexity: {metrics['complexity']}\n\n"
            
            # Generate docstrings
            output_path = os.path.join(output_dir, f"doc_{file_base}")
            if add_docstrings(py_file, output_path):
                docstring_content = read_python_file(output_path) or "No docstrings generated."
            else:
                docstring_content = "Failed to generate docstrings."
            text_content += "Code with Docstrings:\n"
            text_content += "-" * 30 + "\n"
            text_content += docstring_content + "\n\n"
            
            # Perform code review
            review_comments = review_code(py_file)
            text_content += "Code Review Findings:\n"
            text_content += "- " + "\n- ".join(review_comments) if review_comments else "- No significant issues found.\n"
            text_content += "\n"
            
            # Predict bugs
            bug_predictions = predict_bugs(py_file)
            text_content += "Bug Predictions:\n"
            text_content += "- " + "\n- ".join(bug_predictions) if bug_predictions else "- No potential bugs detected.\n"
            text_content += "\n"

        text_path = os.path.join(output_dir, "project_report.txt")
        if write_python_file(text_content, text_path):
            logger.info(f"Generated text report at {text_path}")
            return True, text_path
        return False, "Failed to write text report."
    except Exception as e:
        logger.error(f"Error generating text report: {str(e)}")
        return False, f"Error generating text report: {str(e)}"

def generate_project_report(input_file, output_dir, file_name):
    """
    Generate a project report in LaTeX format (PDF) or plain text fallback based on the uploaded file.

    Args:
        input_file (str): Path to the input file (Python or ZIP).
        output_dir (str): Directory to store temporary files and output report.
        file_name (str): Name of the input file for report metadata.

    Returns:
        tuple: (bool, str, str) - Success status, path to generated report (PDF or text), and report type ('pdf' or 'txt').
    """
    try:
        # Create temporary directory for processing
        temp_dir = tempfile.mkdtemp()
        if not ensure_directory(temp_dir):
            return False, "Failed to create temporary directory.", "none"

        python_files = []
        if file_name.endswith('.py'):
            python_files.append(input_file)
        elif file_name.endswith('.zip'):
            try:
                with zipfile.ZipFile(input_file, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)
                for root, _, files in os.walk(temp_dir):
                    python_files.extend(os.path.join(root, f) for f in files if f.endswith('.py'))
            except zipfile.BadZipFile:
                return False, "Invalid or corrupted ZIP file.", "none"
        else:
            return False, "Unsupported file format. Please upload a .py or .zip file.", "none"

        if not python_files:
            return False, "No Python files found in the uploaded ZIP.", "none"

        # Initialize LaTeX content
        latex_content = generate_latex_preamble(file_name)
        latex_content += f"\\section{{Project Overview}}\n"
        latex_content += f"\\textbf{{File Name:}} {escape_latex(file_name)}\\\\[0.2cm]\n"
        latex_content += f"\\textbf{{Generated:}} {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\\\\[0.2cm]\n"
        latex_content += f"\\textbf{{Description:}} Analysis of uploaded Python code with docstrings, code review, bug predictions, and metrics.\n\n"

        # Process each Python file
        for py_file in python_files:
            file_base = os.path.basename(py_file)
            latex_content += f"\\section{{Analysis of {escape_latex(file_base)}}}\n"
            
            # Code Metrics
            metrics = calculate_code_metrics(py_file)
            latex_content += "\\subsection{Code Metrics}\n"
            latex_content += "\\begin{description}\n"
            latex_content += f"\\item[Lines of Code:] {metrics['line_count']}\n"
            latex_content += f"\\item[Functions:] {metrics['function_count']}\n"
            latex_content += f"\\item[Classes:] {metrics['class_count']}\n"
            latex_content += f"\\item[Cyclomatic Complexity:] {metrics['complexity']}\n"
            latex_content += "\\end{description}\n\n"
            
            # Generate docstrings
            output_path = os.path.join(temp_dir, f"doc_{file_base}")
            if not add_docstrings(py_file, output_path):
                logger.warning(f"Failed to generate docstrings for {py_file}")
            docstring_content = read_python_file(output_path) or "No docstrings generated."
            docstring_content = escape_latex(docstring_content)
            latex_content += "\\subsection{Code with Docstrings}\n"
            latex_content += "\\begin{lstlisting}[language=Python]\n"
            latex_content += docstring_content + "\n"
            latex_content += "\\end{lstlisting}\n"
            
            # Perform code review
            review_comments = review_code(py_file)
            review_text = "\\item " + "\\item ".join(escape_latex(c) for c in review_comments) if review_comments else "\\item No significant issues found."
            latex_content += "\\subsection{Code Review Findings}\n"
            latex_content += "\\begin{itemize}\n" + review_text + "\n\\end{itemize}\n"
            
            # Predict bugs
            bug_predictions = predict_bugs(py_file)
            bug_text = "\\item " + "\\item ".join(escape_latex(b) for b in bug_predictions) if bug_predictions else "\\item No potential bugs detected."
            latex_content += "\\subsection{Bug Predictions}\n"
            latex_content += "\\begin{itemize}\n" + bug_text + "\n\\end{itemize}\n"

        # Finalize LaTeX document
        latex_content += "\\end{document}"

        # Write LaTeX file
        latex_path = os.path.join(output_dir, "project_report.tex")
        if not write_python_file(latex_content, latex_path):
            return False, "Failed to write LaTeX file.", "none"

        # Try compiling LaTeX to PDF
        pdf_path = os.path.join(output_dir, "project_report.pdf")
        try:
            result = subprocess.run(
                ["latexmk", "-pdf", f"-outdir={output_dir}", latex_path],
                capture_output=True, text=True, timeout=60
            )
            if result.returncode != 0:
                logger.error(f"LaTeX compilation failed: {result.stderr}")
                # Fallback to text
                success, text_path = generate_text_fallback(python_files, output_dir, file_name)
                return success, text_path, "txt"
        except (subprocess.SubprocessError, FileNotFoundError) as e:
            logger.error(f"LaTeX compilation error: {str(e)}")
            # Fallback to text
            success, text_path = generate_text_fallback(python_files, output_dir, file_name)
            return success, text_path, "txt"

        # Clean up LaTeX auxiliary files
        for ext in ['.aux', '.log', '.fls', '.fdb_latexmk', '.toc']:
            aux_file = latex_path.replace('.tex', ext)
            if os.path.exists(aux_file):
                os.remove(aux_file)

        # Clean up temporary directory
        shutil.rmtree(temp_dir)

        if os.path.exists(pdf_path):
            logger.info(f"Generated PDF report at {pdf_path}")
            return True, pdf_path, "pdf"
        return False, "Failed to generate PDF report.", "none"

    except Exception as e:
        logger.error(f"Error generating project report: {str(e)}")
        # Fallback to text
        success, text_path = generate_text_fallback(python_files, output_dir, file_name)
        return success, text_path, "txt"

def generate_latex_preamble(file_name):
    """
    Generate LaTeX preamble for the project report with a professional title page.

    Args:
        file_name (str): Name of the input file for the title.

    Returns:
        str: LaTeX preamble with necessary packages and title page.
    """
    return r"""
\documentclass[a4paper,12pt]{article}
\usepackage[utf8]{inputenc}
\usepackage{listings}
\usepackage{xcolor}
\usepackage{geometry}
\usepackage{times}
\geometry{margin=1in}

\lstset{
    language=Python,
    basicstyle=\ttfamily\small,
    keywordstyle=\color{blue},
    stringstyle=\color{red},
    commentstyle=\color{green!60!black},
    showstringspaces=false,
    breaklines=true,
    frame=single,
    numbers=left,
    numberstyle=\tiny,
    numbersep=5pt
}

\title{SmartSDLC Project Report: """ + escape_latex(file_name) + r"""}
\author{SmartSDLC Analysis Tool}
\date{\today}

\begin{document}
\maketitle
\tableofcontents
\newpage
"""