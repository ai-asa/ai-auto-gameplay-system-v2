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
            '--game-info',
            type=str,
            help='Information to play game'
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
                     config.get('GAMEPLAY', 'game_title', fallback=None) or 
                     self._get_interactive_input('Enter game title: '))
        
        save_name = (args.save_name or 
                    config.get('GAMEPLAY', 'save_name', fallback=None) or 
                    self._get_interactive_input('Enter save name: '))
        
        play_target = (args.play_target or 
                      config.get('GAMEPLAY', 'play_target', fallback=None) or 
                      self._get_interactive_input('Enter play target: '))
        
        game_info = (args.game_info or 
                      config.get('GAMEPLAY', 'game_info', fallback=None) or 
                      self._get_interactive_input('Enter game information: '))
        
        return game_title, save_name, play_target, game_info
    
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
    
    source_dir = "config//gamedata"
    dest_dir = "config//gamedata"
    copy_directory_to_documents(source_dir, dest_dir)

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

def copy_directory_to_documents(source_relative_dir: str, dest_relative_dir: str) -> None:
    """Copy all files from a source directory to a destination directory in the documents directory."""
    source_dir_path = resource_path(source_relative_dir)
    dest_dir_path = os.path.join(get_base_documents_dir(), dest_relative_dir)
    
    if not os.path.exists(dest_dir_path):
        os.makedirs(dest_dir_path)
        print(f"Created directory: {dest_dir_path}")
    
    if os.path.exists(source_dir_path):
        for item in os.listdir(source_dir_path):
            source_item_path = os.path.join(source_dir_path, item)
            dest_item_path = os.path.join(dest_dir_path, item)
            
            if os.path.isfile(source_item_path):
                if not os.path.exists(dest_item_path):
                    try:
                        shutil.copyfile(source_item_path, dest_item_path)
                        print(f"Copied {source_item_path} to {dest_item_path}")
                    except Exception as e:
                        print(f"Error copying {source_item_path} to {dest_item_path}: {e}")
    else:
        print(f"Source directory {source_dir_path} does not exist.")
    
def main():
    # try:
    # Initialize system
    setup_directories()
    copy_required_files()
    
    # Get configuration
    config = GameplayConfiguration()
    game_title, save_name, play_target, game_info = config.get_configuration()
    
    # Initialize game system
    from game_play_system import GamePlaySystem
    base_dir = get_base_documents_dir()
    gs = GamePlaySystem(base_dir, game_title, save_name, play_target, game_info)
    
    # Set up multiprocessing
    queue_advice = multiprocessing.Queue()
    exit_event = multiprocessing.Event()
    
    # Run the game system
    try:
        gs.gemini_loop_gameplay(exit_event, queue_advice)
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