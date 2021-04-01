import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import time
import json
import numpy as np

#from SPARQLWrapper import SPARQLWrapper, JSON
from streamlit_agraph import agraph, Node, Edge, TripleStore, Config
#from pyvis.network import Network
from IPython.core.display import display, HTML
from ..backend.get_cluster import ClusterData

def app():

  # Set title and user input elements
  st.title("Recipe Recommender Network")
  sidebar = st.sidebar
  middle, rsidebar = st.beta_columns([3, 1])
  sidebar.title("Choose meal type and ingredients")
  userIngredients = sidebar.text_input("Input ingredients that should be included in returned recipes:")
  userRecipesNum = sidebar.selectbox("Select number of recipes to return: ", options=[10,20,30,40,50], index=0)

  # create empty lists for holding nodes and edges for network
  #net = Network() # place holder for transitioning to pyvis
  nodes = []
  edges = []
  nodeSize = 500

  # filter data for only recipes that contain the user inputs
  if userIngredients != "":
      ingredients = userIngredients.split(',')
      ingredients = [i.strip() for i in ingredients]
      # Bring in the initial data
      #tmp = pd.read_csv(r'C:\Users\jdnun\OneDrive\Documents\GT\Spring2021\Project\code\cse6242_project-main\src\cluster_test.csv') # Here is where we would access the data from the backend
      tmp = ClusterData(stringInput= ingredients, topNrRecipes=userRecipesNum)
      print('length before filter: ', len(tmp))
      #contains = [tmp["RecipeIngredientParts"].str.contains(i) for i in ingredients]
      # print(ingredients)
      #tmp = tmp[np.all(contains, axis=0)]
      #print('length of filtered: ', len(tmp))



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
          #net.add_node(int(tmp.iloc[i]['RecipeId']), value=nodeSize, label=tmp.iloc[i]["Name"]) # place holder for transitioning to pyvis
      for i in range(0, len(tmp["nodes"])):
          for j in range(0, len(tmp["nodes"])):
              if tmp.iloc[i]['RecipeId'] != tmp.iloc[j]['RecipeId'] and int(tmp.iloc[i]["Ingredient Difference"]) == int(tmp.iloc[j]["Ingredient Difference"]) \
                      and [int(tmp.iloc[j]['RecipeId']),int(tmp.iloc[i]['RecipeId'])] not in edgeList:
                  edgeList.append([int(tmp.iloc[i]['RecipeId']),int(tmp.iloc[j]['RecipeId'])])
                  edges.extend([Edge(source=int(tmp.iloc[i]['RecipeId']), label=int(tmp.iloc[j]["Ingredient Difference"]),
                                     target=int(tmp.iloc[j]["RecipeId"]), type="CURVE_SMOOTH")])
                  #net.add_edge(int(tmp.iloc[j]["RecipeId"]),int(tmp.iloc[i]['RecipeId']),title=int(tmp.iloc[j]["Ingredient Difference"])) # # place holder for transitioning to pyvis


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
          # HtmlFile = open('C:/Users/jdnun/AppData/Local/Programs/Python/Python37/testgraph.html', 'r', encoding='utf-8')
          # source_code = HtmlFile.read()
          # components.html(source_code, height = 900, width = 1000)
          #net.show('testgraph.html') # place holder for transitioning to pyvis
          #display(HTML('net.html'))






  st.text("Showing recipes based on the following user inputs: {}".format(userIngredients))

if __name__=='__main__':
    app()
