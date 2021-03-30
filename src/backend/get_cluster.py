import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.pipeline import Pipeline
from typing import List

import pickle


class ClusterData:
    def __init__(self, stringInput:List[str], topNrRecipes:int):
        """
        :param stringInput: ["ingredient 1", "chicken..."]
        :param topNrRecipes: 40 - return 50 recipes in the cluster

        1. get a list of ingridients
        2. predict from list
        3. get cluster
        4. filter top N
        5. return DF

        ...

        TODO: add additional api inputs (work with Jonathan)
        TODO: if save model locally to app files to use later - make sure to have a cleanup method
        TODO: predictCluster
        TODO: run class with inputs to methods or __init__ to get results
        TODO: setup and read pipeline model not kmeans model
        TODO: decide on whether to split class to two (get model and actual model class)


        TODO:  clean data before hand (Orion)
        TODO: get the pipeline working (Dennis)
        """

        self.stringInput:str = stringInput
        self.pathToModel = "ec2 path to the saved model (pickle file)"
        self.filename = ""
        self.pipelineMode:Pipeline = self.getModel(self, self.filename)


        self.df:pd.DataFrame = None

        self.classNumber:int = None
        self.classData:pd.DataFrame = None

    def cleanData(self, fileName:str)->pd.DataFrame:
        #TODO: possibly for beggining only, low priority
        pass

    def fitModel(self):
        # Building a new cluster model
        # time intensive but possible on smaller subsets of data
        # ideally do this beforehand and have a pipeline model
        pass

    def saveModel(self, model):
        # save the model to disk
        # TODO: define differences between save and get?
        try:
            filename = 'finalized_model.sav'
            pickle.dump(model, open(filename, 'wb'))
            return True

        except:
            return False

    def getModel(self,filename:str)->Pipeline:
        # load the model from disk
        #TODO: further define the method if neccessary

        loaded_model = pickle.load(open(filename, 'rb'))

        return loaded_model

    def predictCluster(self,model: KMeans,stringInput:List[str])->int:
        """
        :param model: Pipeline model
        :param stringInput:
        :return: return class that the "recipe" belongs to according to model
        """
        #TODO: make method actionable
        #1. class = model.predict(stringInput)
        #cluster  = pipelineMode.predict("")
        pass

    def getClusterData(self, clusterNr:int = None)->pd.DataFrame:
        # TODO: implement code to sort and return top N
        # TODO: agree what all fields of data we should return for each cluster
        # TODO: implement data filter for desired fields
        # Use results from cluster, returns subset of data based on some N value

        dfCluster = self.df.where(self.df.cluster == clusterNr)

        return dfCluster



