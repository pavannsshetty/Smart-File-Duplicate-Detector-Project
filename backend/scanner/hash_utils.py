import hashlib


def calculate_hash(file_path, chunk_size=65536):
    try:
        sha256_hash = hashlib.sha256()

        with open(file_path, "rb") as file:
            chunk = file.read(chunk_size)
            while chunk:
                sha256_hash.update(chunk)
                chunk = file.read(chunk_size)

        return sha256_hash.hexdigest()

    except (FileNotFoundError, PermissionError, Exception) as error:
        raise error
