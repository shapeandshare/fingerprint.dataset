from pathlib import Path
import pandas as pd


def export_to_df():
    files_df: pd.DataFrame = pd.read_csv("file_list.csv")
    files_df.to_pickle(path=(Path(".") / "file_list.df.pkl.bz2").resolve().as_posix(), compression={"method": "bz2"})


if __name__ == "__main__":
    export_to_df()
