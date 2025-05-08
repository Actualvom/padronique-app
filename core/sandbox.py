#!/usr/bin/env python3
"""
sandbox.py: Runs new code updates in an isolated environment.
"""

import os
import sys
import logging
import importlib.util
import traceback
import uuid

logger = logging.getLogger("padronique.sandbox")

class Sandbox:
    """
    Sandbox environment for safely running untrusted code.
    
    CAUTION: This is a basic sandbox that provides limited isolation.
    In a production environment, use more robust sandboxing techniques.
    """
    
    def __init__(self):
        """Initialize the sandbox."""
        self.restricted_modules = [
            "os.system", "subprocess", "shutil.rmtree", "socket",
            "requests.post", "urllib.request", "ftplib", "smtplib"
        ]
        self.execution_id = str(uuid.uuid4())
        self.results = {}
    
    def validate_code(self, code_string):
        """
        Validate code for potentially dangerous operations.
        
        Args:
            code_string: String containing the code to validate
            
        Returns:
            tuple: (is_valid, message)
        """
        # Check for restricted module imports
        for module in self.restricted_modules:
            if module in code_string:
                return False, f"Found restricted module: {module}"
        
        # Check for eval, exec
        if "eval(" in code_string or "exec(" in code_string:
            return False, "Found eval() or exec() which are not allowed"
        
        # Check for file operations
        if "open(" in code_string and ("w" in code_string or "a" in code_string):
            return False, "File write operations are restricted"
        
        return True, "Code passed validation"
    
    def run_code_string(self, code_string):
        """
        Run code from a string in the sandbox.
        
        Args:
            code_string: String containing the code to run
            
        Returns:
            dict: Execution results
        """
        # Validate code first
        is_valid, message = self.validate_code(code_string)
        if not is_valid:
            logger.warning(f"Code validation failed: {message}")
            return {"success": False, "error": message}
        
        # Create a restricted globals dictionary
        safe_globals = {
            "__builtins__": {
                name: __builtins__[name] 
                for name in ["print", "dict", "list", "tuple", "set", "int", "float", 
                             "str", "bool", "True", "False", "None", "len", "range", 
                             "enumerate", "zip", "min", "max", "sum", "abs", "round"]
            },
            "result": None
        }
        
        try:
            # Execute code with restricted globals
            exec(code_string, safe_globals)
            return {
                "success": True,
                "result": safe_globals.get("result"),
                "execution_id": self.execution_id
            }
        except Exception as e:
            error_msg = f"Error executing code: {str(e)}\n{traceback.format_exc()}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": str(e),
                "traceback": traceback.format_exc(),
                "execution_id": self.execution_id
            }
    
    def run_file(self, file_path):
        """
        Run a Python file in the sandbox.
        
        Args:
            file_path: Path to the Python file
            
        Returns:
            dict: Execution results
        """
        try:
            with open(file_path, 'r') as f:
                code_string = f.read()
            
            return self.run_code_string(code_string)
        except Exception as e:
            error_msg = f"Error running file {file_path}: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}
    
    def load_module_safely(self, module_path):
        """
        Load a Python module safely for testing.
        
        Args:
            module_path: Path to the Python module file
            
        Returns:
            module or None: The loaded module or None if loading failed
        """
        try:
            # Read the file content first for validation
            with open(module_path, 'r') as f:
                code_string = f.read()
            
            # Validate code
            is_valid, message = self.validate_code(code_string)
            if not is_valid:
                logger.warning(f"Module validation failed: {message}")
                return None
            
            # Load the module
            module_name = os.path.basename(module_path).replace('.py', '')
            spec = importlib.util.spec_from_file_location(module_name, module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            return module
        except Exception as e:
            logger.error(f"Error loading module {module_path}: {e}")
            return None

# Create a global sandbox instance
sandbox = Sandbox()

def run_in_sandbox(script_path):
    """
    Run a script in the sandbox. Public function for easy access.
    
    Args:
        script_path: Path to the script
        
    Returns:
        dict: Execution results
    """
    return sandbox.run_file(script_path)

if __name__ == "__main__":
    # When run directly, execute a script provided as argument
    if len(sys.argv) != 2:
        print("Usage: sandbox.py <script_path>")
    else:
        result = run_in_sandbox(sys.argv[1])
        print(f"Execution result: {result}")
