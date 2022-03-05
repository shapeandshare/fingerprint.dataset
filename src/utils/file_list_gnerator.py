import json
from pathlib import Path
from typing import List

file_list: List = []

# "G:\Dropbox"
# root_dir: Path = Path("G:/Dropbox")
root_dir: Path = Path("../..")
for child in root_dir.glob("**/*"):
    if child.is_file():
        file_list.append(child.resolve().as_posix())
        print(".", end="")

with open("../file_list.json", mode="w", encoding="utf-8") as file:
    file.write(json.dumps(file_list, indent=4))

# with open("file_list.json", mode="r", encoding="utf-8") as file:
#     imported: Dict = json.load(file)
