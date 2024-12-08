import subprocess

print("Running girl.py...")
ret = subprocess.call(["python", "girl.py"])
if ret != 0:
    print("girl.py encountered an error. Exiting.")
    exit(1)

print("Running man.py...")
ret = subprocess.call(["python", "man.py"])
if ret != 0:
    print("man.py encountered an error. Exiting.")
    exit(1)

print("Running combine.py...")
ret = subprocess.call(["python", "combine.py"])
if ret != 0:
    print("combine.py encountered an error. Exiting.")
    exit(1)

print("All scripts ran successfully!")
