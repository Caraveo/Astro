#!/usr/bin/env python3

import os
import sys
import gi
import threading
import subprocess
import signal
import json
from pathlib import Path

gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gtk, Gdk, GLib

# Import our custom components
from voice.voice_interface import VoiceInterface
from ui.grid_wm import GridWindowManager
from ai.ollama_assistant import OllamaAssistant, VoiceCommandProcessor

class AstroDistro:
    def __init__(self):
        # Create necessary directories
        self.config_dir = Path.home() / '.config' / 'astrodistro'
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.init_components()
        
        # Set up signal handlers
        self.setup_signal_handlers()
    
    def init_components(self):
        """Initialize all system components."""
        try:
            # Start Ollama if not running
            self.start_ollama()
            
            # Initialize AI assistant
            self.assistant = OllamaAssistant()
            self.command_processor = VoiceCommandProcessor(self.assistant)
            
            # Initialize window manager
            self.wm = GridWindowManager()
            
            # Initialize voice interface
            self.voice_interface = VoiceInterface()
            
            # Connect voice interface to command processor
            self.voice_interface.connect('command-received', self.on_command_received)
            
            print("All components initialized successfully")
        
        except Exception as e:
            print(f"Error initializing components: {e}")
            sys.exit(1)
    
    def start_ollama(self):
        """Start Ollama if it's not already running."""
        try:
            # Check if Ollama is running
            subprocess.run(['pgrep', 'ollama'], check=True, capture_output=True)
        except subprocess.CalledProcessError:
            print("Starting Ollama...")
            subprocess.Popen(['ollama', 'serve'])
    
    def setup_signal_handlers(self):
        """Set up signal handlers for graceful shutdown."""
        signal.signal(signal.SIGINT, self.handle_shutdown)
        signal.signal(signal.SIGTERM, self.handle_shutdown)
    
    def handle_shutdown(self, signum, frame):
        """Handle system shutdown."""
        print("\nShutting down AstroDistro...")
        
        # Save window layout
        self.wm.save_layout()
        
        # Clean up resources
        self.assistant.clear_history()
        
        # Exit gracefully
        Gtk.main_quit()
        sys.exit(0)
    
    def on_command_received(self, widget, command):
        """Handle voice commands."""
        self.command_processor.add_command(command)
    
    def run(self):
        """Start the main event loop."""
        try:
            Gtk.main()
        except Exception as e:
            print(f"Error in main loop: {e}")
            self.handle_shutdown(None, None)

def main():
    # Set up environment
    os.environ['GTK_THEME'] = 'Adwaita'
    os.environ['GDK_SCALE'] = '1'
    
    # Create and run the system
    system = AstroDistro()
    system.run()

if __name__ == '__main__':
    main() 