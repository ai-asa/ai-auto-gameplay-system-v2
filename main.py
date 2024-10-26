import os
import sys
import shutil
import argparse
import configparser
import multiprocessing
from typing import Tuple

class GameplayConfiguration:
    def __init__(self):
        self.parser = self._create_parser()
        
    def _create_parser(self) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(
            description='AI Game Play System - Automated gameplay with AI assistance',
            formatter_class=argparse.RawDescriptionHelpFormatter
        )
        
        parser.add_argument(
            '--game-title',
            type=str,
            help='Title of the game to be played'
        )
        
        parser.add_argument(
            '--save-name',
            type=str,
            help='Name of the save file/slot to use'
        )
        
        parser.add_argument(
            '--play-target',
            type=str,
            help='Target objective for the gameplay session'
        )
        
        parser.add_argument(
            '--config',
            type=str,
            help='Path to custom configuration file'
        )
        
        return parser
    
    def _load_config_file(self, config_path: str) -> configparser.ConfigParser:
        config = configparser.ConfigParser()
        if os.path.exists(config_path):
            config.read(config_path, encoding='utf-8')
        return config
    
    def get_configuration(self) -> Tuple[str, str, str]:
        args = self.parser.parse_args()
        
        # Try loading from config file first
        config_file = args.config or os.path.join(get_base_documents_dir(), 'config', 'gameplay_config.ini')
        config = self._load_config_file(config_file)
        
        # Get values with priority: CLI args > config file > interactive input
        game_title = (args.game_title or 
                     config.get('Gameplay', 'game_title', fallback=None) or 
                     self._get_interactive_input('Enter game title: '))
        
        save_name = (args.save_name or 
                    config.get('Gameplay', 'save_name', fallback=None) or 
                    self._get_interactive_input('Enter save name: '))
        
        play_target = (args.play_target or 
                      config.get('Gameplay', 'play_target', fallback=None) or 
                      self._get_interactive_input('Enter play target: '))
        
        return game_title, save_name, play_target
    
    def _get_interactive_input(self, prompt: str) -> str:
        return input(prompt)

def get_documents_dir() -> str:
    return os.path.join(os.environ['USERPROFILE'], 'Documents')

def get_base_documents_dir() -> str:
    return os.path.join(get_documents_dir(), 'AIGamePlaySystem')

def resource_path(relative_path: str) -> str:
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def setup_directories() -> None:
    """Initialize required directories and copy necessary files."""
    base_dir = get_base_documents_dir()
    directories = ['settings', 'config']
    
    for directory in directories:
        dir_path = os.path.join(base_dir, directory)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
            print(f"Created directory: {dir_path}")

def copy_required_files() -> None:
    """Copy required configuration files to the documents directory."""
    files_to_copy = [
        ("settings//settings.ini", "settings//settings.ini"),
        ("config//gameplay_config.ini", "config//gameplay_config.ini")
    ]
    
    for source, dest in files_to_copy:
        copy_file_to_documents(source, dest)

def copy_file_to_documents(source_relative_path: str, dest_relative_path: str) -> None:
    source_path = resource_path(source_relative_path)
    dest_path = os.path.join(get_base_documents_dir(), dest_relative_path)
    
    dest_dir = os.path.dirname(dest_path)
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
    
    if not os.path.exists(dest_path):
        try:
            shutil.copyfile(source_path, dest_path)
            print(f"Copied {source_path} to {dest_path}")
        except Exception as e:
            print(f"Error copying {source_path} to {dest_path}: {e}")
    
def main():
    # try:
    # Initialize system
    setup_directories()
    copy_required_files()
    
    # Get configuration
    config = GameplayConfiguration()
    game_title, save_name, play_target = config.get_configuration()
    
    # Initialize game system
    from game_play_system import GamePlaySystem
    base_dir = get_base_documents_dir()
    gs = GamePlaySystem(base_dir, game_title, save_name, play_target)
    
    # Set up multiprocessing
    queue_advice = multiprocessing.Queue()
    exit_event = multiprocessing.Event()
    
    # Run the game system
    try:
        gs.loop_gameplay(exit_event, queue_advice)
    except KeyboardInterrupt:
        print("\nShutting down gracefully...")
        exit_event.set()
    finally:
        queue_advice.close()
        queue_advice.join_thread()
            
    # except Exception as e:
    #     print(f"Error during execution: {e}")
    #     sys.exit(1)

if __name__ == "__main__":
    main()