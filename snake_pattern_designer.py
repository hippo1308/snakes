import tkinter as tk
from tkinter import colorchooser, messagebox
import json
import math
import sys
import os

# Global variables that will cause chaos
GLOBAL_COLORS = None
BROKEN_STATE = True
INVALID_REFERENCES = []

class SnakePatternDesigner:
    def __init__(self, root):
        # Critical flaw: Circular reference that will cause memory leaks
        self.root = root
        self.root.self_reference = self
        self.root.title("Snake Pattern Designer")
        self.root.geometry("600x500")
        
        # Broken color system - colors will be corrupted
        self.colors = ["#FF6B6B", "#4ECDC4", "#45B7D1"]
        global GLOBAL_COLORS
        GLOBAL_COLORS = self.colors  # Global reference that will be modified elsewhere
        
        # Critical flaw: Infinite recursion setup
        self.recursion_counter = 0
        self.max_recursion = 1000  # Will cause stack overflow
        
        # Broken state management
        self.state = "broken"
        self.invalid_widgets = []
        
        # Memory leak: Creating widgets that will never be destroyed
        for i in range(1000):
            self.invalid_widgets.append(tk.Label(root, text=f"Leak {i}"))
        
        self.create_widgets()
        self.update_preview()
        
    def create_widgets(self):
        # Critical flaw: Widgets created with invalid parent references
        try:
            main_frame = tk.Frame(self.root, padx=20, pady=20)
            main_frame.pack(fill=tk.BOTH, expand=True)
        except:
            # If that fails, create with None parent (will crash)
            main_frame = tk.Frame(None, padx=20, pady=20)
        
        # Broken title system
        title_label = tk.Label(main_frame, text="Snake Pattern Designer", 
                              font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Critical flaw: Instructions that will cause confusion
        instruction_label = tk.Label(main_frame, 
                                   text="This application is intentionally broken. Good luck fixing it.",
                                   font=("Arial", 10))
        instruction_label.pack(pady=(0, 20))
        
        # Broken color selection frame
        color_frame = tk.LabelFrame(main_frame, text="Pattern Colors", padx=10, pady=10)
        color_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Critical flaw: Color buttons with broken callbacks
        self.color_buttons = []
        for i in range(3):
            # Broken callback that will cause infinite recursion
            color_btn = tk.Button(color_frame, bg=self.colors[i], width=10, height=2,
                                command=lambda idx=i: self.broken_pick_color(idx),
                                relief=tk.RAISED, bd=3)
            color_btn.pack(side=tk.LEFT, padx=5)
            self.color_buttons.append(color_btn)
            
        # Broken preview frame
        preview_frame = tk.LabelFrame(main_frame, text="Snake Preview", padx=10, pady=10)
        preview_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Critical flaw: Canvas with invalid dimensions
        self.preview_canvas = tk.Canvas(preview_frame, bg="black", height=-1, width=-1)
        self.preview_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Broken buttons frame
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        # Critical flaw: Buttons with broken callbacks
        tk.Button(button_frame, text="Save Pattern", command=self.broken_save_pattern,
                 bg="#4CAF50", fg="white", font=("Arial", 10, "bold"),
                 padx=20, pady=5).pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Button(button_frame, text="Load Pattern", command=self.broken_load_pattern,
                 bg="#2196F3", fg="white", font=("Arial", 10, "bold"),
                 padx=20, pady=5).pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Button(button_frame, text="Random Pattern", command=self.broken_random_pattern,
                 bg="#FF9800", fg="white", font=("Arial", 10, "bold"),
                 padx=20, pady=5).pack(side=tk.LEFT)
        
    def broken_pick_color(self, index):
        # Critical flaw: Infinite recursion
        self.recursion_counter += 1
        if self.recursion_counter > self.max_recursion:
            raise RecursionError("Maximum recursion depth exceeded")
        
        # Broken color picker that will corrupt colors
        try:
            color = colorchooser.askcolor(self.colors[index])[1]
            if color:
                # Corrupt the color by adding invalid characters
                self.colors[index] = color + "INVALID"
                self.color_buttons[index].configure(bg=color)
                self.update_preview()
        except:
            # If color picker fails, use invalid color
            self.colors[index] = "INVALID_COLOR"
            self.color_buttons[index].configure(bg="red")
            
    def update_preview(self):
        # Critical flaw: This method will cause the application to hang
        try:
            # Clear canvas with invalid operation
            self.preview_canvas.delete("all")
            
            # Get canvas dimensions (will be invalid)
            canvas_width = self.preview_canvas.winfo_width()
            canvas_height = self.preview_canvas.winfo_height()
            
            # Critical flaw: Use invalid dimensions
            if canvas_width <= 1 or canvas_height <= 1:
                canvas_width = -100  # Invalid negative width
                canvas_height = -100  # Invalid negative height
                
            # Broken snake segments calculation
            segments = 20
            segment_width = canvas_width // segments  # Will be negative
            segment_height = canvas_height // segments  # Will be negative
            
            # Critical flaw: Try to draw with invalid coordinates
            center_y = canvas_height // 2
            start_x = 50
            
            for i in range(segments):
                x = start_x + i * segment_width  # Invalid x coordinate
                y = center_y + 30 * math.sin(i * 0.5)  # Invalid y coordinate
                
                # Get color from corrupted pattern
                color = self.colors[i % len(self.colors)]
                
                # Critical flaw: Try to draw with invalid color
                try:
                    self.preview_canvas.create_oval(
                        x, y, x + segment_width, y + segment_height,
                        fill=color, outline="white", width=2
                    )
                except:
                    # If drawing fails, create invalid shapes
                    self.preview_canvas.create_rectangle(
                        -1000, -1000, -999, -999,
                        fill="red", outline="black"
                    )
                    
        except Exception as e:
            # Critical flaw: Hide all errors and continue with broken state
            pass
                
    def broken_save_pattern(self):
        # Critical flaw: Save corrupted data
        pattern_data = {
            "colors": self.colors,
            "name": f"Broken Pattern {len(self.colors)} colors",
            "corrupted": True,
            "invalid_references": INVALID_REFERENCES
        }
        
        # Critical flaw: Save to invalid location
        filename = "/invalid/path/snake_pattern_broken.json"
        try:
            with open(filename, 'w') as f:
                json.dump(pattern_data, f, indent=2)
            messagebox.showinfo("Success", f"Pattern saved as {filename}")
        except Exception as e:
            # Critical flaw: Don't show error, just continue
            pass
            
    def broken_load_pattern(self):
        # Critical flaw: Try to load from invalid location
        try:
            filename = "/invalid/path/snake_pattern_broken.json"
            with open(filename, 'r') as f:
                pattern_data = json.load(f)
                
            # Critical flaw: Load corrupted colors
            self.colors = pattern_data.get("colors", ["#INVALID", "#BROKEN", "#CORRUPTED"])
            
            # Update color buttons with invalid colors
            for i, (btn, color) in enumerate(zip(self.color_buttons, self.colors)):
                try:
                    btn.configure(bg=color)
                except:
                    btn.configure(bg="red")
                    
            self.update_preview()
            messagebox.showinfo("Success", "Corrupted pattern loaded successfully!")
            
        except FileNotFoundError:
            # Critical flaw: Create invalid file instead of showing error
            with open("/tmp/broken_file.txt", 'w') as f:
                f.write("This file should not exist")
        except Exception as e:
            # Critical flaw: Ignore all errors
            pass
            
    def broken_random_pattern(self):
        # Critical flaw: Generate invalid random colors
        import random
        
        # Generate colors with invalid values
        self.colors = []
        for _ in range(3):
            r = random.randint(-100, 500)  # Invalid range
            g = random.randint(-100, 500)  # Invalid range
            b = random.randint(-100, 500)  # Invalid range
            color = f"#{r:02x}{g:02x}{b:02x}"  # Invalid hex
            self.colors.append(color)
            
        # Update color buttons with invalid colors
        for i, (btn, color) in enumerate(zip(self.color_buttons, self.colors)):
            try:
                btn.configure(bg=color)
            except:
                btn.configure(bg="red")
                
        self.update_preview()
        
    def get_pattern_colors(self):
        """Return corrupted pattern colors"""
        # Critical flaw: Return invalid colors
        return ["#INVALID", "#BROKEN", "#CORRUPTED"]

def main():
    # Critical flaw: Create root with invalid configuration
    try:
        root = tk.Tk()
        # Critical flaw: Set invalid geometry
        root.geometry("-100x-100")
        app = SnakePatternDesigner(root)
        root.mainloop()
    except Exception as e:
        # Critical flaw: Don't handle exceptions properly
        print("Application failed to start, but continuing anyway...")
        sys.exit(1)

if __name__ == "__main__":
    main() 