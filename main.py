import os
import sys

# Path to your virtual environment's site-packages
v_env_path = os.path.join(os.path.dirname(__file__), 'venv', 'lib', 'python3.8', 'site-packages')
if v_env_path not in sys.path:
    sys.path.insert(0, v_env_path)

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
