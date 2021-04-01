import streamlit as st
import pandas as pd
import sklearn
import numpy as np
import time
import json
import numpy as np

#from SPARQLWrapper import SPARQLWrapper, JSON
from streamlit_agraph import agraph, Node, Edge, TripleStore, Config
#from pyvis.network import Network

from run_time_constants import testDataPath
from ..backend.cluster_api import ClusterAPI

topNrRecipes = 10

def app():
    #TODO: Node interaction (click node -> link with some recipe details populates the bottom of the page ?)
    #TODO: Arrange windows:
    #TODO: initial nodegraph... none - just text instructing user to enter recipes
    # 1 - left: user input interface,
    # 2 - center: nodal graph center,
    # 3 - right: recipe list/ingridients
    # 4 - bottom link to the page with the recipe ?
    # 5 - count of outputs results
    # 6 - background display and clean vis

    # Set title and user input elements
    st.title("Recipe Recommender Network")
    sidebar = st.sidebar
    middle, rsidebar = st.beta_columns([3, 1])
    sidebar.title("Enter ingridients or any food related words")
    sidebar.text("The more detail you add to the ingredients the better your resuls will be")

    # Dennis note: lets keep only one box for user input to simplify implementations, we can add the second one later
    userIngredientsInput = sidebar.text_input()

    #TODO: make second box actionable: userInput = sidebar.text_input("Input recipe to use as cluster seed: ")

    doneButton = sidebar.button("Run")

    if doneButton:

        result = composeClusterApi(userIngredientsInput)

        if not result:
            sidebar.write("Did not find a user input, please add ingredients")
        else:
            clusterApi = result #contains RecipeDf, and edgesDf
            sidebar.success('Perfect, results are displayed in the graph')

            updateGraph(clusterApi,middle)

    # create empty lists for holding nodes and edges for network
    #net = Network() # place holder for transitioning to pyvis
    nodes = []
    edges = []
    nodeSize = 500

    # Bring in the initial data
    tmp = pd.read_csv(testDataPath) # Here is where we would access the data from the backend
    print('length before filter: ', len(tmp))

    # filter data for only recipes that contain the user inputs
    if userIngredientsInput != "":
      ingredients = userIngredientsInput.split(',')
      ingredients = [i.strip() for i in ingredients]
      contains = [tmp["RecipeIngredientParts"].str.contains(i) for i in ingredients]
      #print(ingredients)
      tmp = tmp[np.all(contains, axis=0)]
      print('length of filtered: ', len(tmp))


    if len(tmp) != 0:
      edgeList = []

      ### Used for loading the data directly from the dictionary output from Orion's clustering script
      # for i in range(0, len(tmp["c1"]["nodes"])):
      #     nodes.extend([Node(id=int(tmp["c1"]["nodes"].iloc[i]['RecipeId']), label=tmp["c1"]["nodes"].iloc[i]["Name"],
      #                        size=nodeSize)])
      #     for j in range(0, len(tmp["c1"]["nodes"])):
      #         if tmp["c1"]["nodes"].iloc[i]['RecipeId'] != tmp["c1"]["nodes"].iloc[j]['RecipeId'] and int(tmp["c1"]["nodes"].iloc[i]["Ingredient Difference"]) == int(tmp["c1"]["nodes"].iloc[j]["Ingredient Difference"]) \
      #                 and [int(tmp["c1"]["nodes"].iloc[j]['RecipeId']),int(tmp["c1"]["nodes"].iloc[i]['RecipeId'])] not in edgeList:
      #             edgeList.append([int(tmp["c1"]["nodes"].iloc[i]['RecipeId']),int(tmp["c1"]["nodes"].iloc[j]['RecipeId'])])
      #             edges.extend([Edge(source=int(tmp["c1"]["nodes"].iloc[i]['RecipeId']), label=int(tmp["c1"]["nodes"].iloc[j]["Ingredient Difference"]),
      #                                target=int(tmp["c1"]["nodes"].iloc[j]["RecipeId"]), type="CURVE_SMOOTH")])
      for i in range(0, len(tmp["nodes"])):
          nodes.extend([Node(id=int(tmp.iloc[i]['RecipeId']), label=tmp.iloc[i]["Name"],
                             size=nodeSize)])
          #net.add_node(n_id=int(tmp.iloc[i]['RecipeId']), value=nodeSize, label=tmp.iloc[i]["Name"]) # place holder for transitioning to pyvis
          for j in range(0, len(tmp["nodes"])):
              if tmp.iloc[i]['RecipeId'] != tmp.iloc[j]['RecipeId'] and int(tmp.iloc[i]["Ingredient Difference"]) == int(tmp.iloc[j]["Ingredient Difference"]) \
                      and [int(tmp.iloc[j]['RecipeId']),int(tmp.iloc[i]['RecipeId'])] not in edgeList:
                  edgeList.append([int(tmp.iloc[i]['RecipeId']),int(tmp.iloc[j]['RecipeId'])])
                  edges.extend([Edge(source=int(tmp.iloc[i]['RecipeId']), label=int(tmp.iloc[j]["Ingredient Difference"]),
                                     target=int(tmp.iloc[j]["RecipeId"]), type="CURVE_SMOOTH")])
                  #net.add_edge(int(tmp.iloc[i]['RecipeId']),int(tmp.iloc[j]["RecipeId"]),title=int(tmp.iloc[j]["Ingredient Difference"])) # # place holder for transitioning to pyvis


      # diffList = [str(i) for i in set(tmp["c1"]["nodes"]["Ingredient Difference"])]
      # diffList.append('All')
      # diffList.sort(reverse=True)
      # display_category = sidebar.selectbox("Ingredient difference: ",index=0, options = diffList) # could add more stuff here later on or add other endpoints in the sidebar.
      # if display_category == "all":
      viewEdges = edges
      # else:
      #     viewEdges = [edge for edge in edges if edge.label == display_category]
      #mealType = sidebar.selectbox("Meal Type: ", index=0, options = ["Breakfast", "Lunch", "Dinner"]) # Just a place holder could be 'soup', 'salad', or 'italian', 'indian', etc

      # set network configuration
      config = Config(height=500,
                      width=700,
                      nodeHighlightBehavior=True,
                      highlightColor="#F7A7A6",
                      directed=False,
                      collapsible=True,
                      node={'labelProperty': 'label'},
                      link={'labelProperty': 'label', 'renderLabel': False}
                      )
      # add network to middle column of streamlit canvas
      with middle:
          #st.text("Displaying {} cuisine types".format(display_category))
          return_value = agraph(nodes=nodes,
                                 edges=viewEdges,
                                 config=config)
            #net.show('testgraph.html') # place holder for transitioning to pyvis

    st.text("Showing recipes based on the following ingredients: {}".format(userIngredientsInput))

def updateGraph(clusterApi,middle):
    recipeDf = clusterApi.clusterTopDf
    edgesDf = clusterApi.edgesTopDf
    nodeList = clusterApi.nodeList

    nodes, edges = getNodesEdges(recipeDf, edgesDf, nodeList)
    generateGraph(nodes,edges,middle)

def generateGraph(nodes,edges,middle):
    # set network configuration
    config = Config(height=500,
                    width=700,
                    nodeHighlightBehavior=True,
                    highlightColor="#F7A7A6",
                    directed=False,
                    collapsible=True,
                    node={'labelProperty': 'label'},
                    link={'labelProperty': 'label', 'renderLabel': False}
                    )
    # add network to middle column of streamlit canvas
    with middle:
        # st.text("Displaying {} cuisine types".format(display_category))
        return_value = agraph(nodes=nodes,
                              edges=edges,
                              config=config)

def composeClusterApi(userIngredientsInput):
    if (userIngredientsInput is None) or (userIngredientsInput == ""):
        return False

    try:
        clusterApi = ClusterAPI(stringInput=userIngredientsInput,
                                topNrRecipes=topNrRecipes)
        clusterApi.topRecipeData()
    except:
        return False

    return clusterApi

def getNodesEdges(recipeDf,edgesDf,nodeList):
    nodes = []
    edges = []

    for index,row in nodeList.iterrows():
        #TODO: normalize nodeSize
        id = row["RecipeId"]
        nodeSize = row["nodeSize"]
        label = recipeDf[recipeDf.RecipeId == id].Name.tolist()[0]

        nodes.append(Node(id = id, label = label, size = nodeSize))

    for index, row in edgesDf.iterrows():
        edges.append(Edge(source=row["recipeIdA"], target=row["recipeIdB"],strokeWidth = row["edge_weight"], type="CURVE_SMOOTH"))

    return nodes,edges



if __name__=='__main__':
    app()
