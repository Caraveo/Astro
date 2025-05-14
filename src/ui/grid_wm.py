import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gtk, Gdk, GLib, GObject
import cairo
import math
import json
import os

class GridWindowManager:
    def __init__(self):
        self.display = Gdk.Display.get_default()
        self.screen = self.display.get_default_screen()
        self.windows = {}
        self.grid_size = 4  # 4x4 grid
        self.current_layout = {}
        
        # Initialize window tracking
        self.display.connect('window-created', self.on_window_created)
        
        # Load saved layout
        self.load_layout()
    
    def on_window_created(self, display, window):
        if window.get_type_hint() == Gdk.WindowTypeHint.NORMAL:
            self.windows[window.get_xid()] = {
                'window': window,
                'position': None,
                'size': None
            }
            self.arrange_window(window)
    
    def arrange_window(self, window):
        # Find first available grid position
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                if not self.is_position_occupied(i, j):
                    self.place_window(window, i, j)
                    return
    
    def place_window(self, window, grid_x, grid_y):
        # Calculate window position and size
        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()
        
        cell_width = screen_width / self.grid_size
        cell_height = screen_height / self.grid_size
        
        x = int(grid_x * cell_width)
        y = int(grid_y * cell_height)
        width = int(cell_width)
        height = int(cell_height)
        
        # Set window properties
        window.set_decorated(False)
        window.set_skip_taskbar_hint(True)
        
        # Make window transparent
        window.set_opacity(0.9)
        
        # Move and resize window
        window.move(x, y)
        window.resize(width, height)
        
        # Store window position
        self.windows[window.get_xid()]['position'] = (grid_x, grid_y)
        self.windows[window.get_xid()]['size'] = (width, height)
        
        # Save layout
        self.save_layout()
    
    def is_position_occupied(self, grid_x, grid_y):
        for window_data in self.windows.values():
            if window_data['position'] == (grid_x, grid_y):
                return True
        return False
    
    def save_layout(self):
        layout = {}
        for xid, data in self.windows.items():
            if data['position'] is not None:
                layout[str(xid)] = {
                    'position': data['position'],
                    'size': data['size']
                }
        
        with open(os.path.expanduser('~/.config/astrodistro/layout.json'), 'w') as f:
            json.dump(layout, f)
    
    def load_layout(self):
        try:
            with open(os.path.expanduser('~/.config/astrodistro/layout.json'), 'r') as f:
                self.current_layout = json.load(f)
        except FileNotFoundError:
            self.current_layout = {}
    
    def apply_layout(self):
        for xid, data in self.current_layout.items():
            if int(xid) in self.windows:
                window = self.windows[int(xid)]['window']
                self.place_window(window, *data['position'])

class TransparentWindow(Gtk.Window):
    def __init__(self):
        super().__init__()
        
        # Set window properties
        self.set_decorated(False)
        self.set_app_paintable(True)
        self.set_opacity(0.9)
        
        # Create transparent background
        self.connect('draw', self.on_draw)
        
        # Add content
        self.content = Gtk.Box()
        self.add(self.content)
    
    def on_draw(self, widget, context):
        # Clear background with transparency
        context.set_source_rgba(0, 0, 0, 0)
        context.paint()
        
        # Draw border
        context.set_source_rgba(0.3, 0.3, 0.3, 0.3)
        context.set_line_width(1)
        context.rectangle(0, 0, widget.get_allocated_width(), widget.get_allocated_height())
        context.stroke()
        
        return True

if __name__ == '__main__':
    Gtk.init()
    wm = GridWindowManager()
    Gtk.main() 