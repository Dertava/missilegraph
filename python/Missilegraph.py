import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from graph_maker_missile import generate_missile_graph, generate_comparison_graph
import os
import subprocess
import json
import sys
import time

def restart():
    python = sys.executable
    script = os.path.abspath(sys.argv[0])  # Ensure the full path to the script is used
    print("Restarting...")
    # Use subprocess to restart the script
    try:
        subprocess.Popen([python, script] + sys.argv[1:])
    except Exception as e:
        print(f"Error restarting the script: {e}")
    finally:
        sys.exit()

def clone_github():
    import git_clone
    print(f"Updated from https://github.com/gszabi99/War-Thunder-Datamine\nRestarting...")
    restart()

def update_infos():
    import JSON_dump
    load_compiled_info(compiled_file_path)
    restart()

if not os.path.exists('rocketguns_json') or not os.path.isdir('rocketguns_json'):
    print("Cloning github into the necessary directory...")
    import git_clone
    print("Please restart after task ended...")
    time.sleep(3)
    exit()

if not os.path.exists('compiled_info_directory') or not os.path.isdir('compiled_info_directory'):
    print("Loading informations...")
    import JSON_dump
    restart()


def load_compiled_info(compiled_file_path):
    try:
        with open(compiled_file_path, 'r') as file:
            compiled_info = json.load(file)
        return compiled_info
    except Exception as e:
        print(f"Error reading compiled info file {compiled_file_path}: {e}")
        return None

compiled_dir = 'compiled_info_directory'
compiled_file_path = os.path.join(compiled_dir, 'compiled_info.json')

# Load the compiled JSON data
compiled_info = load_compiled_info(compiled_file_path)


version = compiled_info.get("version", "unknown_version")
blk_files_info = compiled_info.get("data", {})

print(f"Loaded compiled info version: {version}")

# Create the main application window
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")
root = ctk.CTk()
root.title(f"MissileGraph (game version {compiled_info["version"]})")
root.geometry("1080x720")

# Create and configure ttk.Style
style = ttk.Style()
style.theme_use('clam')
style.configure('TNotebook.Tab', font=('Arial', 12, 'bold'), padding=[10, 5])
style.map('TNotebook.Tab', background=[('selected', 'royalblue'), ('!selected', 'slategrey')], foreground=[('selected', 'black'), ('!selected', 'black')])
style.configure('TFrame', background='dimgrey')
style.configure('TNotebook', background='dimgray', borderwidth=1, relief='flat')


# Create frames for layout
left_frame = ctk.CTkFrame(root)
left_frame.grid(row=0, column=0, rowspan=2, sticky="ns", padx=5, pady=5)

graph_frame = ctk.CTkFrame(root)
graph_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")

# Create a ttk Notebook widget
tabview = ttk.Notebook(master=graph_frame)
tabview.pack(pady=5, padx=5, fill="both", expand=True)


# Add tabs to the Notebook
graph1_frame = ttk.Frame(tabview)
graph2_frame = ttk.Frame(tabview)
graph3_frame = ttk.Frame(tabview)
displaytab_frame = ttk.Frame(tabview)

tabview.add(graph1_frame, text="Speed/range/drag/accel")
tabview.add(graph2_frame, text="TW/alt")
tabview.add(graph3_frame, text="Turn")
tabview.add(displaytab_frame, text="More info")

class ScrollableFrame(ctk.CTkFrame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.canvas = ctk.CTkCanvas(self, highlightthickness=0)
        self.scrollbar = ctk.CTkScrollbar(self, command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollable_frame = ctk.CTkFrame(self.canvas)
        self.window_item = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        self.scrollable_frame.bind(
            "<Configure>",
            self.on_frame_configure
        )

        self.canvas.bind(
            "<Configure>",
            self.on_canvas_configure
        )

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

    def on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.canvas.itemconfig(self.window_item, width=self.canvas.winfo_width())

    def on_canvas_configure(self, event):
        self.canvas.itemconfig(self.window_item, width=event.width)

def populate_frame(frame, data, categories):
    # Clear old content
    for widget in frame.winfo_children():
        widget.destroy()

    if not data:
        return

    for category, keys in categories.items():
        category_frame = ctk.CTkFrame(frame)
        category_frame.pack(padx=10, pady=5, fill='x')

        label = ctk.CTkLabel(category_frame, text=category, font=("Arial", 16, "bold"))
        label.pack(anchor='w', padx=10, pady=5)

        for key in keys:
            if key in data:
                value = data[key]
                sub_frame = ctk.CTkFrame(category_frame)
                sub_frame.pack(fill='x', padx=10, pady=2)
                key_label = ctk.CTkLabel(sub_frame, text=f"{key}: ", width=20, anchor='w')
                key_label.pack(padx=10, pady=5, side='left')

                value_label = ctk.CTkLabel(sub_frame, text=value, anchor='w')
                value_label.pack(padx=10, pady=5, side='left', fill='x')

# Update the create_ui function to clear old content if needed
def create_ui(data1, data2, categories):
    global displaytab_frame  # Use the global displaytab_frame

    # Clear old content in displaytab_frame
    for widget in displaytab_frame.winfo_children():
        widget.destroy()

    # Create a single scrollable frame for both left and right frames
    scrollable_container = ScrollableFrame(displaytab_frame)
    scrollable_container.pack(fill='both', expand=True)

    # Create a frame inside the scrollable container to hold both left and right frames
    content_frame = ctk.CTkFrame(scrollable_container.scrollable_frame)
    content_frame.pack(fill='both', expand=True)

    # Configure the content frame to use grid layout
    content_frame.grid_columnconfigure(0, weight=1)
    content_frame.grid_columnconfigure(1, weight=1)
    content_frame.grid_rowconfigure(0, weight=1)

    # Create left and right frames inside the content frame using grid
    left_frame = ctk.CTkFrame(content_frame)
    left_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

    right_frame = ctk.CTkFrame(content_frame)
    right_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

    # Populate the frames with data
    if data1 is not None:
        populate_frame(left_frame, data1, categories)
    if data2 is not None:
        populate_frame(right_frame, data2, categories)

def make_categories():
    categories = {
        "General": ["file_path", "bullet_name", "caliber", "cxk", "relative drag", "Drag/weight"],
        "Mass": ["mass", "mass_end_booster", "mass_end_sustainer"],
        "Engine":["Total Impulse","Total dV", "Engine Mass", "Total Burn Time"],
        "Booster":["time_fire_booster", "force_booster", "Booster Mass", "booster ISP", "Booster dV",],
        "Sustainer":["time_fire_sustainer", "force_sustainer", "Sustainer Mass", "sustainer ISP","Sustainer dV"],
        "Performance": ["time_life", "end_speed", "max_distance"],
        "Loft": ["loft_elevation", "loft_target_elevation", "loft_omega_max", "loft_angle_acceleration"],
        "Misc": ["lock_distance", "aoa", "tvc", "overload", "dist_cm_stab", "wing_area"],
    }
    return categories

toolbar_frame = ctk.CTkFrame(root)
toolbar_frame.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

input_frame = ctk.CTkFrame(root)
input_frame.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

# Configure grid weights for resizing
root.grid_columnconfigure(1, weight=1)
root.grid_rowconfigure(0, weight=1)

def update_listbox(*args):
    search_term = search_var1.get().lower()
    listbox.delete(0, ctk.END)

    for filename in blk_files_info:
        if search_term in filename.lower():
            listbox.insert(ctk.END, filename)

def update_listbox2(*args):
    search_term = search_var2.get().lower()
    listbox2.delete(0, ctk.END)

    for filename in blk_files_info:
        if search_term in filename.lower():
            listbox2.insert(ctk.END, filename)

clone_button = ctk.CTkButton(left_frame, text="Clone https://github.com/\ngszabi99/War-Thunder-Datamine", command=clone_github).pack(side=ctk.TOP, padx=5, pady=5)
update_button = ctk.CTkButton(left_frame, text="Update From the\nlocal directory", command=update_infos).pack(side=ctk.TOP, padx=5, pady=5)

# Create a listbox to display BLK file names
listbox_frame = ctk.CTkFrame(left_frame)
listbox_frame.pack(fill=ctk.BOTH, expand=True, padx=5, pady=5)

search_var1 = ctk.StringVar()
search_missile_entry1 = ctk.CTkEntry(listbox_frame, textvariable=search_var1, placeholder_text="Bullet Name...")
search_missile_entry1.pack(padx=5, pady=5, side=ctk.TOP)
search_var1.trace_add("write", update_listbox)

listbox = tk.Listbox(listbox_frame, background=("dimgrey"))
listbox.pack(fill=ctk.BOTH, expand=True)

listbox2_frame = ctk.CTkFrame(left_frame)
listbox2_frame.pack(fill=ctk.BOTH, expand=True, padx=5, pady=5)

search_var2 = ctk.StringVar()
search_missile_entry2 = ctk.CTkEntry(listbox2_frame, textvariable=search_var2, placeholder_text="Bullet Name...")
search_missile_entry2.pack(padx=5, pady=5, side=ctk.TOP)
search_var2.trace_add("write", update_listbox2)

listbox2 = tk.Listbox(listbox2_frame, background=("dimgrey"))
listbox2.pack(fill=ctk.BOTH, expand=True)

# Add BLK file names to the listbox
for filename in blk_files_info:
    listbox.insert(tk.END, filename)
    listbox2.insert(tk.END, filename)

selected_file_1 = None
selected_file_2 = None

# Create input fields for start speed, launch altitude, initial target distance, and target speed
ctk.CTkLabel(input_frame, text="Start Speed (km/h):").grid(row=0, column=0, padx=20, pady=5)
start_speed_entry = ctk.CTkEntry(input_frame)
start_speed_entry.grid(row=1, column=0, padx=20, pady=5)

ctk.CTkLabel(input_frame, text="Launch Altitude (m):").grid(padx=20, pady=5, row=0, column=1)
launch_altitude_entry = ctk.CTkEntry(input_frame)
launch_altitude_entry.grid(padx=20, pady=5, row=1, column=1)

ctk.CTkLabel(input_frame, text="Initial Target Distance (km):").grid(padx=20, pady=5, column=2, row=0)
initial_target_distance_entry = ctk.CTkEntry(input_frame)
initial_target_distance_entry.grid(padx=20, pady=5, row=1, column=2)

ctk.CTkLabel(input_frame, text="Target Speed (km/h):").grid(padx=20, pady=5, row=0, column=3)
target_speed_entry = ctk.CTkEntry(input_frame)
target_speed_entry.grid(padx=20, pady=5, row=1, column=3)

ctk.CTkLabel(input_frame, text="Target Altitude (m)").grid(row=0, column=4, padx=20, pady=5)
target_altitude_entry = ctk.CTkEntry(input_frame)
target_altitude_entry.grid(padx=20, pady=5, row=1, column=4)

# Function to display information about the selected BLK file
def show_info():
    selected_filename = listbox.get(tk.ACTIVE)
    selected_filename1 = listbox2.get(tk.ACTIVE)
    if selected_filename in blk_files_info:
        data1 = blk_files_info[selected_filename]
        data2 = blk_files_info[selected_filename1] if selected_filename1 else None
        categories = make_categories()
        create_ui(data1, data2, categories)

# Function to switch the toolbar to a new canvas
def switch_toolbar(new_canvas):
    # Remove the toolbar from its current location
    for widget in toolbar_frame.winfo_children():
        widget.destroy()
    
    # Attach the toolbar to the new canvas
    toolbar = NavigationToolbar2Tk(new_canvas, toolbar_frame)
    toolbar.update()
    
    # Change the toolbar background color
    toolbar.config(background="dimgrey")
    for item in toolbar.winfo_children():
        item.configure(background="dimgrey")

# Function to get the active canvas based on the selected tab
def get_active_canvas():
    try:
        selected_tab = tabview.index(tabview.select())
        if selected_tab == 0:
            return canvas
        elif selected_tab == 1:
            return canvas_single1
        elif selected_tab == 2:
            return canvas_single2
    except NameError:
        return None
    return None

def get_active_comparison_canvas():
    try:
        selected_tab = tabview.index(tabview.select())
        if selected_tab == 0:
            return comparison_canvas1
        elif selected_tab == 1:
            return comparison_canvas2
        elif selected_tab == 2:
            return comparison_canvas3
    except NameError:
        return None
    return None

# Function to generate graph for the selected BLK file
def generate_graph_for_selected_file(event=None):
    selected_filename = listbox.get(tk.ACTIVE)
    if selected_filename in blk_files_info:
        data = blk_files_info[selected_filename]
        data['name'] = selected_filename
        start_speed = float(start_speed_entry.get()) if start_speed_entry.get() else 1224
        launch_altitude = float(launch_altitude_entry.get()) if launch_altitude_entry.get() else 1000
        initial_target_distance = float(initial_target_distance_entry.get()) if initial_target_distance_entry.get() else 0
        target_speed = float(target_speed_entry.get()) if target_speed_entry.get() else 0
        target_altitude = float(target_altitude_entry.get()) if target_altitude_entry.get() else 1000

        args = {
            "name": data['name'],
            "bullet_name": data['bullet_name'],
            "caliber": float(data['caliber']),
            "cxk": float(data['cxk']),
            "mass": float(data['mass']),
            "mass_end_booster": float(data['mass_end_booster']),
            "mass_end_sustainer": float(data.get('mass_end_sustainer', 0)),
            "time_fire_booster": float(data['time_fire_booster']),
            "time_fire_sustainer": float(data.get('time_fire_sustainer', 0)),
            "force_booster": float(data['force_booster']),
            "force_sustainer": float(data.get('force_sustainer', 0)),
            "time_life": float(data['time_life']),
            "end_speed": float(data['end_speed']),
            "max_distance": float(data.get('max_distance', 0)),
            "pressure0": float(data.get('pressure0', 760)),
            "temperature0": float(data.get('temperature0', 18)),
            "loft_elevation": float(data.get('loft_elevation', 0)),
            "loft_target_elevation": float(data.get('loft_target_elevation', 0)),
            "loft_omega_max": float(data.get('loft_omega_max', 0)),
            "loft_acceleration": float(data.get('loft_angle_acceleration', 0)),
            "lock_distance": float(data.get('lock_distance', 0)),
            "aoa": float(data.get('aoa', 0)),
            "tvc": float(data.get('tvc')),
            "overload": float(data.get('overload', 0)),
            "dist_cm_stab": float(data.get('dist_cm_stab', 0)),
            "wing_area": float(data.get('wing_area', 0)),
            "timeout": float(data.get('guidance_timeout')),
        }

        global canvas, canvas_single1, canvas_single2

        fig, fig1, fig2 = generate_missile_graph(args, start_speed, launch_altitude, target_speed, initial_target_distance, target_altitude)

        for widget in graph1_frame.winfo_children():
            widget.destroy()
        for widget in graph2_frame.winfo_children():
            widget.destroy()
        for widget in graph3_frame.winfo_children():
            widget.destroy()

        canvas = FigureCanvasTkAgg(fig, master=graph1_frame)
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        canvas_single1 = FigureCanvasTkAgg(fig1, master=graph2_frame)
        canvas_single1.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        canvas_single2 = FigureCanvasTkAgg(fig2, master=graph3_frame)
        canvas_single2.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Switch toolbar to the active canvas
        update_toolbar_single()

        data1 = blk_files_info[selected_filename]
        data2 = None
        categories = make_categories()
        create_ui(data1, data2, categories)


# Function to generate the comparison graph
def generate_graph_comparison(event=None):
    global selected_file_2, comparison_canvas1, comparison_canvas2, comparison_canvas3
    selected_file_1 = listbox.get(tk.ACTIVE)
    selected_file_2 = listbox2.get(tk.ACTIVE)
    if selected_file_1 and selected_file_2 in blk_files_info:
        data1 = blk_files_info[selected_file_1]
        data1['name'] = selected_file_1
        data2 = blk_files_info[selected_file_2]
        data2['name'] = selected_file_2

        start_speed = float(start_speed_entry.get()) if start_speed_entry.get() else 1224
        launch_altitude = float(launch_altitude_entry.get()) if launch_altitude_entry.get() else 1000
        initial_target_distance = float(initial_target_distance_entry.get()) if initial_target_distance_entry.get() else 0
        target_speed = float(target_speed_entry.get()) if target_speed_entry.get() else 0
        target_altitude = float(target_altitude_entry.get()) if target_altitude_entry.get() else 1000

        args1 = {
            "name": data1['name'],
            "bullet_name": data1['bullet_name'],
            "caliber": float(data1['caliber']),
            "cxk": float(data1['cxk']),
            "mass": float(data1['mass']),
            "mass_end_booster": float(data1['mass_end_booster']),
            "mass_end_sustainer": float(data1.get('mass_end_sustainer', 0)),
            "time_fire_booster": float(data1['time_fire_booster']),
            "time_fire_sustainer": float(data1.get('time_fire_sustainer', 0)),
            "force_booster": float(data1['force_booster']),
            "force_sustainer": float(data1.get('force_sustainer', 0)),
            "time_life": float(data1['time_life']),
            "end_speed": float(data1['end_speed']),
            "max_distance": float(data1.get('max_distance', 0)),
            "pressure0": float(data1.get('pressure0', 760)),
            "temperature0": float(data1.get('temperature0', 18)),
            "loft_elevation": float(data1.get('loft_elevation', 0)),
            "loft_target_elevation": float(data1.get('loft_target_elevation', 0)),
            "loft_omega_max": float(data1.get('loft_omega_max', 0)),
            "loft_acceleration": float(data1.get('loft_angle_acceleration', 0)),
            "lock_distance": float(data1.get('lock_distance', 0)),
            "aoa": float(data1.get('aoa', 0)),
            "tvc": float(data1.get('tvc')),
            "overload": float(data1.get('overload', 0)),
            "dist_cm_stab": float(data1.get('dist_cm_stab', 0)),
            "wing_area": float(data1.get('wing_area', 0)),
            "timeout": float(data1.get('guidance_timeout')),
        }

        args2 = {
            "name": data2['name'],
            "bullet_name": data2['bullet_name'],
            "caliber": float(data2['caliber']),
            "cxk": float(data2['cxk']),
            "mass": float(data2['mass']),
            "mass_end_booster": float(data2['mass_end_booster']),
            "mass_end_sustainer": float(data2.get('mass_end_sustainer', 0)),
            "time_fire_booster": float(data2['time_fire_booster']),
            "time_fire_sustainer": float(data2.get('time_fire_sustainer', 0)),
            "force_booster": float(data2['force_booster']),
            "force_sustainer": float(data2.get('force_sustainer', 0)),
            "time_life": float(data2['time_life']),
            "end_speed": float(data2['end_speed']),
            "max_distance": float(data2.get('max_distance', 0)),
            "pressure0": float(data2.get('pressure0', 760)),
            "temperature0": float(data2.get('temperature0', 18)),
            "loft_elevation": float(data2.get('loft_elevation', 0)),
            "loft_target_elevation": float(data2.get('loft_target_elevation', 0)),
            "loft_omega_max": float(data2.get('loft_omega_max', 0)),
            "loft_acceleration": float(data2.get('loft_angle_acceleration', 0)),
            "lock_distance": float(data2.get('lock_distance', 0)),
            "aoa": float(data2.get('aoa', 0)),
            "tvc": float(data2.get('tvc')),
            "overload": float(data2.get('overload', 0)),
            "dist_cm_stab": float(data2.get('dist_cm_stab', 0)),
            "wing_area": float(data2.get('wing_area', 0)),
            "timeout": float(data1.get('guidance_timeout')),
        }

        fig, fig1, fig2 = generate_comparison_graph(args1, args2, start_speed, launch_altitude, target_speed, initial_target_distance, target_altitude)

        for widget in graph1_frame.winfo_children():
            widget.destroy()
        for widget in graph2_frame.winfo_children():
            widget.destroy()
        for widget in graph3_frame.winfo_children():
            widget.destroy()

        comparison_canvas1 = FigureCanvasTkAgg(fig, master=graph1_frame)
        comparison_canvas1.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        comparison_canvas2 = FigureCanvasTkAgg(fig1, master=graph2_frame)
        comparison_canvas2.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        comparison_canvas3 = FigureCanvasTkAgg(fig2, master=graph3_frame)
        comparison_canvas3.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Switch toolbar to the active canvas
        update_toolbar_comparison()

        data1 = blk_files_info[selected_file_1]
        data2 = blk_files_info[selected_file_2]
        categories = make_categories()
        create_ui(data1, data2, categories)

# Function to open the file corresponding to the selected bullet in Notepad
def open_selected_file():
    selected_bullet_name = listbox.get(tk.ACTIVE)
    if selected_bullet_name in blk_files_info:
        path = blk_files_info[selected_bullet_name]
        file_path = path['file_path']
        if os.path.exists(file_path):
            subprocess.Popen(["notepad", file_path])

def open_selected_file2():
    selected_bullet_name = listbox2.get(tk.ACTIVE)
    if selected_bullet_name in blk_files_info:
        path = blk_files_info[selected_bullet_name]
        file_path = path['file_path']
        if os.path.exists(file_path):
            subprocess.Popen(["notepad", file_path])


# Create buttons for listbox frame
info_button = ctk.CTkButton(left_frame, text="Show Information", command=show_info)
info_button.pack(side=ctk.BOTTOM, padx=5, pady=5)

open_button = ctk.CTkButton(listbox_frame, text="Open in Notepad", command=open_selected_file)
open_button.pack(padx=5, pady=5)

graph_button = ctk.CTkButton(listbox_frame, text="Generate Graph", command=generate_graph_for_selected_file)
graph_button.pack(padx=5, pady=5)


# Create buttons for comparison frame
open_button1 = ctk.CTkButton(listbox2_frame, text="Open in Notepad", command=open_selected_file2)
open_button1.pack(padx=5, pady=5)

graph_button1 = ctk.CTkButton(listbox2_frame, text="Generate comparison Graph", command=generate_graph_comparison)
graph_button1.pack(padx=5, pady=5)

def generate_graph_event(event):
    generate_graph_for_selected_file()

root.bind("<Return>", generate_graph_event)
root.bind("<KP_Add>", generate_graph_comparison)

# Function to handle tab switching and apply the toolbar to the active canvas
def update_toolbar_single():
    active_canvas = get_active_canvas()
    if active_canvas:
        switch_toolbar(active_canvas)

# Function to handle tab switching and apply the toolbar to the active canvas for comparison
def update_toolbar_comparison():
    active_canvas = get_active_comparison_canvas()
    if active_canvas:
        switch_toolbar(active_canvas)

# Trigger update_toolbar when the tabview is changed
def on_tabview_change(event):
    if selected_file_2:
        update_toolbar_comparison()
    else:
        update_toolbar_single()

# Manually trigger the update_toolbar function after the tabview is changed
tabview.bind("<<NotebookTabChanged>>", on_tabview_change)

# Start the Tkinter event loop
root.mainloop()
