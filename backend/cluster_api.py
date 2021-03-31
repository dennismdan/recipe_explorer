import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.pipeline import Pipeline
from typing import List,Tuple

import pickle
import os

from run_time_constants import data,models,pipelineFilePath, fullDataFilePath



class ClusterAPI:
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
        # Initialize class attributes at runtime
        self.rawUserInput:str = stringInput
        self.userIngredientInput:List[str] = self.cleanUserInput(self.rawUserInput)
        self.pathToModel = pipelineFilePath
        self.fullDf: pd.DataFrame = pd.read_csv(fullDataFilePath, header=0, sep=',')
        self.pipelineMode:Pipeline = self.getModel(self.pathToModel)
        self.returnRecipeCount: int = topNrRecipes

        # Initialize class attributes that will be assigned with functions calls
        self.clusterNumber:int = None
        self.clusterDf:pd.DataFrame = None
        self.clusterTopDf: pd.DataFrame = None
        self.edgesDf:pd.DataFrame = None
        self.edgesTopDf:pd.DataFrame = None

    def cleanData(self, fileName:str)->pd.DataFrame:
        #TODO: possibly for beggining only, low priority
        pass

    def cleanUserInput(self, userInputString:str)->List[str]:
        """
        :param userInputString: a string that user input into the webinterface passed to backend
        :return: cleanup the string and place it into a list
        """
        #TODO: add additional string processing to make sure we cover some cleanup cases

        userInputString = userInputString.strip()
        userInputString = [userInputString]

        return userInputString

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

    def getModel(self,filePath:str=None)->Pipeline:
        # load the model from directory
        #TODO: further define the method if neccessary
        if filePath is None:
            filePath = self.pathToModel

        loaded_model = pickle.load(open(filePath, 'rb'))

        return loaded_model

    def predictCluster(self, model:Pipeline = None, newRecipe:List[str] = None)->int:
        """
        :param model: Pipeline model
        :param stringInput: one recipe input in format ["ingridient1, ingridient2...."] all in one string in a list
        :return: return class that the "recipe" belongs to according to model
        """

        if model is None:
            model = self.pipelineMode
        if newRecipe is None:
            newRecipe = self.userIngredientInput

        self.clusterNumber = model.predict(newRecipe)[0]

        return int(self.clusterNumber)

    def getClusterData(self, clusterNr:int = None)->pd.DataFrame:
        """
        :param clusterNr:
        :param returnRecipeCount:
        :return: all data for a cluster
        """
        if clusterNr is None:
            clusterNr = self.predictCluster()

        self.clusterDf = self.fullDf.where(self.fullDf.cluster == clusterNr).dropna()
        self.clusterDf.RecipeId = self.clusterDf.RecipeId.astype("int")
        
        return self.clusterDf

    def getEdgesDf(self, df:pd.DataFrame = None)->pd.DataFrame:
        """
        :param df:subset of data belonging to a cluster
        :return: df as a nodal graph with nodeIdA and nodeIdB with edge_weights
        """

        if df is None and self.clusterDf is not None:
            df = self.clusterDf
        elif df is None:
            print("")
            NoClusterDfError("No dataframe for cluster defined. "
                             "Call methods getClusterData() to create the dataframe first")
        else:
            print("dataframe passed to function")


        corpus = df["RecipeIngredientParts"].tolist()
        ids = df["RecipeId"].tolist()
        ids = [int(id_) for id_ in ids]
        assert isinstance(ids,list)

        #create the sparse matrix
        countVectorizer = CountVectorizer(stop_words={'english'})
        vectorizorModel = countVectorizer.fit(corpus)
        X = vectorizorModel.transform(corpus)

        #multiply to get the correlations
        nodalSparseGraph = X @ X.T
        c = nodalSparseGraph.tocoo()

        #reformat to pandas and assign back the recipe ids
        nodesWeights = pd.DataFrame({"recipeIdA": c.row, "recipeIdB": c.col, "edge_weight": c.data})
        nodesWeights["recipeIdA"] = nodesWeights.recipeIdA.apply(lambda x: ids[x])
        nodesWeights["recipeIdB"] = nodesWeights.recipeIdB.apply(lambda x: ids[x])
        self.edgesDf = nodesWeights[nodesWeights["recipeIdA"] != nodesWeights["recipeIdB"]]
        return self.edgesDf

    def getClusterTopData(self,returnRecipeCount:int = None):
        # TODO: this method will need to run getNodalGraph

        if returnRecipeCount is None:
            returnRecipeCount = self.returnRecipeCount

        if self.clusterDf is None:
            raise NoClusterDfError("clusterDf is not defined, getClusterData method must run first")

        if self.edgesDf is None:
            raise NoClusterDfError("edgesDf is not defined, getNodeGraph method must run first")

        clusterDf = self.clusterDf.copy()

        subsetNodesDF = self.edgesDf.copy()

        subsetNodesDF = subsetNodesDF[["recipeIdA", "edge_weight"]].groupby("recipeIdA").sum()

        nodeList = subsetNodesDF.sort_values(by="edge_weight", ascending=False).head(returnRecipeCount).index.tolist()

        self.clusterTopDf = clusterDf[clusterDf.RecipeId.isin(nodeList)]

        return self.clusterTopDf

    def getEdgesTop(self):
        if self.clusterTopDf is None:
            raise NoClusterDfError("self.clusterTopDf is not defined, getClusterTopData method must run first")

        if self.edgesDf is None:
            raise NoClusterDfError("edgesDf is not defined, getNodeGraph method must run first")

        nodeList = self.clusterTopDf.RecipeId.unique().tolist()
        edgesTopDf = self.edgesDf.copy()
        edgesTopDf = edgesTopDf[self.edgesDf.recipeIdA.isin(nodeList)]
        edgesTopDf = edgesTopDf[self.edgesDf.recipeIdB.isin(nodeList)]

        self.edgesTopDf = edgesTopDf

        return self.edgesTopDf

    def topRecipeData(self)->Tuple[pd.DataFrame,pd.DataFrame,int]:
        model = self.pipelineMode
        newRecipe = self.userIngredientInput
        returnRecipeCount = self.returnRecipeCount

        clusterNr = self.predictCluster(model, newRecipe)

        dfFull = self.getClusterData(clusterNr)
        edgesDf = self.getEdgesDf(dfFull)

        dfTop = self.getClusterTopData(returnRecipeCount)
        edgesTop = self.getEdgesTop()

        return dfTop,edgesTop,clusterNr

class NoClusterDfError(Exception):
    """
    class to handle custom exceptions
    """
    pass

