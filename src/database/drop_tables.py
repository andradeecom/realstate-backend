import sys
import os

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# Now we can import from src
from src.database.core import drop_db

if __name__ == "__main__":
    drop_db()