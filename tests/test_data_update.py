import unittest
from process_data.process_movie_data import MovieLens, VisualizeData
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

    def test_download_data(self):
        ### this is test to see download error
        MovieLens.URL_DEMO = "https://files.grouplens.org/datasets/movielens/somemockdata"
        self.assertRaises(ConnectionError, lambda: MovieLens(use_demo_data=True, use_big_data=False).download_data())

    def __deprecated_test_data_merge(self):
        ## initiate class
        test_output = tempfile.mktemp(dir=test_out_dir, prefix="test_data_merge", suffix=".csv")
        ml_obj = MovieLens(
            temp_folder=test_out_dir,
            output_path=test_output,
            merged_data_path=test_output,
            data_download_path=os.path.join(TEST_DATA_PATH, "movielens_files.zip"),
            use_demo_data=True,
            use_big_data=False
        )

        ml_obj.unzip_data()
        ml_obj.merge_file()

        self.assertTrue(filecmp.cmp(
            os.path.join(TEST_DATA_PATH, "test_merged_data.csv"),
            test_output
        ))


class TestVisualizeData(unittest.TestCase):

    def test_genre_counts(self):
        ##initiate class
        vd_obj = VisualizeData(
            data_file=os.path.join(TEST_DATA_PATH, "test_merged_data.csv")
        )
        test_genre_dict = vd_obj.get_genre_counts()
        expected_dict = {
            '(no genres listed)': 34,
            'Action': 1828,
            'Adventure': 1263,
            'Animation': 611,
            'Children': 664,
            'Comedy': 3756,
            'Crime': 1199,
            'Documentary': 440,
            'Drama': 4361,
            'Fantasy': 779,
            'Film-Noir': 87,
            'Horror': 978,
            'IMAX': 158,
            'Musical': 334,
            'Mystery': 573,
            'Romance': 1596,
            'Sci-Fi': 980,
            'Thriller': 1894,
            'War': 382,
            'Western': 167
        }
        ###Look if output dictionary is as expected
        self.assertDictEqual(test_genre_dict, expected_dict)

        ### change key
        self.assertRaises(AttributeError, lambda: vd_obj.get_genre_counts(["genres"]))

        expected_dict = {
            '(no genres listed)': 47,
            'Action': 30635,
            'Adventure': 24161,
            'Animation': 6988,
            'Children': 9208,
            'Comedy': 39053,
            'Crime': 16681,
            'Documentary': 1219,
            'Drama': 41928,
            'Fantasy': 11834,
            'Film-Noir': 870,
            'Horror': 7291,
            'IMAX': 4145,
            'Musical': 4138,
            'Mystery': 7674,
            'Romance': 18124,
            'Sci-Fi': 17243,
            'Thriller': 26452,
            'War': 4859,
            'Western': 1930}

        test_genre_dict = vd_obj.get_genre_counts(["userId", "movieId"])
        self.assertDictEqual(test_genre_dict, expected_dict)


if __name__ == "__main__":
    try:
        unittest.main()
    finally:
        shutil.rmtree(test_out_dir)