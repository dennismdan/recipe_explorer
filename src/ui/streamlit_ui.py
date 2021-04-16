import streamlit as st
import streamlit.components.v1 as components
import SessionState
import tkinter
#from SPARQLWrapper import SPARQLWrapper, JSON
from streamlit_agraph import agraph, Node, Edge, TripleStore, Config
from pyvis.network import Network

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
    
    #Styling
    st.markdown('<style>.stButton>button {color: black; border-radius: 4px; height: 26px; width: 100%; box-shadow: 0 8px 16px 0 rgba(0,0,0,0.2), 0 6px 20px 0 rgba(0,0,0,0.19)}</style>', unsafe_allow_html=True)
   
    # Set title and user input elements
    st.title("Recipe Explorer Network")
    sidebar = st.sidebar
    sidebar.title("Enter ingredients or any food related words")
    sidebar.text("The more detail you add to the\ningredients the better your\nresuls will be")
    #button = st.empty()
    #Set state
    #session_state = SessionState()
    ss = SessionState
    session_state = ss.get(name='', Buttonclicked=False, button='')
   
    # Dennis note: lets keep only one box for user input to simplify implementations, we can add the second one later
    userIngredientsInput = sidebar.text_input(label="Enter search terms", key="init")
    print('seesion state:' + session_state.name)
    print('session run button:' + str(session_state.Buttonclicked))
    userTopNRecipes = sidebar.selectbox(label="Choose number of recipes to return", options=[3,5,10,15], index=1)
    runButton = sidebar.button("Run")
    status_text = sidebar.text("enter inputs and run")
    
    if session_state.Buttonclicked == False:
        if runButton:
            result = composeClusterApi(userIngredientsInput, userTopNRecipes)
            session_state.Buttonclicked = True
            if result is None:
                status_text.text("Did not find a user input, please add ingredients")
            else:
                clusterApi = result
                session_state.name = 'onion'    
                status_text.text("Perfect, results are displayed in the graph")
                updateGraph(clusterApi,session_state, sidebar)
    else:
        print('start')
        print(session_state.name)
        print(session_state.button)
        #print('cache test:' + str(returnbutton))            

        if session_state.button:
            result = composeClusterApi('onion', userTopNRecipes)
            print('seesion state:' + session_state.name)
            print('run button:' + str(session_state.Buttonclicked))
            print('herein the loop')
                #session_state.Buttonclicked = True
                #ss.name = 'onions'
            if result is None:
                status_text.text("Did not find a user input, please add ingredients")
            else:
                clusterApi = result 
                status_text.text("Perfect, results are displayed in the graph")
                updateGraph(clusterApi,session_state, sidebar)
         

               
    st.markdown("In the left sidebar enter keywords to search for similar recipes.\nNext select the number of recipes you would like returned, and click Run.\n"
            "A network of recipes to explore will appear below. The returned recipes are\nselected from a dataset of over 500,000 recipes. "
            "The recipes have been\nseparated into clusters based on common ingredients. Recipes are selected\nfrom the cluster most "
            "representative of your search terms, bon appetite!")
    st.text("Showing recipes based on the following ingredients: {}".format(session_state.name))
    

def updateGraph(clusterApi, session_state, sidebar):
    recipeDf = clusterApi.clusterTopDf
    edgesDf = clusterApi.edgesDf
    buttons = []

    nodesAndWeights = clusterApi.nodesAndWeights
   
    nodes, edges, urlList  = getNodesEdges(recipeDf, edgesDf, nodesAndWeights)
 
    generateGraph(nodes,edges)
    
    #session_state.name = 'onions' #recipeDf[recipeDf.RecipeId == nodes.id].Name.tolist()[0]
    #session_state.button = st.radio(label = "Test", options = ('Chicken', 'Beef'))
    col1, col2 = st.beta_columns((3, 2)) #columns for results list
    with col1:    
        for i in range(len(urlList)):
            col1.write(urlList[i])
    with col2: 
            for i in range(len(nodes)):
                button = buttons.append(st.button(label = 'Explore Similar Options', key=str(i)))
            #session_state.button = st.radio(label = "Explore Similar Recipes", options = buttons)
            #session_state.button = test
            #st.write('You clicked: ' + str(test))
                for i, button in enumerate(buttons):
                    if button:
                        session_state.name = str(i)
                        #sidebar.text_input(label="Enter search terms", value=str(i))
                        #userIngredientsInput = st.empty()
                    #st.empty()                

def generateGraph(nodes,edges): #,middle):
    # set network configuration
    config = Config(height=500,
                    width=800,
                    nodeHighlightBehavior=True,
                    highlightColor="#d9a0d7",
                    directed=False,
                    collapsible=True,
                    node={'labelProperty': 'label'},
                    link={'labelProperty': 'label', 'renderLabel': False}
                    )
    # add network to middle column of streamlit canvas
 
    return_value = agraph(nodes=nodes,
                              edges=edges,
                              config=config)

def composeClusterApi(userIngredientsInput, topNrRecipes):

    if (userIngredientsInput is None) or (userIngredientsInput == ""):
        return None

    try:
        clusterApi = ClusterAPI(stringInput=userIngredientsInput,
                                topNrRecipes=topNrRecipes)

        clusterApi.topRecipeData()
    except:
        print('Cluster api failed')
        raise
        st.stop()
        st.warning('An error has occured. Please try again.')
        return None

    return clusterApi

def getNodesEdges(recipeDf,edgesDf,nodeList):
    nodes = []
    edges = []
    existingEdges =[]
    urlList = []
    nodeList["nodeSize"] = ((nodeList["nodeSize"] - nodeList["nodeSize"].min()) / (nodeList["nodeSize"].max() - nodeList["nodeSize"].min())) * 1500
    nodeList.sort_values(by="nodeSize", ascending=False, inplace=True)
    nodeList.reset_index(drop=True, inplace=True)
    for index,row in nodeList.iterrows():

        id = int(row["RecipeId"])
        nodeSize = row["nodeSize"]
        label = recipeDf[recipeDf.RecipeId == id].Name.tolist()[0]
        url = "https://www.food.com/recipe/{}".format(str(id))
        link = '[{}]({})'.format(label, url)
  
        label = label.replace('&quot;', '"')
        urlList.append(link)
        try:
            nodes.append(Node(id = int(id), label = label.replace('&amp;', '&'), size = int(nodeSize)))
        except:
            print('Null value returned')
            raise
            st.stop()    
            st.warning('An error has occured. Please try again.')
    edgesDf["edge_weight"] = 1#((edgesDf["edge_weight"] - edgesDf["edge_weight"].min()) / (edgesDf["edge_weight"].max() - edgesDf["edge_weight"].min())) * 5
    for index, row in edgesDf.iterrows():
        if [int(row["recipeIdB"]), int(row["recipeIdA"])] not in existingEdges:
            existingEdges.append([int(row["recipeIdA"]),int(row["recipeIdB"])])
            edges.append(Edge(source=int(row["recipeIdA"]), target=int(row["recipeIdB"]),strokeWidth = int(row["edge_weight"]), type="STRAIGHT"))

    return nodes,edges, urlList



if __name__=='__main__':
    app()