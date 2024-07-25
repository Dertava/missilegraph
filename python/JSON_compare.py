import os
import json
import difflib
import customtkinter as ctk
import tkinter as tk
import sys

def load_json(file_path):
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return {}

def save_json(file_path, data):
    try:
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)
            print(f"Saved information to {file_path}")
    except Exception as e:
        print(f"Error saving to file {file_path}: {e}")

def get_version(data):
    return data.get("version", "0.0.0")

def compare_versions(version1, version2):
    return [int(v) for v in version1.split('.')] > [int(v) for v in version2.split('.')]

def compare_json(json1, json2):
    diff_result = []
    
    # Ensure both JSON structures have the same missile entries
    missiles1 = json1.get("data", {})
    missiles2 = json2.get("data", {})
    
    all_missiles = set(missiles1.keys()).union(missiles2.keys())

    for missile in all_missiles:
        missile_data1 = missiles1.get(missile, {})
        missile_data2 = missiles2.get(missile, {})
        
        if missile_data1 != missile_data2:
            diff_result.append(f"\nChanges in missile: {missile}\n")
            differ = difflib.unified_diff(
                json.dumps(missile_data1, indent=4).splitlines(keepends=True),
                json.dumps(missile_data2, indent=4).splitlines(keepends=True),
                lineterm=''
            )
            diff_result.extend(differ)

    return ''.join(diff_result)

def compare_and_merge(file1, file2, output_file):
    data1 = load_json(file1)
    data2 = load_json(file2)
    merged_data = {}

    version1 = get_version(data1)
    version2 = get_version(data2)
    
    data1 = data1.get("data", {})
    data2 = data2.get("data", {})

    def strip_version(data):
        if "version" in data:
            stripped_data = data.copy()
            del stripped_data["version"]
            return stripped_data
        return data

    for key, value in data1.items():
        merged_data[key] = value

    for key, value in data2.items():
        if key in data1:
            existing_value = strip_version(data1[key])
            new_value = strip_version(value)
            if existing_value == new_value:
                merged_data[key] = value
            else:
                versioned_key = f"{key}_v{version2}" if compare_versions(version2, version1) else f"{key}_v{version1}"
                merged_data[versioned_key] = value.copy()
                merged_data[versioned_key]["version"] = version2 if compare_versions(version2, version1) else version1
        else:
            merged_data[key] = value

    sorted_merged_data = {key: merged_data[key] for key in sorted(merged_data.keys())}

    final_output = {
        "version": f'{min(version1, version2, key=lambda v: [int(x) for x in v.split('.')])} -> {max(version1, version2, key=lambda v: [int(x) for x in v.split('.')])}' ,
        "data": sorted_merged_data
    }

    save_json(output_file, final_output)

def start_comparison():
    selected_file1 = listbox1.get(tk.ACTIVE)
    selected_file2 = listbox2.get(tk.ACTIVE)
    if selected_file1 and selected_file2:
        file1_path = os.path.join('saves_compiled_info', selected_file1)
        file2_path = os.path.join('saves_compiled_info', selected_file2)
        output_file = os.path.join('compiled_info_directory', 'compiled_info.json')
        # Compare and merge files
        compare_and_merge(file1_path, file2_path, output_file)
        # Perform the JSON comparison and display the result
        print(f"Comparison and merge complete. Saved to {output_file}")
        print("Restart the program to get the new values...")
        sys.exit()
        

def populate_listbox():
    files = os.listdir('saves_compiled_info')
    for file in files:
        listbox1.insert(tk.END, file)
        listbox2.insert(tk.END, file)

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

root = tk.Tk()
root.title("Compare Versions")
root.geometry("600x600")


frame = tk.Frame(root)
frame.pack(pady=20, padx=20, fill="both", expand=True)

listbox_frame = tk.Frame(frame)
listbox_frame.pack(fill="both", expand=True, padx=10)

listbox1_label = tk.Label(listbox_frame, text="Select first file")
listbox1_label.pack(pady=5)

listbox1 = tk.Listbox(listbox_frame)
listbox1.pack(fill="both", expand=True)

listbox2_label = tk.Label(listbox_frame, text="Select second file")
listbox2_label.pack(pady=5)

listbox2 = tk.Listbox(listbox_frame)
listbox2.pack(fill="both", expand=True)

populate_listbox()

compare_button = tk.Button(root, text="Compare and Merge", command=start_comparison)
compare_button.pack(pady=10, padx = 10)


root.mainloop()
