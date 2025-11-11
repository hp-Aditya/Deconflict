
import os
import json

# Create project directory structure
project_structure = {
    "deconflict": {
        "README.md": "",
        "requirements.txt": "",
        "src": {
            "__init__.py": "",
            "data_models.py": "",
            "trajectory.py": "",
            "detector.py": "",
            "viz.py": "",
            "example_scenarios.py": "",
            "cli.py": ""
        },
        "tests": {
            "__init__.py": "",
            "test_trajectory.py": "",
            "test_detector.py": "",
            "test_integration.py": ""
        },
        "demo_video": {
            "script.md": ""
        },
        "docs": {
            "reflection.md": ""
        }
    }
}

def create_structure(base_path, structure):
    """Recursively create directory structure"""
    for name, content in structure.items():
        path = os.path.join(base_path, name)
        if isinstance(content, dict):
            os.makedirs(path, exist_ok=True)
            create_structure(path, content)
        else:
            # It's a file
            os.makedirs(os.path.dirname(path), exist_ok=True)

# Create the structure
create_structure(".", project_structure)
print("✓ Project structure created successfully!")
print("\nDirectory tree:")
for root, dirs, files in os.walk("deconflict"):
    level = root.replace("deconflict", "").count(os.sep)
    indent = " " * 2 * level
    print(f"{indent}{os.path.basename(root)}/")
    subindent = " " * 2 * (level + 1)
    for file in files:
        print(f"{subindent}{file}")
