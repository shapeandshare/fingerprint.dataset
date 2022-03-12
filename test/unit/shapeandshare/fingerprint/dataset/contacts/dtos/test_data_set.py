import logging
import shutil
import unittest
import uuid
from pathlib import Path

from src.shapeandshare.fingerprint.dataset import DataSet

logging.basicConfig(level=logging.DEBUG)


class TestDataSet(unittest.TestCase):
    search_path: Path = Path(".") / "test" / "fixtures"
    name: str = f"dataset-unittest-{uuid.uuid4()}"
    output_path: Path = Path(name)

    def setUp(self) -> None:
        self.maxDiff = None

        if self.output_path.exists() and self.output_path.is_dir():
            shutil.rmtree(self.output_path.resolve().as_posix())

    def tearDown(self) -> None:
        if self.output_path.exists() and self.output_path.is_dir():
            shutil.rmtree(self.output_path.resolve().as_posix())

    def test_should_load_normally(self):
        DataSet(name=self.name, search_path=self.search_path)
        self.assertTrue(self.output_path.exists())
        self.assertTrue(self.output_path.is_dir())
        self.assertTrue((self.output_path / ".hashes").exists())
        self.assertTrue((self.output_path / ".hashes").is_dir())
        self.assertTrue((self.output_path / f"{self.name}.txt").exists())
        self.assertTrue((self.output_path / f"{self.name}.txt").is_file())

    def test_should_load_normally_with_recreate(self):
        self.output_path.mkdir()
        with open((self.output_path / "sample.txt").resolve().as_posix(), mode="w", encoding="utf-8") as file:
            file.write("test")
        DataSet(name=self.name, search_path=self.search_path, recreate=True)
        self.assertFalse((self.output_path / "sample.txt").exists())

    def test_should_load_normally_without_reindex(self):
        DataSet(name=self.name, search_path=self.search_path, index=False)
        self.assertFalse((self.output_path / f"{self.name}.txt").exists())

    def test_should_handle_consecutive_runs(self):
        DataSet(name=self.name, search_path=self.search_path)
        dataset: DataSet = DataSet(name=self.name, search_path=self.search_path, recreate=False)
        dataset.build_index()
        dataset.build_index(recreate=True)

    def test_should_run_normally(self):
        dataset: DataSet = DataSet(name=self.name, search_path=self.search_path)
        dataset.hash()
        dataset.generate_dataframe()


if __name__ == "__main__":
    runner = unittest.TextTestRunner()
    runner.run(TestDataSet())
