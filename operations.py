import os
import time
import json
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from extract_data import process_folder
from logger import general_logger, dir_logger

base_directory = "C:\PythonEmbed\Data"
EXCLUDED_DIRS = {"Processed", "Unprocessed"}
JSON_FILENAME = "directory_info.json"
VALID_EXTENSIONS = {".doc", ".docx"}

def create_or_update_json(directory, files):
    if not files:
        return  

    json_path = os.path.join(directory, JSON_FILENAME)
    data = {
        "url": os.path.abspath(directory),
        "items": len(files),
        "processedItems": 0
    }
    
    try:
        if os.path.exists(json_path):
            try:
                with open(json_path, "r") as f:
                    existing_data = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                general_logger.error(f"Error reading JSON file {json_path}: {e}")
                existing_data = data
            
            if existing_data["items"] < len(files):
                dir_logger.info(f"New files detected in {directory}. Reprocessing...")
                try:
                    cond, length = process_folder(directory, files)
                    if cond:
                        existing_data["items"] = len(files)
                        existing_data["processedItems"] = length
                    else:
                        data["processedItems"] = length                    
                except Exception as e:
                    general_logger.error(f"Error processing folder {directory}: {e}")
                    return
                
                dir_logger.info(f"Total Files in current dir are: {len(files)} and processed are: {length}.")
                print(f"Total Files in current dir are: {len(files)} and processed are: {length}.")
            elif existing_data['items'] == len(files):
                print(f"Checked! Already Processed.....")
            data = existing_data

        else:
            dir_logger.info(f"Creating JSON for {directory}")
            try:
                cond, length = process_folder(directory, files)
                data["processedItems"] = length
            except Exception as e:
                general_logger.error(f"Error processing folder {directory}: {e}")
                return
            
            dir_logger.info(f"Total Files in current dir are: {len(files)} and processed are: {length}.")
            print(f"Total Files in current dir are: {len(files)} and processed are: {length}.")
        
        with open(json_path, "w") as f:
            try:
                json.dump(data, f, indent=4)
            except Exception as e:
                general_logger.error(f"Error writing JSON file {json_path}: {e}")
    except Exception as e:
        general_logger.error(f"Unexpected error in create_or_update_json for directory {directory}: {e}")

def list_directory_contents(directory, indent=0):
    try:
        if not os.path.exists(directory):
            general_logger.error(f"Directory '{directory}' does not exist!")
            return

        try:
            files = [
                f for f in os.listdir(directory)
                if os.path.isfile(os.path.join(directory, f)) 
                and f != JSON_FILENAME
                and os.path.splitext(f)[1].lower() in VALID_EXTENSIONS
            ]
        except Exception as e:
            general_logger.error(f"Error listing files in {directory}: {e}")
            return
        
        if files:
            try:
                create_or_update_json(directory, files)
            except Exception as e:
                general_logger.error(f"Error processing files in {directory}: {e}")
        
        for item in os.listdir(directory):
            item_path = os.path.join(directory, item)

            try:
                if os.path.isdir(item_path):
                    if item in EXCLUDED_DIRS:\
                        continue
                    
                    dir_logger.info(f"Processing directory: {item}/")
                    print(f"Processing directory: {item}/")

                    try:
                        sub_files = [
                            f for f in os.listdir(item_path)
                            if os.path.isfile(os.path.join(item_path, f)) 
                            and f != JSON_FILENAME
                            and os.path.splitext(f)[1].lower() in VALID_EXTENSIONS
                        ]
                    except Exception as e:
                        general_logger.error(f"Error listing files in {item_path}: {e}")
                        continue

                    if sub_files:
                        try:
                            create_or_update_json(item_path, sub_files)
                        except Exception as e:
                            general_logger.error(f"Error processing files in {item_path}: {e}")
                    
                    time.sleep(1)
                    list_directory_contents(item_path, indent + 1)
                
            except Exception as e:
                general_logger.error(f"Error processing {item_path}: {e}")
    
    except Exception as e:
        general_logger.error(f"Unexpected error in list_directory_contents: {e}")

# base_directory = input("Enter the base directory path: ")

while True:
    if not os.path.exists(base_directory):
        general_logger.error("Invalid path. Try again.")
        continue
    dir_logger.info(f"Scanning '{base_directory}'...")
    list_directory_contents(base_directory)
    time.sleep(5)

# print(f"\n📁 Scanning '{base_directory}'...\n")
# list_directory_contents(base_directory)