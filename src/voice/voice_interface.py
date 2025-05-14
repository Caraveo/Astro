import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gtk, Gdk, GLib, GObject
import cairo
import math
import threading
import queue
import sounddevice as sd
import numpy as np
import speech_recognition as sr
import json
import os
from datetime import datetime

class VoiceInterface(Gtk.Window):
    def __init__(self):
        super().__init__()
        
        # Initialize window properties
        self.set_decorated(False)
        self.set_keep_above(True)
        self.set_skip_taskbar_hint(True)
        self.set_skip_pager_hint(True)
        self.set_type_hint(Gdk.WindowTypeHint.DOCK)
        self.set_app_paintable(True)
        
        # Set window size and position
        self.set_size_request(100, 100)
        screen = Gdk.Screen.get_default()
        self.move(screen.get_width() - 120, 20)
        
        # Initialize voice recognition
        self.recognizer = sr.Recognizer()
        self.audio_queue = queue.Queue()
        self.is_listening = False
        self.animation_value = 0
        self.animation_direction = 1
        
        # Create drawing area
        self.drawing_area = Gtk.DrawingArea()
        self.drawing_area.connect('draw', self.on_draw)
        self.add(self.drawing_area)
        
        # Start animation
        GLib.timeout_add(50, self.animate)
        
        # Start voice recognition thread
        self.voice_thread = threading.Thread(target=self.voice_recognition_loop)
        self.voice_thread.daemon = True
        self.voice_thread.start()
        
        # Connect signals
        self.connect('destroy', Gtk.main_quit)
        self.connect('button-press-event', self.on_button_press)
        self.connect('button-release-event', self.on_button_release)
        
        # Show window
        self.show_all()
    
    def on_draw(self, widget, context):
        # Get window dimensions
        width = widget.get_allocated_width()
        height = widget.get_allocated_height()
        
        # Clear background
        context.set_source_rgba(0, 0, 0, 0)
        context.paint()
        
        # Draw animated circle
        center_x = width / 2
        center_y = height / 2
        radius = min(width, height) / 2 * 0.8
        
        # Create gradient
        gradient = cairo.RadialGradient(
            center_x, center_y, 0,
            center_x, center_y, radius
        )
        
        # Add gradient stops with animation
        alpha = 0.3 + 0.2 * math.sin(self.animation_value)
        gradient.add_color_stop_rgba(0, 0.2, 0.4, 0.8, alpha)
        gradient.add_color_stop_rgba(1, 0.1, 0.2, 0.4, 0)
        
        context.set_source(gradient)
        context.arc(center_x, center_y, radius, 0, 2 * math.pi)
        context.fill()
        
        return True
    
    def animate(self):
        self.animation_value += 0.1
        self.drawing_area.queue_draw()
        return True
    
    def voice_recognition_loop(self):
        while True:
            try:
                with sr.Microphone() as source:
                    self.recognizer.adjust_for_ambient_noise(source)
                    audio = self.recognizer.listen(source)
                    
                    try:
                        text = self.recognizer.recognize_google(audio)
                        self.process_command(text.lower())
                    except sr.UnknownValueError:
                        pass
                    except sr.RequestError as e:
                        print(f"Could not request results; {e}")
            except Exception as e:
                print(f"Error in voice recognition: {e}")
    
    def process_command(self, command):
        # Process voice commands
        if "open" in command:
            # Handle application opening
            pass
        elif "close" in command:
            # Handle window closing
            pass
        elif "help" in command:
            # Show help
            pass
    
    def on_button_press(self, widget, event):
        if event.button == 1:  # Left click
            self.is_listening = True
            self.drawing_area.queue_draw()
    
    def on_button_release(self, widget, event):
        if event.button == 1:  # Left click
            self.is_listening = False
            self.drawing_area.queue_draw()

if __name__ == '__main__':
    Gtk.init()
    app = VoiceInterface()
    Gtk.main() 