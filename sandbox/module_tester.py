#!/usr/bin/env python3
# sandbox/module_tester.py - Sandbox for testing modules safely

import os
import sys
import time
import logging
import json
import multiprocessing
import resource
import traceback
from typing import Dict, Any, Optional, Tuple
import tempfile
import importlib.util
import inspect
from io import StringIO
import contextlib

logger = logging.getLogger(__name__)

class SandboxException(Exception):
    """Exception raised for sandbox-related errors."""
    pass


class ResourceLimitExceeded(SandboxException):
    """Exception raised when sandbox resource limits are exceeded."""
    pass


class TimeoutException(SandboxException):
    """Exception raised when sandbox execution times out."""
    pass


@contextlib.contextmanager
def capture_output():
    """Context manager to capture stdout and stderr."""
    new_out, new_err = StringIO(), StringIO()
    old_out, old_err = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = new_out, new_err
        yield sys.stdout, sys.stderr
    finally:
        sys.stdout, sys.stderr = old_out, old_err


def set_resource_limits(max_memory_mb: int) -> None:
    """
    Set resource limits for the process.
    
    Args:
        max_memory_mb: Maximum memory in MB
    """
    # Convert MB to bytes
    max_memory_bytes = max_memory_mb * 1024 * 1024
    
    # Set maximum memory limit
    resource.setrlimit(resource.RLIMIT_AS, (max_memory_bytes, max_memory_bytes))
    
    # Set CPU time limit (30 seconds)
    resource.setrlimit(resource.RLIMIT_CPU, (30, 30))


def execute_code_in_subprocess(code: str, inputs: Dict[str, Any], 
                              max_memory_mb: int, timeout: int) -> Dict[str, Any]:
    """
    Execute code in a subprocess with resource limits.
    
    Args:
        code: Python code to execute
        inputs: Input data for the code
        max_memory_mb: Maximum memory in MB
        timeout: Timeout in seconds
        
    Returns:
        Dictionary with execution results
    """
    # Set up temporary files for code and inputs
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as code_file:
        code_file.write(code)
        code_file_path = code_file.name
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as input_file:
        json.dump(inputs, input_file)
        input_file_path = input_file.name
    
    # Create a pipe for results
    parent_conn, child_conn = multiprocessing.Pipe()
    
    # Define the subprocess function
    def subprocess_func(code_path, input_path, conn, max_memory):
        try:
            # Set resource limits
            set_resource_limits(max_memory)
            
            # Load inputs
            with open(input_path, 'r') as f:
                inputs = json.load(f)
            
            # Capture output
            with capture_output() as (out, err):
                # Create a namespace for execution
                namespace = {'__inputs': inputs, '__result': None}
                
                # Execute the code
                with open(code_path, 'r') as f:
                    code_content = f.read()
                
                exec(code_content, namespace)
                
                # Get the result
                result = namespace.get('__result')
            
            # Send result back through pipe
            conn.send({
                'success': True,
                'result': result,
                'stdout': out.getvalue(),
                'stderr': err.getvalue()
            })
        
        except Exception as e:
            # Capture the exception
            conn.send({
                'success': False,
                'error': str(e),
                'traceback': traceback.format_exc(),
                'stdout': out.getvalue() if 'out' in locals() else '',
                'stderr': err.getvalue() if 'err' in locals() else ''
            })
        
        finally:
            conn.close()
    
    # Start the subprocess
    process = multiprocessing.Process(
        target=subprocess_func,
        args=(code_file_path, input_file_path, child_conn, max_memory_mb)
    )
    
    process.start()
    
    # Wait for the process to complete or timeout
    process.join(timeout)
    
    # Check if the process is still running after timeout
    if process.is_alive():
        process.terminate()
        process.join(1)
        
        # Force kill if still alive
        if process.is_alive():
            process.kill()
        
        result = {
            'success': False,
            'error': f'Execution timed out after {timeout} seconds',
            'stdout': '',
            'stderr': ''
        }
    else:
        # Get result from pipe if available
        if parent_conn.poll():
            result = parent_conn.recv()
        else:
            result = {
                'success': False,
                'error': 'Process terminated without returning a result',
                'stdout': '',
                'stderr': ''
            }
    
    # Clean up temporary files
    try:
        os.unlink(code_file_path)
        os.unlink(input_file_path)
    except Exception as e:
        logger.warning(f"Failed to clean up temporary files: {e}")
    
    return result


class SandboxTester:
    """
    Sandbox for testing and running code safely.
    
    Executes code in an isolated environment with resource limits.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the SandboxTester.
        
        Args:
            config: Sandbox configuration
        """
        self.enabled = config.get('enabled', True)
        self.isolation_level = config.get('isolation_level', 'process')
        self.timeout_seconds = config.get('timeout_seconds', 10)
        self.max_memory_mb = config.get('max_memory_mb', 500)
        
        logger.info(f"Sandbox initialized with isolation={self.isolation_level}, timeout={self.timeout_seconds}s, memory={self.max_memory_mb}MB")
    
    def test_code(self, code: str, inputs: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Test a code snippet in the sandbox.
        
        Args:
            code: Python code to test
            inputs: Input data for the code
            
        Returns:
            Dictionary with test results
        """
        if not self.enabled:
            return {
                'success': False,
                'error': 'Sandbox is disabled in configuration',
                'stdout': '',
                'stderr': ''
            }
        
        if inputs is None:
            inputs = {}
        
        # Check if code is valid Python
        try:
            compile(code, '<string>', 'exec')
        except SyntaxError as e:
            return {
                'success': False,
                'error': f'Syntax error: {str(e)}',
                'stdout': '',
                'stderr': '',
                'line': e.lineno,
                'offset': e.offset
            }
        
        # Execute in subprocess for isolation
        start_time = time.time()
        
        result = execute_code_in_subprocess(
            code, inputs, self.max_memory_mb, self.timeout_seconds
        )
        
        execution_time = time.time() - start_time
        
        # Add execution time to result
        result['execution_time'] = execution_time
        
        return result
    
    def test_module(self, module_code: str, class_name: str, method_name: str, 
                   method_args: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Test a module class and method in the sandbox.
        
        Args:
            module_code: Python module code
            class_name: Name of the class to test
            method_name: Name of the method to test
            method_args: Arguments for the method
            
        Returns:
            Dictionary with test results
        """
        if not self.enabled:
            return {
                'success': False,
                'error': 'Sandbox is disabled in configuration',
                'stdout': '',
                'stderr': ''
            }
        
        if method_args is None:
            method_args = {}
        
        # Create a wrapper that loads the module, creates the class,
        # and calls the method
        wrapper_code = f"""
# Import the original inputs
inputs = __inputs
method_args = inputs.get('method_args', {{}})

# Define the module code
{module_code}

# Execute the method and store result
try:
    # Create an instance of the class
    instance = {class_name}()
    
    # Call the method
    __result = getattr(instance, "{method_name}")(**method_args)
except Exception as e:
    import traceback
    __result = {{'error': str(e), 'traceback': traceback.format_exc()}}
"""
        
        # Test the wrapper code
        return self.test_code(wrapper_code, {'method_args': method_args})
    
    def test_brain_module(self, module_code: str, config: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Test a brain module implementation in the sandbox.
        
        Args:
            module_code: Python module code
            config: Module configuration
            
        Returns:
            Dictionary with test results
        """
        if not self.enabled:
            return {
                'success': False,
                'error': 'Sandbox is disabled in configuration',
                'stdout': '',
                'stderr': ''
            }
        
        if config is None:
            config = {}
        
        # Create a wrapper that simulates the brain module environment
        wrapper_code = f"""
# Import the original inputs
inputs = __inputs
config = inputs.get('config', {{}})
test_input = inputs.get('test_input', {{}})

# Mock required classes and dependencies
class MemoryManager:
    def __init__(self):
        self.memories = {{}}
    
    def store_memory(self, memory_data, tags=None):
        import uuid
        memory_id = str(uuid.uuid4())
        self.memories[memory_id] = {{'data': memory_data, 'tags': tags}}
        return memory_id
    
    def retrieve_memory(self, memory_id):
        return self.memories.get(memory_id, {{}}).get('data')
    
    def search_memories(self, query, tags=None, limit=10):
        return []
    
    def get_memory_context(self, query, context_size=5):
        return []

class BrainModule:
    def __init__(self, config, memory_manager):
        self.config = config
        self.memory_manager = memory_manager
        self.active = True
        self.last_used = 0
        self.processing_count = 0
        self.error_count = 0
        self.total_processing_time = 0
    
    def is_active(self):
        return self.active
    
    def activate(self):
        self.active = True
    
    def deactivate(self):
        self.active = False
    
    def get_stats(self):
        return {{
            'active': self.active,
            'processing_count': self.processing_count,
            'error_count': self.error_count
        }}
    
    def shutdown(self):
        pass

# Add the module code
{module_code}

# Find the module class (subclass of BrainModule)
module_class = None
for item_name in dir():
    item = locals()[item_name]
    try:
        if (isinstance(item, type) and 
            issubclass(item, BrainModule) and 
            item is not BrainModule):
            module_class = item
            break
    except TypeError:
        pass

if not module_class:
    __result = {{'error': 'No BrainModule subclass found in code'}}
else:
    try:
        # Create the module
        memory_manager = MemoryManager()
        module = module_class(config, memory_manager)
        
        # Process test input
        process_result = module.process(test_input)
        
        __result = {{
            'module_class': module_class.__name__,
            'process_result': process_result,
            'is_active': module.is_active(),
            'stats': module.get_stats()
        }}
    except Exception as e:
        import traceback
        __result = {{'error': str(e), 'traceback': traceback.format_exc()}}
"""
        
        # Test the wrapper code
        return self.test_code(
            wrapper_code, 
            {'config': config, 'test_input': {'type': 'text', 'content': 'Test input'}}
        )
