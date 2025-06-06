import ast
from transformers import AutoModelForSequenceClassification, AutoTokenizer
import torch

# Load CodeBERT model and tokenizer
model_name = "microsoft/codebert-base"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)

def review_code(file_path):
    """
    Perform AI-driven code review using CodeBERT and AST analysis.
    Returns a list of review comments.
    """
    try:
        # Read the code file
        with open(file_path, "r") as f:
            code = f.read()
        
        # AST-based analysis for structural issues
        comments = []
        tree = ast.parse(code)
        
        # Check for unused variables
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_name = node.name
                args = {arg.arg for arg in node.args.args}
                used_vars = set()
                for subnode in ast.walk(node):
                    if isinstance(subnode, ast.Name):
                        used_vars.add(subnode.id)
                unused_args = args - used_vars
                if unused_args:
                    comments.append(f"Function '{func_name}' has unused arguments: {', '.join(unused_args)}")
                
                # Check for complex functions (e.g., too many lines)
                if len(node.body) > 20:
                    comments.append(f"Function '{func_name}' is too long; consider refactoring.")
        
        # CodeBERT-based analysis for code quality
        inputs = tokenizer(code, return_tensors="pt", truncation=True, max_length=512)
        with torch.no_grad():
            outputs = model(**inputs)
        logits = outputs.logits
        # Simple heuristic: assume high confidence in negative class indicates issues
        if logits.softmax(dim=1)[0][1].item() > 0.7:
            comments.append("CodeBERT detected potential quality issues; review for best practices.")
        
        return comments if comments else ["No significant issues found."]
    except Exception as e:
        return [f"Error during code review: {str(e)}"]