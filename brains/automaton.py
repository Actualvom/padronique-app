#!/usr/bin/env python3
"""
automaton.py: Handles automated tasks and scheduling.
"""

import time
import threading
import logging
from brains.base_brain import BaseBrain

class Automaton(BaseBrain):
    """
    Automaton brain responsible for automated tasks and scheduling.
    Manages background processes and maintenance routines.
    """
    
    def __init__(self):
        """Initialize the Automaton brain."""
        super().__init__("Automaton")
        self.digital_soul = None  # Will be set by orchestrator
        self.tasks = {}  # Dictionary of scheduled tasks
        self.running_tasks = {}  # Currently running tasks
        self._task_lock = threading.Lock()
        self._shutdown = False
        self._scheduler_thread = None
        self._start_scheduler()
    
    def _start_scheduler(self):
        """Start the scheduler thread."""
        self._scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self._scheduler_thread.start()
        self.logger.info("Task scheduler started")
    
    def _scheduler_loop(self):
        """Main loop for the task scheduler."""
        while not self._shutdown:
            try:
                current_time = time.time()
                
                with self._task_lock:
                    # Find tasks that need to run
                    tasks_to_run = []
                    for task_id, task in self.tasks.items():
                        if current_time >= task["next_run"] and not task.get("running", False):
                            tasks_to_run.append(task_id)
                
                # Run due tasks
                for task_id in tasks_to_run:
                    self._run_task(task_id)
            
            except Exception as e:
                self.logger.error(f"Error in scheduler loop: {e}")
            
            # Sleep before checking again
            time.sleep(1)
    
    def _run_task(self, task_id):
        """
        Run a scheduled task.
        
        Args:
            task_id: ID of the task to run
        """
        with self._task_lock:
            if task_id not in self.tasks:
                return
            
            task = self.tasks[task_id]
            task["running"] = True
            task["last_run"] = time.time()
            
            # Calculate next run time
            if task["interval"]:
                task["next_run"] = task["last_run"] + task["interval"]
            else:
                # One-time task, remove after running
                self.tasks.pop(task_id)
        
        # Start task in a separate thread
        thread = threading.Thread(
            target=self._execute_task_wrapper,
            args=(task_id, task["function"], task["args"], task["kwargs"]),
            daemon=True
        )
        thread.start()
        
        self.running_tasks[task_id] = {
            "thread": thread,
            "start_time": time.time()
        }
        
        self.logger.info(f"Started task: {task_id}")
    
    def _execute_task_wrapper(self, task_id, func, args, kwargs):
        """
        Wrapper to execute a task and handle errors.
        
        Args:
            task_id: Task ID
            func: Function to call
            args: Function arguments
            kwargs: Function keyword arguments
        """
        try:
            result = func(*args, **kwargs)
            self.logger.debug(f"Task {task_id} completed successfully")
            
            # Record result if digital soul is available
            if hasattr(self, 'digital_soul') and self.digital_soul:
                self.digital_soul.add_memory(
                    "interaction", 
                    {"task_id": task_id, "result": "success", "details": str(result)},
                    tags=["automated_task", f"task:{task_id}", "success"]
                )
                
        except Exception as e:
            self.logger.error(f"Error executing task {task_id}: {e}")
            
            # Record error if digital soul is available
            if hasattr(self, 'digital_soul') and self.digital_soul:
                self.digital_soul.add_memory(
                    "interaction", 
                    {"task_id": task_id, "result": "error", "details": str(e)},
                    tags=["automated_task", f"task:{task_id}", "error"]
                )
        
        finally:
            # Mark task as no longer running
            with self._task_lock:
                if task_id in self.tasks:
                    self.tasks[task_id]["running"] = False
            
            # Remove from running tasks
            if task_id in self.running_tasks:
                self.running_tasks.pop(task_id)
    
    def process_input(self, input_data):
        """
        Process input data to check for automation commands.
        
        Args:
            input_data: Input data to process
            
        Returns:
            str: Response or None
        """
        super().process_input(input_data)
        
        # Skip cycle updates
        if input_data == "Cycle update":
            return None
        
        # Check for automation-related commands
        if "schedule" in input_data.lower() or "automate" in input_data.lower():
            return "I can help you automate tasks. Please provide more details about what you'd like to schedule."
        
        return None
    
    def schedule_task(self, task_id, function, interval=None, run_at=None, args=None, kwargs=None):
        """
        Schedule a task to run.
        
        Args:
            task_id: Unique identifier for the task
            function: Function to call
            interval: Seconds between runs (None for one-time tasks)
            run_at: Specific time to run (None for immediate or interval-based)
            args: Function arguments
            kwargs: Function keyword arguments
            
        Returns:
            bool: True if scheduled successfully
        """
        args = args or ()
        kwargs = kwargs or {}
        
        # Determine when to run
        if run_at:
            next_run = run_at
        else:
            next_run = time.time()
        
        with self._task_lock:
            self.tasks[task_id] = {
                "function": function,
                "interval": interval,
                "next_run": next_run,
                "last_run": None,
                "running": False,
                "args": args,
                "kwargs": kwargs
            }
        
        self.logger.info(f"Scheduled task: {task_id}, Interval: {interval}s, Next run: {next_run}")
        return True
    
    def cancel_task(self, task_id):
        """
        Cancel a scheduled task.
        
        Args:
            task_id: ID of the task to cancel
            
        Returns:
            bool: True if cancelled, False if not found
        """
        with self._task_lock:
            if task_id in self.tasks:
                self.tasks.pop(task_id)
                self.logger.info(f"Cancelled task: {task_id}")
                return True
            else:
                self.logger.warning(f"Task not found for cancellation: {task_id}")
                return False
    
    def list_tasks(self):
        """
        List all scheduled tasks.
        
        Returns:
            dict: Dictionary of tasks and their details
        """
        with self._task_lock:
            # Create a copy with serializable values
            tasks_copy = {}
            current_time = time.time()
            
            for task_id, task in self.tasks.items():
                # Format timestamps as relative times
                next_run_in = task["next_run"] - current_time if task["next_run"] else None
                last_run_ago = current_time - task["last_run"] if task["last_run"] else None
                
                tasks_copy[task_id] = {
                    "interval": task["interval"],
                    "next_run_in_seconds": next_run_in,
                    "last_run_ago_seconds": last_run_ago,
                    "running": task["running"]
                }
            
            return tasks_copy
    
    def shutdown(self):
        """Shutdown the scheduler."""
        self._shutdown = True
        if self._scheduler_thread:
            self._scheduler_thread.join(timeout=5.0)
        self.logger.info("Task scheduler shutdown")
