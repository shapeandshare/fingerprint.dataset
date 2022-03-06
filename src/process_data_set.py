import logging

from .contracts.dtos.data_set import DataSet

if __name__ == "__main__":
    # Set log level (from default: warning) to info
    logging.getLogger().setLevel(logging.INFO)

    data_set: DataSet = DataSet(name="dataset", search_path=".")
    data_set.build_index()
    data_set.generate_hash()
    data_set.generate_csv()
    data_set.generate_dataframe()
