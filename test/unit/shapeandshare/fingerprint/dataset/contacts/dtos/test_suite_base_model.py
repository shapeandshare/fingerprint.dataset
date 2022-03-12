import unittest


class BaseModelTestSuite(unittest.TestCase):
    def test_should(self):
        pass


if __name__ == "__main__":
    runner = unittest.TextTestRunner()
    runner.run(BaseModelTestSuite())
