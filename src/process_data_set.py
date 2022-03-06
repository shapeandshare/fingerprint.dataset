from .contracts.dtos.data_set import DataSet

if __name__ == "__main__":
    data_set: DataSet = DataSet(name="dataset", search_path=".")
    data_set.generate_file_list()
    data_set.generate_file_list_hashes()
    data_set.build_csv()
    data_set.export_to_df()
