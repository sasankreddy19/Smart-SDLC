import ast

def predict_bugs(file_path):
    """
    Predict potential bugs in the code using rule-based analysis.
    Returns a list of potential bug descriptions.
    """
    try:
        # Read the code file
        with open(file_path, "r") as f:
            code = f.read()
        
        # AST-based analysis for potential bugs
        bugs = []
        tree = ast.parse(code)
        
        for node in ast.walk(tree):
            # Detect potential infinite loops
            if isinstance(node, ast.While):
                if isinstance(node.test, ast.NameConstant) and node.test.value is True:
                    bugs.append(f"Potential infinite loop at line {node.lineno}: 'while True' without break.")
            
            # Detect unsafe functions
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if node.func.id in ["eval", "exec"]:
                    bugs.append(f"Use of unsafe function '{node.func.id}' at line {node.lineno}; consider safer alternatives.")
            
            # Detect division by zero risk
            if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
                if isinstance(node.right, ast.Num) and node.right.n == 0:
                    bugs.append(f"Potential division by zero at line {node.lineno}.")
        
        return bugs if bugs else ["No potential bugs detected."]
    except Exception as e:
        return [f"Error during bug prediction: {str(e)}"]