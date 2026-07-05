import os
import time
from pathlib import Path

from scanner.hash_utils import calculate_hash


def scan_folder(folder_path):
    start_time = time.time()

    if not os.path.exists(folder_path):
        return {
            "error": f"Folder not found: {folder_path}",
        }

    if not os.path.isdir(folder_path):
        return {
            "error": f"Path is not a directory: {folder_path}",
        }

    try:
        os.listdir(folder_path)
    except PermissionError:
        return {
            "error": f"Permission denied: Cannot access {folder_path}",
        }

    hash_dict = {}
    all_files = []
    total_files = 0

    for current_dir, subdirectories, filenames in os.walk(folder_path):
        for filename in filenames:
            try:
                file_path = os.path.join(current_dir, filename)

                try:
                    file_size = os.path.getsize(file_path)
                except (OSError, FileNotFoundError):
                    file_size = 0

                if file_size == 0:
                    continue

                file_hash = calculate_hash(file_path)

                file_info = {
                    "name": filename,
                    "path": file_path,
                    "size": file_size,
                    "hash": file_hash,
                    "folder": current_dir,
                    "extension": Path(filename).suffix.lower(),
                }
                all_files.append(file_info)

                if file_hash in hash_dict:
                    hash_dict[file_hash].append(file_path)
                else:
                    hash_dict[file_hash] = [file_path]

                total_files += 1

            except (FileNotFoundError, PermissionError):
                continue
            except Exception:
                continue

    scan_time = round(time.time() - start_time, 2)

    if total_files == 0:
        return {
            "folder_path": folder_path,
            "total_files": 0,
            "duplicate_files": 0,
            "space_saved": 0,
            "all_files": [],
            "duplicate_groups": [],
            "scan_time": scan_time,
            "error": None,
            "message": "The folder is empty or contains no readable files.",
        }

    duplicate_groups = []
    duplicate_count = 0
    total_space_saved = 0

    for file_hash, file_list in hash_dict.items():
        if len(file_list) > 1:
            try:
                file_size = os.path.getsize(file_list[0])
            except OSError:
                file_size = 0

            group = {
                "hash": file_hash,
                "size": file_size,
                "files": file_list,
                "original": file_list[0],
                "duplicates": file_list[1:],
                "count": len(file_list),
            }
            duplicate_groups.append(group)

            duplicate_count += len(file_list) - 1
            total_space_saved += file_size * (len(file_list) - 1)

    return {
        "folder_path": folder_path,
        "total_files": total_files,
        "duplicate_files": duplicate_count,
        "space_saved": total_space_saved,
        "all_files": all_files,
        "duplicate_groups": duplicate_groups,
        "scan_time": scan_time,
        "error": None,
    }
