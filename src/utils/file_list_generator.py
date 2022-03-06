from pathlib import Path
from typing import Optional

from tqdm import tqdm


# root_dir: Path = Path("G:/Dropbox")
# root_dir: Path = Path(".")
def generate_file_list(base: Optional[Path] = None):
    if not base:
        base = Path(".")

    with open("file_list.txt", mode="w", encoding="utf-8") as file:
        for child in tqdm(base.glob("**/*")):
            if child.is_file():
                file.write(f"{child.resolve().as_posix()}\r\n")


if __name__ == "__main__":
    generate_file_list(base=Path("G:/Dropbox"))
