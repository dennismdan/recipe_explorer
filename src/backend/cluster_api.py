import datetime
import json
import time

import pandas as pd
import numpy as np

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.preprocessing import MinMaxScaler
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

        recipeDf cols = "RecipeId","Name","RecipeIngredientParts",
                        "RecipeIngredientQuantities","Description",
                        "Images","RecipeCategory","Keywords"
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
        self.nodesAndWeights = None
        self.nodeList = None

    def cleanUserInput(self, userInputString:str)->List[str]:
        """
        :param userInputString: a string that user input into the webinterface passed to backend
        :return: cleanup the string and place it into a list
        """
        #TODO: add additional string processing to make sure we cover some cleanup cases

        userInputString = userInputString.strip()
        userInputString = [userInputString]

        return userInputString

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
        assert isinstance(newRecipe, list)
        assert isinstance(newRecipe[0],str)
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

    def getClusterTopData(self,returnRecipeCount:int = None):
        # TODO: this method will need to run getNodalGraph

        if returnRecipeCount is None and self.returnRecipeCount is not None:
            returnRecipeCount = self.returnRecipeCount
        elif returnRecipeCount is None and self.returnRecipeCount is None:
            raise NoClusterDfError("A number for recipe count wasn't defined")

        if self.clusterDf is None:
            raise NoClusterDfError("clusterDf is not defined, getClusterData method must run first")

        clusterDf = self.clusterDf.copy()

        self.clusterTopDf = clusterDf.sample(n = returnRecipeCount)

        return self.clusterTopDf

    def setNodeSizes(self, df:pd.DataFrame = None)->pd.DataFrame:
        """
        :param df:subset of data belonging to a cluster
        :return: df as a nodal graph with nodeIdA and nodeIdB with edge_weights
        """

        if df is None and self.clusterTopDf is not None:
            df = self.clusterTopDf
        elif df is None:
            print("")
            NoClusterDfError("No dataframe for cluster defined. "
                             "Call methods getClusterTopData() to create the dataframe first")
        else:
            print("dataframe passed to function")


        corpus = df["RecipeIngredientParts"].tolist()
        ids = df["RecipeId"].tolist()
        ids = [int(id_) for id_ in ids]

        #create the sparse matrix
        vectorizer = TfidfVectorizer(stop_words={'english'},use_idf=True)
        vectorizorModel = vectorizer.fit(corpus)
        X = vectorizorModel.transform(corpus)

        #multiply to get the correlations
        nodalSparseGraph = X @ X.T
        nodalSparseGraph = np.array(nodalSparseGraph.todense())

        #extract only lower triangle to reduce repeating endges
        nodalGraph = np.tril(nodalSparseGraph,k=-1) #sets diag =0 also
        shape = nodalGraph.shape

        coordinates = {"recipeIdA": [], "recipeIdB": [], "edge_weight": []}
        for row in range(shape[0]):
            for col in range(shape[1]):
                weight = nodalGraph[row][col]
                if weight > 0:
                    coordinates["recipeIdA"].append(row)
                    coordinates["recipeIdB"].append(col)
                    coordinates["edge_weight"].append(weight)



        #place values into pandas
        edgesDf = pd.DataFrame(coordinates)

        #normalize weights from 0 to 1
        scaler = MinMaxScaler()
        edgesDf["edge_weight"] = scaler.fit_transform(edgesDf[["edge_weight"]])
        edgesDf["edge_weight"] = edgesDf["edge_weight"].round(2)
        #reformat to pandas and assign back the recipe ids
        edgesDf["recipeIdA"] = edgesDf.recipeIdA.apply(lambda x: ids[x])
        edgesDf["recipeIdB"] = edgesDf.recipeIdB.apply(lambda x: ids[x])

        df1 = edgesDf[["recipeIdA", "edge_weight"]].rename(columns={"recipeIdA": "RecipeId","edge_weight":"nodeSize"})
        df2 = edgesDf[["recipeIdB", "edge_weight"]].rename(columns={"recipeIdB": "RecipeId","edge_weight":"nodeSize"})

        nodeSizes = pd.concat([df1, df2])
        nodeSizes = nodeSizes.groupby("RecipeId", as_index=False).sum()
        nodeSizes["nodeSize"] = scaler.fit_transform(nodeSizes[["nodeSize"]]).round(2)

        self.nodesAndWeights = nodeSizes

        return

    def getEdgesDf(self, df:pd.DataFrame = None)->pd.DataFrame:
        """
        :param df:subset of data belonging to a cluster
        :return: df as a nodal graph with nodeIdA and nodeIdB with edge_weights
        """

        if df is None and self.clusterTopDf is not None:
            df = self.clusterTopDf
        elif df is None:
            print("")
            NoClusterDfError("No dataframe for cluster defined. "
                             "Call methods getClusterTopData() to create the dataframe first")
        else:
            print("dataframe passed to function")


        corpus = df["Keywords"].tolist()
        ids = df["RecipeId"].tolist()
        ids = [int(id_) for id_ in ids]

        #create the sparse matrix
        vectorizer = TfidfVectorizer(stop_words={'english'},use_idf=True)
        vectorizorModel = vectorizer.fit(corpus)
        X = vectorizorModel.transform(corpus) # top selected

        #multiply to get the correlations
        nodalSparseGraph = X @ X.T
        nodalSparseGraph = np.array(nodalSparseGraph.todense())

        #extract only lower triangle to reduce repeating endges
        nodalGraph = np.tril(nodalSparseGraph,k=-1) #sets diag =0 also
        shape = nodalGraph.shape

        coordinates = {"recipeIdA": [], "recipeIdB": [], "edge_weight": []}
        for row in range(shape[0]):
            for col in range(shape[1]):
                weight = nodalGraph[row][col]
                if weight > 0:
                    coordinates["recipeIdA"].append(row)
                    coordinates["recipeIdB"].append(col)
                    coordinates["edge_weight"].append(weight)


        #place values into pandas
        edgesDf = pd.DataFrame(coordinates)

        #normalize weights from 0 to 1
        scaler = MinMaxScaler()
        edgesDf["edge_weight"] = scaler.fit_transform(edgesDf[["edge_weight"]])
        edgesDf["edge_weight"] = edgesDf["edge_weight"].round(2)
        #reformat to pandas and assign back the recipe ids
        edgesDf["recipeIdA"] = edgesDf.recipeIdA.apply(lambda x: ids[x])
        edgesDf["recipeIdB"] = edgesDf.recipeIdB.apply(lambda x: ids[x])

        self.edgesDf = edgesDf.copy() # save results to the class attribute

        return self.edgesDf

    def topRecipeData(self)->Tuple[pd.DataFrame,pd.DataFrame,int]:

        model = self.pipelineMode

        newRecipe = self.userIngredientInput
        returnRecipeCount = self.returnRecipeCount

        clusterNr = self.predictCluster(model, newRecipe)

        self.getClusterData(clusterNr)

        dfTop = self.getClusterTopData(returnRecipeCount)
        self.setNodeSizes(dfTop)
        edgesDf = self.getEdgesDf(dfTop)


        return dfTop,edgesDf,clusterNr

    def updateRecipeData(self,returnRecipeCount:int = None)->Tuple[pd.DataFrame,pd.DataFrame]:
        if returnRecipeCount is None and self.returnRecipeCount is not None:
            returnRecipeCount = self.returnRecipeCount
        elif returnRecipeCount is None and self.returnRecipeCount is None:
            raise NoClusterDfError("A number for recipe count wasn't defined")


        dfTop = self.getClusterTopData(returnRecipeCount)
        self.setNodeSizes(dfTop)
        edgesDf = self.getEdgesDf(dfTop)

        return dfTop,edgesDf

class NoClusterDfError(Exception):
    """
    class to handle custom exceptions
    """
    pass

