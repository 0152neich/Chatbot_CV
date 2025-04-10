# shared/state.py
import os
import json
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

class StateManager:
    def __init__(self, state_file: str):
        """Initialize StateManager with the path to the state file.

        Args:
            state_file (str): Path to the file storing the state.
        """
        self.state_file = state_file

    def get_folder_state(self, folder_path: str, file_extension: str = None) -> Dict[str, float]:
        """Get the current state of the folder (file names and modification times).

        Args:
            folder_path (str): Path to the folder.
            file_extension (str, optional): Filter files by extension (e.g., '.md').

        Returns:
            Dict[str, float]: Dictionary of filenames and their modification times.
        """
        current_state = {}
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            if os.path.isfile(file_path) and (file_extension is None or filename.lower().endswith(file_extension)):
                current_state[filename] = os.path.getmtime(file_path)
        return current_state

    def load_previous_state(self) -> Dict[str, float]:
        """Load the previous state from the state file.

        Returns:
            Dict[str, float]: Previous state or empty dict if file doesn't exist.
        """
        try:
            with open(self.state_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            logger.info(f"No previous state found at {self.state_file}. Treating as first run.")
            return {}

    def save_state(self, state: Dict[str, float]) -> None:
        """Save the current state to the state file.

        Args:
            state (Dict[str, float]): State to save.
        """
        try:
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(state, f)
            logger.info(f"Saved state to {self.state_file}")
        except Exception as e:
            logger.error(f"Error saving state to {self.state_file}: {str(e)}")
            raise

    def get_new_files(self, current_state: Dict[str, float], previous_state: Dict[str, float]) -> List[str]:
        """Identify new or changed files by comparing current and previous states.

        Args:
            current_state (Dict[str, float]): Current state of the folder.
            previous_state (Dict[str, float]): Previous state of the folder.

        Returns:
            List[str]: List of new or changed filenames.
        """
        new_files = []
        for filename, mtime in current_state.items():
            if filename not in previous_state or previous_state[filename] != mtime:
                new_files.append(filename)
        return new_files