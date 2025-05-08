#!/usr/bin/env python3
"""
adaptive_module_loader.py: Loads and integrates external modules safely.
"""

import os
import sys
import importlib
import importlib.util
import inspect
import logging
import json
import time
import re
import hashlib
from brains.base_brain import BaseBrain

class AdaptiveModuleLoader(BaseBrain):
    """
    Adaptive Module Loader brain responsible for safely loading and integrating external code.
    Provides a mechanism for Padronique to extend its capabilities with new modules.
    """
    
    def __init__(self):
        """Initialize the Adaptive Module Loader brain."""
        super().__init__("AdaptiveLoader")
        self.digital_soul = None  # Will be set by orchestrator
        self.sandbox = None       # Will be set by orchestrator
        self.pending_modules = {}
        self.loaded_modules = {}
        self.module_dir = "modules"
        self.quarantine_dir = "modules/quarantine"
        self.verified_dir = "modules/verified"
        self.integration_status = {
            "last_scan": 0,
            "modules_integrated": 0,
            "failed_integrations": 0
        }
        
        # Create directories
        for directory in [self.module_dir, self.quarantine_dir, self.verified_dir]:
            if not os.path.exists(directory):
                try:
                    os.makedirs(directory)
                    self.logger.info(f"Created directory: {directory}")
                except Exception as e:
                    self.logger.error(f"Failed to create directory {directory}: {e}")
    
    def process_input(self, input_data):
        """
        Process input data for module loading and integration.
        
        Args:
            input_data: Input data to process
            
        Returns:
            str: Response or None
        """
        super().process_input(input_data)
        
        # Handle cycle updates - scan for new modules
        if input_data == "Cycle update":
            self._scan_for_modules()
            return None
        
        # Skip if not module-related
        if not self._is_module_related(input_data):
            return None
        
        try:
            input_lower = input_data.lower()
            
            # Check for module installation commands
            if any(phrase in input_lower for phrase in ["install module", "add module", "load module"]):
                return self._handle_module_installation(input_data)
            
            # Check for module listing commands
            elif any(phrase in input_lower for phrase in ["list modules", "show modules", "installed modules"]):
                return self._list_modules()
            
            # Check for module verification commands
            elif any(phrase in input_lower for phrase in ["verify module", "check module", "validate module"]):
                return self._handle_module_verification(input_data)
            
            # Check for module removal commands
            elif any(phrase in input_lower for phrase in ["remove module", "uninstall module", "delete module"]):
                return self._handle_module_removal(input_data)
            
            # Default response
            else:
                return "I can help you manage external modules that extend my capabilities. I can install, verify, list, or remove modules."
                
        except Exception as e:
            self.logger.error(f"Error processing module loader input: {e}")
            self.stats["error_count"] += 1
            return None
    
    def _is_module_related(self, text):
        """
        Determine if input is related to module loading.
        
        Args:
            text: Input text
            
        Returns:
            bool: True if module-related
        """
        text_lower = text.lower()
        
        # Module-related keywords
        module_keywords = [
            "module", "plugin", "extension", "addon", "add-on",
            "install", "uninstall", "load", "integrate", "import",
            "code", "function", "class", "update"
        ]
        
        return any(keyword in text_lower for keyword in module_keywords)
    
    def _scan_for_modules(self):
        """
        Scan for new modules to integrate.
        
        Returns:
            int: Number of new modules found
        """
        # Only scan periodically (every 5 minutes)
        current_time = time.time()
        if current_time - self.integration_status["last_scan"] < 300:
            return 0
        
        self.integration_status["last_scan"] = current_time
        
        # Scan the quarantine directory for modules pending verification
        new_modules = 0
        
        try:
            for filename in os.listdir(self.quarantine_dir):
                if filename.endswith(".py") and not filename.startswith("_"):
                    module_path = os.path.join(self.quarantine_dir, filename)
                    module_id = self._generate_module_id(module_path)
                    
                    # Check if already processed
                    if module_id not in self.pending_modules and module_id not in self.loaded_modules:
                        # Add to pending modules
                        self.pending_modules[module_id] = {
                            "filename": filename,
                            "path": module_path,
                            "status": "pending",
                            "discovered": current_time
                        }
                        new_modules += 1
                        self.logger.info(f"Found new module: {filename}")
        except Exception as e:
            self.logger.error(f"Error scanning for modules: {e}")
        
        return new_modules
    
    def _handle_module_installation(self, text):
        """
        Handle module installation requests.
        
        Args:
            text: Request text
            
        Returns:
            str: Response
        """
        # Check if this is about a specific module file
        module_path_match = re.search(r"'([^']+\.py)'|\"([^\"]+\.py)\"", text)
        
        if module_path_match:
            # Get the module path
            module_path = module_path_match.group(1) or module_path_match.group(2)
            
            # Ensure the path is absolute or relative to current directory
            if not os.path.isabs(module_path) and not module_path.startswith("./"):
                module_path = os.path.join(".", module_path)
            
            # Check if file exists
            if not os.path.exists(module_path):
                return f"Module file not found: {module_path}"
            
            # Copy to quarantine for verification
            return self._quarantine_module(module_path)
        
        # If not about a specific file, check if we're being asked to add new code
        code_block_match = re.search(r"```(?:python)?\s*(.*?)```", text, re.DOTALL)
        
        if code_block_match:
            # Extract code from the code block
            code = code_block_match.group(1).strip()
            
            # Generate a filename for the module
            module_name = f"custom_module_{int(time.time())}.py"
            module_path = os.path.join(self.quarantine_dir, module_name)
            
            # Save the code to a file in quarantine
            try:
                with open(module_path, 'w') as f:
                    f.write(code)
                
                self.logger.info(f"Saved new module code to {module_path}")
                
                # Add to pending modules
                module_id = self._generate_module_id(module_path)
                self.pending_modules[module_id] = {
                    "filename": module_name,
                    "path": module_path,
                    "status": "pending",
                    "discovered": time.time()
                }
                
                return f"Code saved as {module_name} and placed in quarantine for verification. You can verify it with 'verify module {module_name}'."
            
            except Exception as e:
                self.logger.error(f"Error saving module code: {e}")
                return f"Failed to save module code: {str(e)}"
        
        # If no module file or code block was provided
        return "To install a module, please provide a Python file path or a code block using triple backticks (```python ... ```)."
    
    def _quarantine_module(self, source_path):
        """
        Copy a module file to the quarantine directory.
        
        Args:
            source_path: Path to the source module file
            
        Returns:
            str: Response
        """
        try:
            # Get the filename
            filename = os.path.basename(source_path)
            quarantine_path = os.path.join(self.quarantine_dir, filename)
            
            # Copy the file to quarantine
            import shutil
            shutil.copy2(source_path, quarantine_path)
            
            # Add to pending modules
            module_id = self._generate_module_id(quarantine_path)
            self.pending_modules[module_id] = {
                "filename": filename,
                "path": quarantine_path,
                "source_path": source_path,
                "status": "pending",
                "discovered": time.time()
            }
            
            self.logger.info(f"Module '{filename}' placed in quarantine for verification")
            return f"Module '{filename}' has been placed in quarantine for verification. You can verify it with 'verify module {filename}'."
            
        except Exception as e:
            self.logger.error(f"Error quarantining module: {e}")
            return f"Failed to quarantine module: {str(e)}"
    
    def _list_modules(self):
        """
        List all modules (pending and loaded).
        
        Returns:
            str: Module list
        """
        response = "Module Status:\n\n"
        
        # Pending modules
        if self.pending_modules:
            response += "Pending Modules (awaiting verification):\n"
            for module_id, info in self.pending_modules.items():
                discovered_time = time.strftime("%Y-%m-%d %H:%M", time.localtime(info["discovered"]))
                response += f"- {info['filename']} (discovered: {discovered_time})\n"
        else:
            response += "No pending modules.\n"
        
        response += "\n"
        
        # Loaded modules
        if self.loaded_modules:
            response += "Loaded Modules:\n"
            for module_id, info in self.loaded_modules.items():
                loaded_time = time.strftime("%Y-%m-%d %H:%M", time.localtime(info["loaded"]))
                response += f"- {info['name']} (loaded: {loaded_time})\n"
                if "description" in info:
                    response += f"  Description: {info['description']}\n"
        else:
            response += "No loaded modules.\n"
        
        return response
    
    def _handle_module_verification(self, text):
        """
        Handle module verification requests.
        
        Args:
            text: Request text
            
        Returns:
            str: Response
        """
        # Extract module name
        module_name_match = re.search(r"verify module ['\"]?([a-zA-Z0-9_\.]+)['\"]?", text, re.IGNORECASE)
        
        if not module_name_match:
            return "Please specify which module to verify, e.g., 'verify module example_module.py'."
        
        module_name = module_name_match.group(1)
        
        # Find the module in pending modules
        module_id = None
        for mid, info in self.pending_modules.items():
            if info["filename"] == module_name:
                module_id = mid
                break
        
        if not module_id:
            return f"Module '{module_name}' not found in pending modules. Available pending modules: " + ", ".join(info["filename"] for info in self.pending_modules.values())
        
        # Verify the module
        module_path = self.pending_modules[module_id]["path"]
        verification_result = self._verify_module(module_path)
        
        if verification_result["safe"]:
            # Move to verified directory
            verified_path = os.path.join(self.verified_dir, os.path.basename(module_path))
            
            try:
                import shutil
                shutil.copy2(module_path, verified_path)
                
                # Try to load the module
                load_result = self._load_module(verified_path)
                
                if load_result["success"]:
                    # Update status
                    self.loaded_modules[module_id] = {
                        "name": load_result["name"],
                        "path": verified_path,
                        "module": load_result["module"],
                        "classes": load_result["classes"],
                        "functions": load_result["functions"],
                        "loaded": time.time()
                    }
                    
                    # Add description if available
                    if "description" in load_result:
                        self.loaded_modules[module_id]["description"] = load_result["description"]
                    
                    # Remove from pending
                    del self.pending_modules[module_id]
                    
                    # Clean up quarantine file
                    try:
                        os.remove(module_path)
                    except:
                        pass
                    
                    self.integration_status["modules_integrated"] += 1
                    
                    return f"Module '{module_name}' has been verified and loaded successfully."
                else:
                    return f"Module '{module_name}' passed security verification but failed to load: {load_result['error']}"
                
            except Exception as e:
                self.logger.error(f"Error moving verified module: {e}")
                return f"Error moving verified module: {str(e)}"
        else:
            # Update status
            self.pending_modules[module_id]["status"] = "failed_verification"
            self.pending_modules[module_id]["failure_reason"] = verification_result["reason"]
            self.integration_status["failed_integrations"] += 1
            
            return f"Module '{module_name}' failed verification: {verification_result['reason']}"
    
    def _verify_module(self, module_path):
        """
        Verify a module for safety.
        
        Args:
            module_path: Path to the module file
            
        Returns:
            dict: Verification result
        """
        # Read the module content
        try:
            with open(module_path, 'r') as f:
                code = f.read()
        except Exception as e:
            return {
                "safe": False,
                "reason": f"Could not read module file: {str(e)}"
            }
        
        # Check for dangerous imports
        dangerous_imports = [
            "os.system", "subprocess", "pty", "socket", "requests.delete",
            "shutil.rmtree", "__import__('os').system", "eval(", "exec("
        ]
        
        for imp in dangerous_imports:
            if imp in code:
                return {
                    "safe": False,
                    "reason": f"Module contains potentially dangerous code: {imp}"
                }
        
        # Check for file operations that might be destructive
        file_ops = [
            r"\.remove\(", r"\.unlink\(", r"os\.remove", 
            r"os\.unlink", r"\.rmtree\(", r"shutil\.rmtree"
        ]
        
        for op in file_ops:
            if re.search(op, code):
                return {
                    "safe": False,
                    "reason": f"Module contains potentially destructive file operations: {op}"
                }
        
        # Use the sandbox to test the module if available
        if hasattr(self, 'sandbox') and self.sandbox:
            try:
                sandbox_result = self.sandbox.load_module_safely(module_path)
                
                if sandbox_result is None:
                    return {
                        "safe": False,
                        "reason": "Module failed sandbox validation"
                    }
            except Exception as e:
                return {
                    "safe": False,
                    "reason": f"Sandbox testing failed: {str(e)}"
                }
        
        # All checks passed
        return {
            "safe": True,
            "reason": "Module passed all security checks"
        }
    
    def _load_module(self, module_path):
        """
        Load a verified module.
        
        Args:
            module_path: Path to the verified module file
            
        Returns:
            dict: Load result
        """
        try:
            # Extract module name from path
            module_name = os.path.basename(module_path).replace(".py", "")
            
            # Load the module
            spec = importlib.util.spec_from_file_location(module_name, module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Extract classes and functions
            classes = {}
            functions = {}
            
            for name, obj in inspect.getmembers(module):
                if inspect.isclass(obj) and obj.__module__ == module_name:
                    classes[name] = obj
                elif inspect.isfunction(obj) and obj.__module__ == module_name:
                    functions[name] = obj
            
            # Try to get module description
            description = module.__doc__ if hasattr(module, "__doc__") and module.__doc__ else "No description available"
            
            return {
                "success": True,
                "name": module_name,
                "module": module,
                "classes": classes,
                "functions": functions,
                "description": description
            }
            
        except Exception as e:
            self.logger.error(f"Error loading module {module_path}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _handle_module_removal(self, text):
        """
        Handle module removal requests.
        
        Args:
            text: Request text
            
        Returns:
            str: Response
        """
        # Extract module name
        module_name_match = re.search(r"(?:remove|uninstall|delete) module ['\"]?([a-zA-Z0-9_\.]+)['\"]?", text, re.IGNORECASE)
        
        if not module_name_match:
            return "Please specify which module to remove, e.g., 'remove module example_module'."
        
        module_name = module_name_match.group(1)
        
        # Check if it's a pending module
        pending_id = None
        for mid, info in self.pending_modules.items():
            if info["filename"] == module_name or info["filename"].startswith(module_name):
                pending_id = mid
                break
        
        if pending_id:
            # Remove the file from quarantine
            try:
                os.remove(self.pending_modules[pending_id]["path"])
                del self.pending_modules[pending_id]
                return f"Removed pending module '{module_name}' from quarantine."
            except Exception as e:
                self.logger.error(f"Error removing pending module: {e}")
                return f"Error removing pending module: {str(e)}"
        
        # Check if it's a loaded module
        loaded_id = None
        for mid, info in self.loaded_modules.items():
            if info["name"] == module_name:
                loaded_id = mid
                break
        
        if loaded_id:
            # Remove the file from verified directory
            try:
                os.remove(self.loaded_modules[loaded_id]["path"])
                del self.loaded_modules[loaded_id]
                return f"Removed loaded module '{module_name}'."
            except Exception as e:
                self.logger.error(f"Error removing loaded module: {e}")
                return f"Error removing loaded module: {str(e)}"
        
        return f"No module named '{module_name}' found in pending or loaded modules."
    
    def _generate_module_id(self, module_path):
        """
        Generate a unique ID for a module.
        
        Args:
            module_path: Path to the module file
            
        Returns:
            str: Module ID
        """
        try:
            with open(module_path, 'rb') as f:
                content = f.read()
            return hashlib.md5(content).hexdigest()
        except:
            # Fallback to path-based ID
            return f"mod_{hashlib.md5(module_path.encode()).hexdigest()[:8]}"
    
    def get_module(self, module_name):
        """
        Get a loaded module by name.
        Interface for other brain modules to use.
        
        Args:
            module_name: Name of the module
            
        Returns:
            module or None: The loaded module if found
        """
        for info in self.loaded_modules.values():
            if info["name"] == module_name:
                return info["module"]
        return None
    
    def get_class(self, class_name):
        """
        Get a class from a loaded module.
        
        Args:
            class_name: Name of the class
            
        Returns:
            class or None: The class if found
        """
        for info in self.loaded_modules.values():
            for name, cls in info["classes"].items():
                if name == class_name:
                    return cls
        return None
    
    def get_function(self, function_name):
        """
        Get a function from a loaded module.
        
        Args:
            function_name: Name of the function
            
        Returns:
            function or None: The function if found
        """
        for info in self.loaded_modules.values():
            for name, func in info["functions"].items():
                if name == function_name:
                    return func
        return None
    
    def load_from_code(self, code, name=None):
        """
        Load a module from code string.
        
        Args:
            code: Python code string
            name: Optional module name
            
        Returns:
            dict: Load result
        """
        if not name:
            name = f"dynamic_module_{int(time.time())}"
        
        # First, verify the code
        dangerous_patterns = [
            "os.system", "subprocess", "pty", "socket", "requests.delete",
            "shutil.rmtree", "__import__('os').system", "eval(", "exec(",
            r"\.remove\(", r"\.unlink\(", r"os\.remove", r"os\.unlink"
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, code):
                return {
                    "success": False,
                    "error": f"Code contains potentially dangerous pattern: {pattern}"
                }
        
        try:
            # Create a module from code
            module = types.ModuleType(name)
            exec(code, module.__dict__)
            
            # Extract classes and functions
            classes = {}
            functions = {}
            
            for obj_name, obj in inspect.getmembers(module):
                if inspect.isclass(obj) and obj.__module__ == name:
                    classes[obj_name] = obj
                elif inspect.isfunction(obj) and obj.__module__ == name:
                    functions[obj_name] = obj
            
            # Generate an ID for the module
            module_id = f"dynamic_{hashlib.md5(code.encode()).hexdigest()[:8]}"
            
            # Add to loaded modules
            self.loaded_modules[module_id] = {
                "name": name,
                "module": module,
                "classes": classes,
                "functions": functions,
                "loaded": time.time(),
                "dynamic": True
            }
            
            return {
                "success": True,
                "module_id": module_id,
                "module": module
            }
            
        except Exception as e:
            self.logger.error(f"Error loading code as module: {e}")
            return {
                "success": False,
                "error": str(e)
            }
