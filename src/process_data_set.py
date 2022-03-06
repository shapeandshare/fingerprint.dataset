from .contracts.dtos.data_set import DataSet

if __name__ == "__main__":
    data_set: DataSet = DataSet(name="dataset", search_path=".")
    data_set.build_index()
    data_set.generate_hash()
    data_set.generate_csv()
    data_set.generate_dataframe()
