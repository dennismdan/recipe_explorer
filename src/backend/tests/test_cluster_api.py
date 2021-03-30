import pytest
from ..cluster_api import ClusterAPI
from sklearn.pipeline import Pipeline
import pandas as pd

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
    clusterDf = cluster_api.getClusterData()
    assert isinstance(clusterDf,pd.DataFrame)
    assert len(clusterDf)==topNrRecipes
