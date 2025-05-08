"""
Memory Backup Manager

This module handles automatic backup of memory data to ensure no data is ever lost.
It provides scheduled backups as well as emergency backup functionality in case of system errors.
"""

import json
import os
import shutil
import time
import logging
import threading
import datetime
import yaml
import gzip
import signal
import atexit
from pathlib import Path

logger = logging.getLogger(__name__)

class BackupManager:
    """Manages automatic backups of memory data to prevent data loss."""
    
    def __init__(self, config_path="./config.yaml"):
        """
        Initialize the backup manager.
        
        Args:
            config_path (str): Path to the configuration file
        """
        self.config = self._load_config(config_path)
        self.backup_config = self.config.get('memory', {}).get('auto_backup', {})
        
        self.enabled = self.backup_config.get('enabled', True)
        self.interval_minutes = self.backup_config.get('interval_minutes', 30)
        self.max_backups = self.backup_config.get('max_backups', 5)
        self.backup_location = self.backup_config.get('backup_location', './memory/backups/')
        
        # Ensure backup directory exists
        os.makedirs(self.backup_location, exist_ok=True)
        
        # Setup emergency backup on exit
        atexit.register(self.emergency_backup)
        
        # Set up signal handlers for crash detection
        signal.signal(signal.SIGTERM, self._handle_exit_signal)
        signal.signal(signal.SIGINT, self._handle_exit_signal)
        
        if self.enabled:
            self.backup_thread = None
            self.stop_event = threading.Event()
            logger.info(f"Memory backup system initialized. Backups will be stored in {self.backup_location}")
        else:
            logger.warning("Automatic memory backup is disabled in configuration")
    
    def _load_config(self, config_path):
        """
        Load configuration from the YAML file.
        
        Args:
            config_path (str): Path to the configuration file
            
        Returns:
            dict: Configuration data
        """
        try:
            with open(config_path, 'r') as file:
                return yaml.safe_load(file)
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            # Return default configuration
            return {
                'memory': {
                    'auto_backup': {
                        'enabled': True,
                        'interval_minutes': 30,
                        'max_backups': 5,
                        'backup_location': './memory/backups/'
                    }
                }
            }
    
    def start_scheduled_backups(self):
        """Start the scheduled backup thread if enabled."""
        if not self.enabled:
            logger.warning("Automatic backups are disabled, not starting scheduled backups")
            return
        
        if self.backup_thread and self.backup_thread.is_alive():
            logger.warning("Backup thread is already running")
            return
        
        self.stop_event.clear()
        self.backup_thread = threading.Thread(target=self._backup_thread_function, daemon=True)
        self.backup_thread.start()
        logger.info(f"Scheduled memory backups started. Interval: {self.interval_minutes} minutes")
    
    def stop_scheduled_backups(self):
        """Stop the scheduled backup thread."""
        if self.backup_thread and self.backup_thread.is_alive():
            self.stop_event.set()
            self.backup_thread.join(timeout=10)
            logger.info("Scheduled memory backups stopped")
    
    def _backup_thread_function(self):
        """Thread function that performs periodic backups."""
        while not self.stop_event.is_set():
            try:
                self.create_backup()
                # Wait for the next backup interval, checking every 60 seconds if we should stop
                for _ in range(self.interval_minutes):
                    if self.stop_event.wait(60):  # Wait for 60 seconds or until stop event
                        break
            except Exception as e:
                logger.error(f"Error in backup thread: {e}")
                # Wait a shorter time if there was an error
                if self.stop_event.wait(300):  # 5 minutes
                    break
    
    def create_backup(self, backup_name=None):
        """
        Create a backup of all memory data.
        
        Args:
            backup_name (str, optional): Custom name for the backup. If not provided,
                                        a timestamp-based name will be used.
                                        
        Returns:
            str: Path to the created backup file
        """
        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = backup_name or f"memory_backup_{timestamp}"
            backup_file = os.path.join(self.backup_location, f"{backup_name}.json.gz")
            
            # Collect all memory data
            memory_data = self._collect_memory_data()
            
            # Save to compressed file
            with gzip.open(backup_file, 'wt', encoding='utf-8') as f:
                json.dump(memory_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Memory backup created successfully: {backup_file}")
            
            # Cleanup old backups if needed
            self._cleanup_old_backups()
            
            return backup_file
        
        except Exception as e:
            logger.error(f"Failed to create memory backup: {e}")
            # Try to create an emergency backup
            try:
                return self.emergency_backup(f"emergency_{timestamp}")
            except Exception as e2:
                logger.critical(f"Emergency backup also failed: {e2}")
                return None
    
    def emergency_backup(self, backup_name=None):
        """
        Create an emergency backup when a crash or unexpected exit is detected.
        This function uses a simplified approach to maximize chance of success.
        
        Args:
            backup_name (str, optional): Custom name for the emergency backup
            
        Returns:
            str: Path to the created emergency backup file
        """
        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = backup_name or f"emergency_backup_{timestamp}"
            backup_file = os.path.join(self.backup_location, f"{backup_name}.json")
            
            # Collect memory data with minimal processing
            memory_data = self._collect_memory_data(emergency=True)
            
            # Save to regular (non-compressed) file for maximum reliability
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(memory_data, f, ensure_ascii=False)
            
            logger.info(f"Emergency memory backup created: {backup_file}")
            return backup_file
        
        except Exception as e:
            logger.critical(f"Critical: Failed to create emergency backup: {e}")
            
            # Last resort - try to dump raw data
            try:
                raw_backup_file = os.path.join(self.backup_location, f"raw_emergency_{timestamp}.json")
                with open(raw_backup_file, 'w', encoding='utf-8') as f:
                    f.write(str(self._collect_raw_memory_data()))
                logger.info(f"Raw emergency backup created: {raw_backup_file}")
                return raw_backup_file
            except Exception as e2:
                logger.critical(f"All backup attempts failed: {e2}")
                return None
    
    def _collect_memory_data(self, emergency=False):
        """
        Collect all memory data from various sources.
        
        Args:
            emergency (bool): If True, use more aggressive collection methods
                              that prioritize getting data over format
        
        Returns:
            dict: Collected memory data
        """
        memory_data = {
            'metadata': {
                'timestamp': datetime.datetime.now().isoformat(),
                'version': self.config.get('system', {}).get('version', '1.0.0'),
                'emergency': emergency
            },
            'memories': [],
            'conversations': [],
            'preferences': {}
        }
        
        # Collect from database if available
        try:
            from models import db, Memory, Interaction, UserSettings
            
            with db.session.begin():
                # Get memories
                memories = Memory.query.all()
                memory_data['memories'] = [
                    {
                        'id': m.id,
                        'memory_type': m.memory_type,
                        'content': m.content,
                        'importance': m.importance,
                        'embedding': m.embedding,
                        'created_at': m.created_at.isoformat() if m.created_at else None,
                        'last_accessed': m.last_accessed.isoformat() if m.last_accessed else None,
                        'access_count': m.access_count
                    } for m in memories
                ]
                
                # Get interactions
                interactions = Interaction.query.all()
                memory_data['conversations'] = [
                    {
                        'id': i.id,
                        'timestamp': i.timestamp.isoformat() if i.timestamp else None,
                        'input_text': i.input_text,
                        'response_text': i.response_text,
                        'sentiment_score': i.sentiment_score,
                        'active_brains': i.active_brains,
                        'context_data': i.context_data,
                        'interaction_duration': i.interaction_duration
                    } for i in interactions
                ]
                
                # Get settings
                settings = UserSettings.query.first()
                if settings:
                    memory_data['preferences'] = {
                        'theme': settings.theme,
                        'language': settings.language,
                        'voice_enabled': settings.voice_enabled,
                        'notification_enabled': settings.notification_enabled
                    }
        
        except Exception as e:
            logger.error(f"Failed to collect data from database: {e}")
            if emergency:
                # In emergency mode, try to collect data from other sources
                memory_data = self._collect_raw_memory_data()
        
        return memory_data
    
    def _collect_raw_memory_data(self):
        """
        Collect raw memory data from files and any other available sources.
        Last resort for emergency backups.
        
        Returns:
            dict: Raw collected data
        """
        raw_data = {
            'metadata': {
                'timestamp': str(datetime.datetime.now()),
                'emergency': True
            },
            'raw_files': {}
        }
        
        # Try to find and include any JSON files in the memory directory
        memory_dir = Path('./memory')
        if memory_dir.exists():
            for file_path in memory_dir.glob('**/*.json'):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        raw_data['raw_files'][str(file_path)] = f.read()
                except Exception:
                    pass
        
        return raw_data
    
    def _cleanup_old_backups(self):
        """Remove old backups if the number exceeds the configured maximum."""
        if self.max_backups <= 0:  # No limit
            return
        
        try:
            backup_files = []
            for filename in os.listdir(self.backup_location):
                if filename.startswith('memory_backup_') and (filename.endswith('.json.gz') or filename.endswith('.json')):
                    file_path = os.path.join(self.backup_location, filename)
                    backup_files.append((file_path, os.path.getmtime(file_path)))
            
            # Sort by modification time, newest first
            backup_files.sort(key=lambda x: x[1], reverse=True)
            
            # Delete oldest files that exceed the limit
            for file_path, _ in backup_files[self.max_backups:]:
                os.remove(file_path)
                logger.info(f"Removed old backup: {file_path}")
        
        except Exception as e:
            logger.error(f"Error cleaning up old backups: {e}")
    
    def _handle_exit_signal(self, signum, frame):
        """Signal handler for emergency backup on abnormal termination."""
        logger.warning(f"Received exit signal {signum}, creating emergency backup")
        self.emergency_backup()
        # Re-raise the signal to allow normal handling
        signal.signal(signum, signal.SIG_DFL)
        os.kill(os.getpid(), signum)
    
    def restore_from_backup(self, backup_path):
        """
        Restore memory data from a backup file.
        
        Args:
            backup_path (str): Path to the backup file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Determine if the file is compressed
            is_compressed = backup_path.endswith('.gz')
            
            # Load the backup data
            if is_compressed:
                with gzip.open(backup_path, 'rt', encoding='utf-8') as f:
                    backup_data = json.load(f)
            else:
                with open(backup_path, 'r', encoding='utf-8') as f:
                    backup_data = json.load(f)
            
            # Create a backup of current data before restoring
            self.create_backup(backup_name=f"pre_restore_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}")
            
            # Check if we have a database to restore to
            try:
                from models import db, Memory, Interaction, UserSettings, User
                
                # Start a transaction
                with db.session.begin():
                    # Restore memories
                    if 'memories' in backup_data:
                        # Get existing user or create one
                        user = User.query.first()
                        if not user:
                            user = User(username="default", email="default@example.com")
                            user.set_password("default")
                            db.session.add(user)
                            db.session.flush()  # Get ID without committing
                        
                        # Clear existing memories
                        Memory.query.delete()
                        
                        # Add restored memories
                        for memory_data in backup_data['memories']:
                            memory = Memory(
                                user_id=user.id,
                                memory_type=memory_data.get('memory_type', 'fact'),
                                content=memory_data.get('content', ''),
                                importance=memory_data.get('importance', 0.5),
                                embedding=memory_data.get('embedding'),
                                access_count=memory_data.get('access_count', 0)
                            )
                            
                            # Try to parse dates
                            try:
                                if 'created_at' in memory_data and memory_data['created_at']:
                                    memory.created_at = datetime.datetime.fromisoformat(memory_data['created_at'])
                                if 'last_accessed' in memory_data and memory_data['last_accessed']:
                                    memory.last_accessed = datetime.datetime.fromisoformat(memory_data['last_accessed'])
                            except ValueError:
                                pass
                                
                            db.session.add(memory)
                    
                    # Restore interactions
                    if 'conversations' in backup_data:
                        # Clear existing interactions
                        Interaction.query.delete()
                        
                        # Add restored interactions
                        for interaction_data in backup_data['conversations']:
                            interaction = Interaction(
                                user_id=user.id,
                                input_text=interaction_data.get('input_text', ''),
                                response_text=interaction_data.get('response_text', ''),
                                sentiment_score=interaction_data.get('sentiment_score'),
                                active_brains=interaction_data.get('active_brains'),
                                context_data=interaction_data.get('context_data'),
                                interaction_duration=interaction_data.get('interaction_duration')
                            )
                            
                            # Try to parse timestamp
                            try:
                                if 'timestamp' in interaction_data and interaction_data['timestamp']:
                                    interaction.timestamp = datetime.datetime.fromisoformat(interaction_data['timestamp'])
                            except ValueError:
                                pass
                                
                            db.session.add(interaction)
                    
                    # Restore preferences
                    if 'preferences' in backup_data:
                        # Get existing settings or create new
                        settings = UserSettings.query.first()
                        if not settings:
                            settings = UserSettings(user_id=user.id)
                            db.session.add(settings)
                        
                        # Update settings
                        preferences = backup_data['preferences']
                        settings.theme = preferences.get('theme', 'dark')
                        settings.language = preferences.get('language', 'en')
                        settings.voice_enabled = preferences.get('voice_enabled', False)
                        settings.notification_enabled = preferences.get('notification_enabled', True)
                
                logger.info(f"Successfully restored from backup: {backup_path}")
                return True
            
            except Exception as e:
                logger.error(f"Failed to restore to database: {e}")
                # If database restore fails, try to save the data to files
                self._restore_to_files(backup_data)
                return False
        
        except Exception as e:
            logger.error(f"Failed to restore from backup: {e}")
            return False
    
    def _restore_to_files(self, backup_data):
        """
        Fallback method to restore data to files when database is unavailable.
        
        Args:
            backup_data (dict): The backup data to restore
        """
        try:
            # Create restore directory
            restore_dir = os.path.join(self.backup_location, 'restore_' + datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))
            os.makedirs(restore_dir, exist_ok=True)
            
            # Save memories
            if 'memories' in backup_data:
                with open(os.path.join(restore_dir, 'memories.json'), 'w', encoding='utf-8') as f:
                    json.dump(backup_data['memories'], f, ensure_ascii=False, indent=2)
            
            # Save conversations
            if 'conversations' in backup_data:
                with open(os.path.join(restore_dir, 'conversations.json'), 'w', encoding='utf-8') as f:
                    json.dump(backup_data['conversations'], f, ensure_ascii=False, indent=2)
            
            # Save preferences
            if 'preferences' in backup_data:
                with open(os.path.join(restore_dir, 'preferences.json'), 'w', encoding='utf-8') as f:
                    json.dump(backup_data['preferences'], f, ensure_ascii=False, indent=2)
            
            logger.info(f"Backup data restored to files in directory: {restore_dir}")
        
        except Exception as e:
            logger.error(f"Failed to restore to files: {e}")

# Singleton instance
backup_manager = None

def get_backup_manager():
    """Get or create the backup manager singleton instance."""
    global backup_manager
    if backup_manager is None:
        backup_manager = BackupManager()
    return backup_manager

# Automatically initialize the backup manager when this module is imported
backup_manager = get_backup_manager()