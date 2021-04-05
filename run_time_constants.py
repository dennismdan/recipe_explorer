import os
sourceDir = os.path.dirname(__file__)


#Directory Paths
ui:str = os.path.join(os.path.join(sourceDir,"src"),"ui")
backend:str = os.path.join(os.path.join(sourceDir,"src"),"backend")
models:str = os.path.join(sourceDir,r"models")
data:str = os.path.join(os.path.dirname(sourceDir),"data")
print("data file path: ",data)

#Other Runtime Constants
pipelineFileName = "pipeline_k150.sav"
fullDataFileName = "recipe_clusters.csv"

pipelineFilePath = os.path.join(models,"pipeline_k150.sav")

#------------> place the data file right outside root directory so the structure looks like this:
# -somefolder
#  |___cse6242_project
#      |______all project files (src...)
#  |___data
#      |______ recipe_clusters.csv

fullDataFilePath = os.path.join(data,"recipe_clusters.csv")

#fullDataFilePath = os.path.join(data,"recipe_clusters.csv")