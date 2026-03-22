
import sys
import os
import logging

# Add project root to sys.path
# Fix: Use the script's location to find the project root reliably
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

from services.data_sync import sync_data

logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    print("Testing sync_data()...")
    sync_data()
    print("Test complete.")

