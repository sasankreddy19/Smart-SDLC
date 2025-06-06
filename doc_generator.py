import ast

def generate_function_docstring(func_node):
    """
    Generate a docstring for a function node with inferred return type.
    
    Args:
        func_node (ast.FunctionDef): The AST node for the function.
    
    Returns:
        str: A formatted docstring.
    """
    doc = f'"""\n{func_node.name} function.\n\n'
    
    # Add arguments
    args = [arg.arg for arg in func_node.args.args if arg.arg != "self"]
    if args:
        doc += "Args:\n"
        for arg in args:
            doc += f"    {arg}: Description of {arg}.\n"
    
    # Infer return type from return statements
    return_types = set()
    for node in ast.walk(func_node):
        if isinstance(node, ast.Return) and node.value:
            if isinstance(node.value, ast.Num):
                return_types.add("number")
            elif isinstance(node.value, ast.Str):
                return_types.add("str")
            elif isinstance(node.value, ast.NameConstant) and node.value.value in (True, False):
                return_types.add("bool")
            elif isinstance(node.value, ast.List):
                return_types.add("list")
    
    if return_types:
        doc += "\nReturns:\n"
        doc += f"    {', '.join(return_types)}: Description of return value.\n"
    
    doc += '"""'
    return doc

def generate_class_docstring(class_node):
    """
    Generate a docstring for a class node.
    
    Args:
        class_node (ast.ClassDef): The AST node for the class.
    
    Returns:
        str: A formatted docstring.
    """
    return f'"""\n{class_node.name} class.\n\nDescription of the {class_node.name} class.\n"""'

def add_docstrings(file_path, output_path):
    """
    Read a Python file, add docstrings to functions and classes, and save to a new file.
    
    Args:
        file_path (str): Path to the input Python file.
        output_path (str): Path to save the modified file.
    
    Returns:
        bool: True if successful, False if an error occurs.
    """
    try:
        with open(file_path, "r") as file:
            source = file.read()
        
        tree = ast.parse(source)
        new_body = []
        
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and not ast.get_docstring(node):
                # Generate and insert docstring
                if isinstance(node, ast.FunctionDef):
                    docstring = generate_function_docstring(node)
                else:  # ast.ClassDef
                    docstring = generate_class_docstring(node)
                doc_node = ast.Expr(value=ast.Str(s=docstring))
                node.body.insert(0, doc_node)
            new_body.append(node)
        
        tree.body = new_body
        new_source = ast.unparse(tree)
        
        with open(output_path, "w") as file:
            file.write(new_source)
        return True
    except Exception as e:
        print(f"Error in doc_generator: {str(e)}")
        return False