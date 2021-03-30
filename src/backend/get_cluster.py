import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import HashingVectorizer
import pickle

class ClusterData:
    def __init__(self, stringInput:str, topNrRecipes:int):
        self.stringInput:str = stringInput
        self.pathToModel = "ec2 path to the saved model (pickle file)"

        self.df: pd.DataFrame = None
        self.model:KMeans = None
        self.classNumber:int = None
        self.classData:pd.DataFrame = None

    def fitModel(self):
        pass

    def vecotrizeString(self):
        pass

    def getClusterData(self, clusterNr:int = None):
        "TODO: sort and return top N"
        dfCluster = self.df.where(self.df.cluster == clusterNr)

        return dfCluster

    def saveModel(self,model):
        # save the model to disk
        try:
            filename = 'finalized_model.sav'
            pickle.dump(model, open(filename, 'wb'))
            return True

        except:
            return False

    def getModel(self,filename:str):
        # load the model from disk
        loaded_model = pickle.load(open(filename, 'rb'))

        return loaded_model



