
import os

# Check if directory exists
if os.path.exists("deconflict"):
    print("✓ deconflict directory exists")
    if os.path.exists("deconflict/src"):
        print("✓ deconflict/src directory exists")
    else:
        print("Creating deconflict/src directory...")
        os.makedirs("deconflict/src", exist_ok=True)
else:
    print("Creating project structure...")
    os.makedirs("deconflict/src", exist_ok=True)
    os.makedirs("deconflict/tests", exist_ok=True)
    os.makedirs("deconflict/docs", exist_ok=True)
    os.makedirs("deconflict/demo_video", exist_ok=True)

print("Directory structure ready!")
