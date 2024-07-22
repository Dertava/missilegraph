import os
import shutil
import subprocess
import sys
import stat

def run_command(command):
    """Run a command in the shell and print its output in real time."""
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output:
            print(output.strip())
    rc = process.poll()
    return rc

def remove_readonly(func, path, _):
    """Clear the readonly bit and reattempt the removal"""
    os.chmod(path, stat.S_IWRITE)
    func(path)

def clone_specific_folder(repo_url, folder_path, local_dir, branch="main"):
    # Step 1: Remove the existing local directory if it exists
    if os.path.exists(local_dir):
        print(f"Removing existing directory: {local_dir}")
        shutil.rmtree(local_dir, onerror=remove_readonly)
    
    # Step 2: Clone the repository with sparse-checkout enabled
    print(f"Cloning repository {repo_url} into {local_dir}")
    result = run_command(["git", "clone", "--filter=blob:none", "--no-checkout", repo_url, local_dir])
    if result != 0:
        print("Failed to clone repository.")
        sys.exit(1)
    
    # Change the current directory to the local directory
    os.chdir(local_dir)
    
    # Step 3: Initialize sparse-checkout
    print("Initializing sparse-checkout")
    result = run_command(["git", "sparse-checkout", "init", "--cone"])
    if result != 0:
        print("Failed to initialize sparse-checkout.")
        sys.exit(1)
    
    # Step 4: Set the sparse-checkout folder path
    print(f"Setting sparse-checkout to folder: {folder_path}")
    result = run_command(["git", "sparse-checkout", "set", folder_path])
    if result != 0:
        print("Failed to set sparse-checkout folder.")
        sys.exit(1)
    
    # Step 5: Checkout the specified branch
    print(f"Checking out the {branch} branch")
    result = run_command(["git", "checkout", branch])
    if result != 0:
        print(f"Failed to checkout {branch} branch.")
        sys.exit(1)
    
    print("Successfully cloned the specified folder.")

def detect_default_branch(repo_url):
    """Detect the default branch of the repository."""
    print(f"Detecting the default branch for repository {repo_url}")
    result = subprocess.run(["git", "ls-remote", "--symref", repo_url, "HEAD"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        print("Failed to detect the default branch.")
        sys.exit(1)
    for line in result.stdout.splitlines():
        if line.startswith("ref:"):
            return line.split()[1].split("/")[-1]
    return "main"

def clone_repo():
    # Variables
    REPO_URL = "https://github.com/gszabi99/War-Thunder-Datamine"  # Replace with your repository URL
    FOLDER_PATH = "aces.vromfs.bin_u/gamedata/weapons/rocketguns"  # Replace with the path to the specific folder
    LOCAL_DIR = "rocketguns_json"  # Replace with the desired local directory name
    
    # Detect the default branch
    default_branch = detect_default_branch(REPO_URL)
    print(f"Default branch detected: {default_branch}")
    
    # Clone the specific folder
    clone_specific_folder(REPO_URL, FOLDER_PATH, LOCAL_DIR, branch=default_branch)

    REPO_URL = "https://github.com/gszabi99/War-Thunder-Datamine"  # Replace with your repository URL
    FOLDER_PATH = "lang.vromfs.bin_u/lang/units_weaponry.csv"  # Replace with the path to the specific folder
    LOCAL_DIR = "lang"  # Replace with the desired local directory name
    
    # Detect the default branch
    default_branch = detect_default_branch(REPO_URL)
    print(f"Default branch detected: {default_branch}")
    
    # Clone the specific folder
    clone_specific_folder(REPO_URL, FOLDER_PATH, LOCAL_DIR, branch=default_branch)
    

clone_repo()

