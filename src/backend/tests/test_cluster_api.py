import pytest
from ..cluster_api import ClusterAPI
from sklearn.pipeline import Pipeline
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer

userInputString = "pasta, pizza, tomatoes, basil"
topNrRecipes = 10
cluster_api = ClusterAPI(userInputString,topNrRecipes)

def test_cluster_api_class():
     #initiating the api test
    cluster_api = ClusterAPI(userInputString,topNrRecipes)
    assert isinstance(cluster_api,ClusterAPI)

def test_getModel():
    model = cluster_api.getModel()
    assert isinstance(model,Pipeline)

def test_cleanUserInput():
    outputString = cluster_api.cleanUserInput(userInputString)
    assert isinstance(outputString,list)
    assert isinstance(outputString[0],str)

def test_predictCluster():
    clusterNr = cluster_api.predictCluster()
    assert isinstance(clusterNr,int)

def test_getClusterData():
    #TODO: assert that the class attribute was create self.clusterDf
    clusterDf = cluster_api.getClusterData()
    assert isinstance(clusterDf,pd.DataFrame)


def test_getEdgesDf():
    corpus = ["one two three four five", "one two nine four seven", "ten two eleven four five"]
    ids = [11,15,21]
    df = pd.DataFrame({"RecipeIngredientParts":corpus,"RecipeId":ids})

    nodeGraph = cluster_api.getEdgesDf(df)

    assert isinstance(nodeGraph,pd.DataFrame)
    assert len(nodeGraph) ==3
    assert nodeGraph.loc[0,"edge_weight"]==1


def test_getClusterTopData():

    df = cluster_api.getClusterData()
    print(type(cluster_api.clusterDf))
    edgesDf = cluster_api.getEdgesDf()
    topDf = cluster_api.getClusterTopData()

    assert isinstance(topDf,pd.DataFrame)


def test_topRecipeData():
    dfTop,edges,clusterNr = cluster_api.topRecipeData()
    print(clusterNr)
    print(dfTop)
    print(edges)
    assert isinstance(dfTop,pd.DataFrame)
    assert isinstance(edges,pd.DataFrame)
    assert isinstance(clusterNr, int)
    assert len(dfTop)==topNrRecipes
