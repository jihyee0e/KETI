import hashlib

def get_file_hash(file):
    file.seek(0)
    file_bytes = file.read()
    file.seek(0)
    return hashlib.md5(file_bytes).hexdigest()

def deduplicate_files(files):
    seen_hashes = set()
    unique = []
    duplicates = []

    for file in files:
        file_hash = get_file_hash(file)
        if file_hash not in seen_hashes:
            seen_hashes.add(file_hash)
            unique.append(file)
        else:
            duplicates.append(file.name)
    return unique, duplicates