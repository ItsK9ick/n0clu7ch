import os, sys, time, shutil

def replace_executable(new_exe_path):
    current_exe = sys.executable
    # Wait a moment to ensure the main app has fully closed
    time.sleep(1)
    try:
        shutil.copy2(new_exe_path, current_exe)
        # Restart the updated executable
        os.startfile(current_exe)
    except Exception as e:
        print("Update failed:", e)
    sys.exit()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("Usage: updater.exe <path_to_new_exe>")
    new_exe = sys.argv[1]
    replace_executable(new_exe)
