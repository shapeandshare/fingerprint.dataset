import logging

from src.com.shapeandshare.fingerprint.dataset import DataSet

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    data_set: DataSet = DataSet(name="dataset", search_path=".")
    data_set.hash()
    data_set.generate_dataframe()
    # data_set.delete_generated_reports()

    # One-Liner
    # DataSet(name="dataset", search_path=".").generate_dataframe()
