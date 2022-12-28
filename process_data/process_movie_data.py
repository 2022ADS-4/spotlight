### This script contains class and methods that processes.
## This script will download, merge and process data, and outputs ready-to-train movielens data in gzip format.
import requests, tempfile, os, zipfile, gzip, shutil
import pandas as pd
from config import DATA_PATH
import json

class MovieLens:
    """
    This class is for Movielens data.
    The Movielens data is downloaded, processed, gzipped
    in this class.
    """
    URL_DATA = "https://files.grouplens.org/datasets/movielens/ml-latest.zip"
    URL_DEMO = "https://files.grouplens.org/datasets/movielens/ml-latest-small.zip"
    URL_100K = "https://files.grouplens.org/datasets/movielens/ml-100k.zip"

    def __init__(
            self,
            use_demo_data:bool=False,
            use_big_data:bool=True,
            data_size_variant=None,
            temp_folder=None,
            data_download_path = None,
            merged_data_path = None,
            movies_json = None,
            output_path=None,
            compress=True
    ):
        self.use_demo_data = use_demo_data
        self.use_big_data = use_big_data
        self.data_size_variant = data_size_variant
        if all([use_big_data, use_demo_data]): ## make sure not both are selected
            raise Exception("Cannot download both demo and big data at the same time")

        self.tempfolder = tempfile.mkdtemp(prefix="movielens") if temp_folder is None else temp_folder
        self.data_path = tempfile.mktemp(prefix="movielens_data", suffix=".zip", dir=self.tempfolder) if data_download_path is None else data_download_path
        self.data_merged = tempfile.mktemp(prefix="movielens_merged", suffix=".csv", dir=self.tempfolder) if merged_data_path is None else merged_data_path
        self.movies_json = tempfile.mktemp(prefix="movielens_moviestitles", suffix=".json", dir=self.tempfolder) if movies_json is None else movies_json

        self.compress = compress
        self.output_path = output_path
        ###Variables used in the methods
        if self.data_size_variant is not None:
            if self.data_size_variant == "100K":
                self.url = self.URL_100K
        else:
            self.url = self.URL_DATA if self.use_big_data and not self.use_demo_data else self.URL_DEMO
        self.zipped_folder_name = self.url.split("/")[-1].split(".")[0]  ## To get the folder name from the url

        self.movies_path = os.path.join(self.tempfolder, self.zipped_folder_name, "movies.csv")
        self.links_data = None
        self.movies_data = None
        self.ratings_data = None
        self.tags_data = None

    def process(self):
        self.get_data()
        if self.compress:
            self.compress_data(self.data_merged, self.output_path)
        else:
            os.replace(self.data_merged, self.output_path)

        os.replace(self.movies_json, os.path.join(DATA_PATH, "movie_titles.json"))

        #self.remove_temp(self.tempfolder)

    def process_upload_db(self,collection):
        data = []
        for user_data in self.parse_csv(self.output_path):
            data.append(user_data)
        self.upload_data(collection,data)

    def process_data_for_spotlight_model(self):
        """
        returns data similar to spotlight's code
        """
        from spotlight.interactions import Interactions
        import numpy as np

        user_id = []
        item_id = []
        rating = []
        #timestamp = []

        for user_data in self.download_data_from_db():
            if user_data["user_id"] is None or user_data["movie_id"] is None or user_data["rating"] is None: continue
            user_id.append(int(user_data["user_id"]))
            item_id.append(int(user_data["movie_id"]))
            rating.append(float(user_data["rating"]))
            #timestamp.append(int(float(user_data["timestamp"])))

        return Interactions(
            user_ids=np.array(user_id)[:],
            item_ids=np.array(item_id)[:],
            ratings=np.array(rating)[:],
            #timestamps=np.array(timestamp)[:]
        )

    def download_data(self):
        ### downloads data from movielens link to a zip file
        req = requests.get(self.url)
        if not req.ok:
            raise ConnectionError("Bad connection")
        with open(self.data_path, 'wb') as output_file:
            output_file.write(req.content)

    def unzip_data(self):
        ### unzips and extracts the files inside the zip
        with zipfile.ZipFile(self.data_path, 'r') as zip_ref:
            zip_ref.extractall(self.tempfolder)

    def get_data(self):
        self.download_data()
        self.unzip_data()

        self.links_data = pd.read_csv(os.path.join(self.tempfolder, self.zipped_folder_name, "links.csv"))
        self.movies_data = pd.read_csv(os.path.join(self.tempfolder, self.zipped_folder_name, "movies.csv"))
        self.ratings_data = pd.read_csv(os.path.join(self.tempfolder, self.zipped_folder_name, "ratings.csv"))
        self.tags_data = pd.read_csv(os.path.join(self.tempfolder, self.zipped_folder_name, "tags.csv"))

        self.merge_file()
        self.get_movie_titles_json()

    def merge_file(self):
        ### merge the csv files
        files_to_merged = ["links.csv", "movies.csv", "ratings.csv", "tags.csv"]

        merged_data = pd.merge(
            pd.merge(
                pd.merge(self.movies_data, self.ratings_data, on="movieId", how="outer"), #1
                self.tags_data, on=["userId", "movieId", "timestamp"], how="outer"), #2
            self.links_data, on="movieId", how="outer" #3
        )

        merged_data.to_csv(self.data_merged, index=False)

    def get_movie_titles_json(self):
        movies_dict = {}
        with open(self.movies_path, "r") as fh:
            for line in fh:
                if line.startswith("movieId"): continue
                movie_id, title = line.strip().split(",")[:2]
                if movie_id not in movies_dict:
                    movies_dict[movie_id] = title

        with open(self.movies_json, "w") as mj:
            json.dump(movies_dict, mj)
    @staticmethod
    def parse_csv(in_csv):
        import csv
        with open(in_csv, "r") as fh:
            for line in csv.reader(fh):
                if "movieId" in line: continue
                movie_id = line[0]
                title = line[1]
                genres: list = line[2].split("|")
                user_id = line[3]
                rating = line[4]
                timestamp = line[5]
                yield {
                        "movie_id": movie_id,
                        "title": str(title),
                        "genres": genres,
                        "user_id": str(int(float(user_id))) if user_id != "" else None,
                        "rating": float(rating) if rating != "" else None,
                        "timestamp":timestamp
                    }

    @staticmethod
    def upload_data(collection,data):
        from API.connect_db import MongoDB
        mdb = MongoDB(collection=collection)
        if isinstance(data, dict):
            mdb.insert_entry(data)
        elif isinstance(data, list):
            mdb.insert_many_entries(data)
        else:
            raise Exception("Could not identify data type to upload")
    @staticmethod
    def convert_csv2dict(in_csv):
        """
        converts the merged data into a dictionary for to upload to mongo DB
        """
        import csv
        data = []
        with open(in_csv, "r") as fh:
            for line in csv.reader(fh):
                if "movieId" in line: continue
                movie_id = line[0]
                title = line[1]
                genres: list = line[2].split("|")
                user_id = line[3]
                rating = line[4]
                data.append(
                    {
                        "movie_id": movie_id,
                        "title": str(title),
                        "genres": genres,
                        "user_id": str(int(float(user_id))) if user_id != "" else None,
                        "rating": float(rating) if rating != "" else None
                    })
        return data

    @staticmethod
    def download_data_from_db():
        from API.connect_db import MongoDB
        mbd = MongoDB()
        return list(mbd.get_info({}))

    def save_data(self):
        pass

    @staticmethod
    def compress_data(infile, outfile):
        import gzip
        with open(infile, 'rb') as f_in, gzip.open(f"{outfile}.gz", 'wb') as f_out:
            f_out.writelines(f_in)

    @staticmethod
    def remove_temp(path):
        ### removes a path and children underneath
        shutil.rmtree(path=path)

#ml = MovieLens(use_demo_data=True, use_big_data=False, output_path=os.path.join(DATA_PATH, "ml-data.csv"))
#ml.process_upload_db(collection="main")

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import seaborn as sns

class VisualizeData:
    """
    This class will visualize the characteristics of input data
    output is a pdf file with all the figures
    data_file: csv file
    out_pdf: output path for the pdf file. default data folder
    """

    data_folder = DATA_PATH

    def __init__(self, data_file:str, out_pdf:str=None, numeric_data_keys=None):
        ###Files
        self.data_file = data_file
        self.out_pdf = out_pdf if out_pdf is not None else os.path.join(self.data_folder, "data_summary.pdf")
        self.numeric_data_keys = numeric_data_keys

        ### declare pandas dataframe
        self.dataframe:pd.DataFrame = self.read_data()


        ### Add to a dictionary that collects what to be plotted
        self.plot_variables = {}

    def process(self):
        self.plot_numeric_data(keys=self.numeric_data_keys)
        self.plot_category_counts()
        self.plot_data_distribution(keys=self.numeric_data_keys)
        self.plot_null()
        self.plot_corr_matrix(keys=self.numeric_data_keys)
        self.save_to_pdf()
    def read_data(self):
        """
        reads the data from 'data_file' and converts it into a pandas dataframe
        """
        if self.data_file.endswith(".gz") or self.data_file.endswith(".gzip"):
            return pd.read_csv(self.data_file, compression="gzip", sep=",")
        else:
            return pd.read_csv(self.data_file, sep=",")

    def plot_data_distribution(self, keys):
        ### get data description
        #data_desc = self.dataframe.describe().reset_index()
        data_desc = self.dataframe.loc[:, keys]
        skew = {}
        kurt = {}
        for i in data_desc:
            skew[i] = data_desc[i].skew()
            kurt[i] = data_desc[i].kurt()

        fig_skew = plt.figure()
        plt.plot(list(kurt.keys()), list(kurt.values()))
        #plt.xticks(rotation=45, horizontalalignment='right')
        plt.title("Skew Plot")
        self.plot_variables["skew_plot"] = fig_skew

        fig_kurt = plt.figure()
        plt.plot(list(skew.keys()), list(skew.values()))
        #plt.xticks(rotation=45, horizontalalignment='right')
        plt.title("Kurt Plot")
        self.plot_variables["kurt_plot"] = fig_kurt

    def plot_corr_matrix(self, keys=None):
        corrmat = self.dataframe.corr() if keys is None else self.dataframe.loc[:, keys].corr()
        fig = plt.figure()
        sns.heatmap(corrmat, vmax=1, annot=True, linewidths=.5)
        plt.xticks(rotation=30, horizontalalignment='right')
        plt.yticks(rotation=30, horizontalalignment='right')
        plt.title("Correlation Heatmap")

        ### Add variable dictionary
        self.plot_variables["correlation_matrix"] = fig

    def plot_null(self):
        ### Identify null_df
        null_df = self.dataframe.apply(lambda x: sum(x.isnull())).to_frame(name="count")
        fig = plt.figure()
        plt.bar(null_df.index, null_df['count'])
        plt.title("NaN Values")
        plt.xticks(null_df.index, null_df.index, rotation=45, horizontalalignment='right')
        plt.xlabel("column names")
        plt.ylabel("count")
        plt.margins(0.1)
        ### Add to a dictionary that collects what to be plotted
        self.plot_variables["NaN"] = fig

    def plot_numeric_data(self, keys=None):
        for clm in keys:
            fig = plt.figure()
            self.dataframe.loc[:, [clm]].boxplot()
            plt.title(f"{clm} Values")
            self.plot_variables[clm] = fig

    def plot_category_counts(self):
        category_counts_dict = self.get_genre_counts()
        fig = plt.figure()
        plt.bar(category_counts_dict.keys(), category_counts_dict.values())
        plt.xticks(rotation=35, horizontalalignment='right')
        plt.title("Genre Counts")
        plt.xlabel("Genres")
        plt.ylabel("counts")
        plt.margins(0.1)
        ### Add to a dictionary that collects what to be plotted
        self.plot_variables["genre_counts"] = fig

    def get_genre_counts(self, keys=None):
        keys = keys if keys is not None else ["movieId"]
        keys.append("genres")
        movie_genres = self.dataframe.loc[:, keys].drop_duplicates().dropna(axis=0)
        genres = movie_genres["genres"].apply(lambda x: x.strip().split("|"))

        genre_count_dict = {}

        for genre_list in genres:
            for genre in genre_list:
                if genre in genre_count_dict:
                    genre_count_dict[genre] += 1
                    continue
                genre_count_dict[genre] = 1

        return genre_count_dict

    def save_to_pdf(self):
        # Create the PdfPages object to which we will save the pages:
        # Gets the figures from the "self.plot_variable" dictionary
        # Prints each figure to a pdf.
        with PdfPages(self.out_pdf) as pdf:
            if self.plot_variables is not None:
                for var_name, var_plot in self.plot_variables.items():
                    pdf.savefig(var_plot)
