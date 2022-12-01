import unittest
from process_data.process_movie_data import MovieLens
import tempfile, shutil, os
from tests import TEST_DATA_PATH
import filecmp
test_out_dir = tempfile.mkdtemp(prefix="test_data_update")

class MovielensDataTest(unittest.TestCase):

    def test_class_init(self):
        ##This class should raise error when both demo_data and big_data are given same boolean
        self.assertRaises(Exception, MovieLens.__init__, use_demo_data=False, use_big_data=False)
        self.assertRaises(Exception, MovieLens.__init__, use_demo_data=True, use_big_data=True)
        self.assertRaises(Exception, MovieLens.__init__, use_demo_data=0, use_big_data=0)

    def test_compress_data(self): ##FIXME
       """ ### Making sure compress method works as expected
        infile = os.path.join(TEST_DATA_PATH, "test_compress_data_input.txt")
        expected_out = os.path.join(TEST_DATA_PATH, "test_compress_data_in.txt.gz")

        test_out = tempfile.mktemp(dir=test_out_dir, suffix=".txt")
        MovieLens.compress_data(infile, test_out)
        print(test_out)
        self.assertTrue(filecmp.cmp(
            f"{test_out}.gz",
            expected_out,
            shallow=False),
        ) """

    def test_download_data(self):
        ### this is test to see download error
        MovieLens.URL_DEMO = "https://files.grouplens.org/datasets/movielens/somemockdata"
        self.assertRaises(ConnectionError, lambda: MovieLens(use_demo_data=True, use_big_data=False).download_data())

