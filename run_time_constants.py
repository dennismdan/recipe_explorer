import os
#TODO: all paths will need to be converted to linux once we deploy

sourceDir = os.path.dirname(__file__)


#Directory Paths
ui:str = os.path.join(sourceDir,r"src\ui")
backend:str = os.path.join(sourceDir,r"src\backend")
data:str = os.path.join(sourceDir,r"src\data")
models:str = os.path.join(sourceDir,r"models")


#Other Runtime Constants
pipelineFileName = "pipeline_k150.sav"
fullDataFileName = "recipe_clusters.csv"

pipelineFilePath = os.path.join(models,"pipeline_k150.sav")

#------------> your local path to file /recipe_clusters.csv
fullDataFilePath = r"C:\Users\Dennis\Desktop\GT - OMS Analytics\CSE6242\project\src\data\recipe_clusters.csv"

#fullDataFilePath = os.path.join(data,"recipe_clusters.csv")