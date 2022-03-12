import unittest
from pathlib import Path

from src.shapeandshare.fingerprint.dataset import DataSet


class TestDataSet(unittest.TestCase):
    def test_should_(self):
        search_path: Path = Path(".") / "test" / "fixtures"
        name: str = "dataset"
        dataset: DataSet = DataSet(name=name, search_path=search_path)

        output_path: Path = Path(name)
        self.assertTrue(output_path.exists())
        self.assertTrue(output_path.is_dir())
        self.assertTrue((output_path / ".hashes").exists())
        self.assertTrue((output_path / ".hashes").is_dir())
        self.assertTrue((output_path / f"{name}.txt").exists())
        self.assertTrue((output_path / f"{name}.txt").is_file())


if __name__ == "__main__":
    runner = unittest.TextTestRunner()
    runner.run(TestDataSet())
