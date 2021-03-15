import streamlit as st
import pandas as pd
import numpy as np
import time
import json

from SPARQLWrapper import SPARQLWrapper, JSON
from streamlit_agraph import agraph, Node, Edge, TripleStore, Config


st.title("Food Explorer: A CSE6242 Project")


testDf = pd.DataFrame({"a":[1,2,3,4,5],
                       "b":[11,12,13,14,15]})


nodes = []
edges = []
nodeSize = 500

nodes.extend([Node(id="Spicy Potatoes",label="Spicy Potatoes",size=nodeSize),
             Node(id="Spicy Chicken",label="Spicy Chicken",size=nodeSize),
             Node(id="Pork Belly",label="Pork Belly",size=nodeSize),
             Node(id="Jamaican Fish",label="Jamaican Fish",size=nodeSize),
             Node(id="Pickles",label="Pickles",size=nodeSize)])


edges.extend([Edge(source="Spicy Potatoes",label ="spicy food", target="Spicy Chicken"),
              Edge(source="Jamaican Fish",label ="spicy food", target="Spicy Chicken"),
              Edge(source="Jamaican Fish",label ="spicy food", target="Spicy Potatoes"),
              Edge(source="Jamaican Fish", label="meats", target="Spicy Chicken"),
              Edge(source="Spicy Chicken", label="meats", target="Pork Belly"),
              Edge(source="Jamaican Fish", label="meats", target="Pork Belly"),
              Edge(source="Pickles", label="non-meats", target="Spicy Potatoes"),
              ])

def app():
  st.title("Graph Example")
  sidebar = st.sidebar
  sidebar.title("Filter By Category")
  display_category = sidebar.selectbox("Query Type: ",index=0, options = ["all","spicy foods","meats","non-meats"]) # could add more stuff here later on or add other endpoints in the sidebar.

  config = Config(height=300,
                  width=700,
                  nodeHighlightBehavior=True,
                  highlightColor="#F7A7A6",
                  directed=True,
                  collapsible=True,
                  node={'labelProperty': 'label'},
                  link={'labelProperty': 'label', 'renderLabel': True}
                  )


  st.text(display_category)

  if display_category=="all":
      viewEdges = edges
  else:
      viewEdges = [edge for edge in edges if edge.label==display_category]

  return_value = agraph(nodes=nodes,
                      edges=viewEdges,
                      config=config)



  data_load_state = st.text("Loading Data...")

  st.subheader("Reviewing the Data")
  st.write(testDf)

  st.subheader("Graphing the Data")
  st.bar_chart(testDf)

  checkBox = st.checkbox("Label",value=True,key="on")

  if checkBox == True:
      st.subheader("Displaying text because checkbox is true")
  userInput = st.text_input("input keyword ingredients","potatoes, tomatoes")

  st.text("User selected the following ingredients: "+userInput)

if __name__=='__main__':
    app()
