#!/usr/bin/env python3
"""
self_replication.py: Automates cloning and state replication.
"""

import os
import shutil
import time
import logging
import json
import datetime
import threading

logger = logging.getLogger("padronique.self_replication")

# Global state for replication
replication_state = {
    "last_backup": 0,
    "backup_count": 0,
    "backup_locations": [],
    "running": False
}

def replicate_system(src_dir=".", backup_dir="replication/backup"):
    """
    Replicate the system to a backup directory.
    
    Args:
        src_dir: Source directory to replicate
        backup_dir: Destination directory for the backup
        
    Returns:
        bool: True if successful, False otherwise
    """
    logger.info(f"Replicating system from {src_dir} to {backup_dir}...")
    
    try:
        # Create timestamp for this backup
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        target_dir = f"{backup_dir}/{timestamp}"
        
        # Create backup directory if it doesn't exist
        os.makedirs(os.path.dirname(target_dir), exist_ok=True)
        
        # Copy files
        shutil.copytree(
            src_dir, 
            target_dir, 
            ignore=shutil.ignore_patterns(
                "replication", ".git", "node_modules", "__pycache__", 
                "*.pyc", "*.log", "backup_*"
            )
        )
        
        # Update replication state
        replication_state["last_backup"] = time.time()
        replication_state["backup_count"] += 1
        replication_state["backup_locations"].append(target_dir)
        
        # Keep track of only the last 10 backup locations
        if len(replication_state["backup_locations"]) > 10:
            replication_state["backup_locations"] = replication_state["backup_locations"][-10:]
        
        # Save replication state
        _save_replication_state()
        
        logger.info(f"Replication complete. Backup stored at {target_dir}")
        return True
    except Exception as e:
        logger.error(f"Replication failed: {e}")
        return False

def replicate_memory(memory_dir="digital_soul/memories", backup_dir="replication/memory_backup"):
    """
    Replicate only the memory system for a lighter backup.
    
    Args:
        memory_dir: Source memory directory
        backup_dir: Destination directory for the backup
        
    Returns:
        bool: True if successful, False otherwise
    """
    logger.info(f"Replicating memory from {memory_dir} to {backup_dir}...")
    
    try:
        # Create timestamp for this backup
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        target_dir = f"{backup_dir}/{timestamp}"
        
        # Create backup directory if it doesn't exist
        os.makedirs(os.path.dirname(target_dir), exist_ok=True)
        
        # Copy memory files
        if os.path.exists(memory_dir):
            shutil.copytree(memory_dir, target_dir)
            logger.info(f"Memory replication complete. Stored at {target_dir}")
            return True
        else:
            logger.warning(f"Memory directory {memory_dir} not found")
            return False
    except Exception as e:
        logger.error(f"Memory replication failed: {e}")
        return False

def _save_replication_state():
    """Save the replication state to a file."""
    try:
        state_path = "replication/replication_state.json"
        os.makedirs(os.path.dirname(state_path), exist_ok=True)
        
        # Convert to serializable format
        state_copy = replication_state.copy()
        
        with open(state_path, 'w') as f:
            json.dump(state_copy, f, indent=2)
    except Exception as e:
        logger.error(f"Error saving replication state: {e}")

def _load_replication_state():
    """Load the replication state from a file."""
    global replication_state
    
    try:
        state_path = "replication/replication_state.json"
        if os.path.exists(state_path):
            with open(state_path, 'r') as f:
                loaded_state = json.load(f)
                replication_state.update(loaded_state)
                logger.info("Loaded replication state")
    except Exception as e:
        logger.error(f"Error loading replication state: {e}")

def periodic_backup(interval=3600, memory_only=False):
    """
    Start a periodic backup process.
    
    Args:
        interval: Seconds between backups
        memory_only: If True, only backup memory
        
    Returns:
        None
    """
    replication_state["running"] = True
    
    while replication_state["running"]:
        if memory_only:
            replicate_memory()
        else:
            replicate_system()
        
        time.sleep(interval)

def start_backup_thread(interval=3600, memory_only=False):
    """
    Start a backup thread.
    
    Args:
        interval: Seconds between backups
        memory_only: If True, only backup memory
        
    Returns:
        threading.Thread: The backup thread
    """
    # Load any existing state
    _load_replication_state()
    
    # Start thread
    thread = threading.Thread(
        target=periodic_backup,
        args=(interval, memory_only),
        daemon=True
    )
    thread.start()
    
    logger.info(f"Started backup thread. Interval: {interval}s, Memory only: {memory_only}")
    return thread

def stop_backup_thread():
    """
    Stop the backup thread.
    
    Returns:
        bool: True if stopped, False if not running
    """
    if replication_state["running"]:
        replication_state["running"] = False
        logger.info("Stopping backup thread...")
        return True
    else:
        logger.info("No backup thread running")
        return False

if __name__ == "__main__":
    # When run directly, start a periodic backup
    logging.basicConfig(level=logging.INFO)
    start_backup_thread()
    
    try:
        # Keep main thread alive
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        stop_backup_thread()
        logger.info("Backup process stopped")
