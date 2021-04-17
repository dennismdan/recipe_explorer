import streamlit as st
import streamlit.components.v1 as components
import SessionState

try:
    import streamlit.ReportThread as ReportThread
    from streamlit.server.Server import Server
except Exception:
    # Streamlit >= 0.65.0
    import streamlit.report_thread as ReportThread
    from streamlit.server.server import Server

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

    #Set state
    ss = SessionState
    session_state = ss.get(name='', Buttonclicked=False, button='', recipe_name = '')
    session_state2 = ss.get(name='', Buttonclicked=False, button='', recipe_name = '')
    session_state3 = ss.get(name='', Buttonclicked=False, button='', recipe_name = '')

   
    userIngredientsInput = sidebar.text_input(label="Enter search terms", key="init")

    userTopNRecipes = sidebar.selectbox(label="Choose number of recipes to return", options=[3,5,10,15], index=1)
    runButton = sidebar.button("Run")
    status_text = sidebar.text("enter inputs and run")
    graph = st.beta_columns((5))
    buttons = []
    button = st.empty()
    session_state.button = button
    session_state2.button = button
    session_state3.button = button

    st.markdown("In the left sidebar enter keywords to search for similar recipes.\nNext select the number of recipes you would like returned, and click Run.\n"
            "A network of recipes to explore will appear below. The returned recipes are\nselected from a dataset of over 500,000 recipes. "
            "The recipes have been\nseparated into clusters based on common ingredients. Recipes are selected\nfrom the cluster most "
            "representative of your search terms, bon appetite!")
    
    if (session_state.Buttonclicked == True and runButton == False):
        if session_state.button:
            print('start re-run')
           
            # print(session_state.recipe_name)
            # print('re-run:' + session_state.recipe_name)
            st.text(session_state.recipe_name)
            st.text("Showing recipes based on the following ingredients: {}".format(session_state.name))
            try:
                result = composeClusterApi(session_state.name, userTopNRecipes)
            except Exception:
                st.write('No results Found.')
            if result is None:
                status_text.text("Did not find a user input, please add ingredients")
            else:
                clusterApi = result 
                status_text.text("Perfect, results are displayed in the graph")
                updateGraph(clusterApi,session_state, session_state2, session_state3, sidebar, buttons)

    elif (session_state2.Buttonclicked == True and runButton == False):
        if session_state2.button:
            print('start re-run')

            # print(session_state2.recipe_name)
            # print('re-run:' + session_state2.recipe_name)
            st.text(session_state2.recipe_name)
            st.text("Showing recipes based on the following ingredients: {}".format(session_state2.name))
            try:
                result = composeClusterApi(session_state2.name, userTopNRecipes)
            except Exception:
                st.write('No results Found.')
            if result is None:
                status_text.text("Did not find a user input, please add ingredients")
            else:
                clusterApi = result
                status_text.text("Perfect, results are displayed in the graph")
                updateGraph(clusterApi, session_state, session_state2, session_state3, sidebar, buttons)

    elif (session_state3.Buttonclicked == True and runButton == False):
        if session_state3.button:
            print('start re-run')

            # print(session_state3.recipe_name)
            # print('re-run:' + session_state3.recipe_name)
            st.text(session_state3.recipe_name)
            st.text("Showing recipes based on the following ingredients: {}".format(session_state3.name))
            try:
                result = composeClusterApi(session_state3.name, userTopNRecipes)
            except Exception:
                st.write('No results Found.')
            if result is None:
                status_text.text("Did not find a user input, please add ingredients")
            else:
                clusterApi = result
                status_text.text("Perfect, results are displayed in the graph")
                updateGraph(clusterApi, session_state, session_state2, session_state3, sidebar, buttons)

    if runButton:
        st.text("Showing recipes based on the following ingredients: {}".format(userIngredientsInput))
        result = composeClusterApi(userIngredientsInput, userTopNRecipes)
        session_state.Buttonclicked = True
        session_state2.Buttonclicked = True
        session_state3.Buttonclicked = True
        if result is None:
            status_text.text("Did not find a user input, please add ingredients")
        else:
            clusterApi = result
                    #session_state.name = 'onion'    
            status_text.text("Perfect, results are displayed in the graph")
            updateGraph(clusterApi,session_state, session_state2, session_state3, sidebar, buttons)
                


def updateGraph(clusterApi, session_state, session_state2, session_state3, sidebar, button):
    recipeDf = clusterApi.clusterTopDf
    edgesDf = clusterApi.edgesDf

    nodesAndWeights = clusterApi.nodesAndWeights

    nodes, edges, urlList, orderedNode  = getNodesEdges(recipeDf, edgesDf, nodesAndWeights)
 
    generateGraph(nodes,edges)

    col1, col2 = st.beta_columns((3, 3)) #columns for results list
    col1.write('Click a link below to go to recipe')
    with col1:
        for i in range(len(urlList)):
            col1.write(urlList[i])
    with col2:
        col2.write('Click a button below to explore similar recipes')
        session_state.recipe_name = recipeDf[recipeDf.RecipeId == orderedNode[0][0]].Name.tolist()[0]
        session_state.name = recipeDf[recipeDf.RecipeId == orderedNode[0][0]].RecipeIngredientParts.tolist()[0]
        session_state.button = col2.button("Explore Options Similar to the Top Result", key=1)#the Top Result
        session_state2.recipe_name = recipeDf[recipeDf.RecipeId == orderedNode[1][0]].Name.tolist()[0]
        session_state2.name = recipeDf[recipeDf.RecipeId == orderedNode[1][0]].RecipeIngredientParts.tolist()[0]
        session_state2.button = col2.button("Explore Options Similiar to the 2nd Result", key=2)
        session_state3.recipe_name = recipeDf[recipeDf.RecipeId == orderedNode[2][0]].Name.tolist()[0]
        session_state3.name = recipeDf[recipeDf.RecipeId == orderedNode[2][0]].RecipeIngredientParts.tolist()[0]
        session_state3.button = col2.button("Explore Options Similar to the 3rd Result", key=3)

            
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
    orderedNode = []
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
        orderedNode.append((id, nodeSize))
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
        
    return nodes,edges, urlList, orderedNode



if __name__=='__main__':
    app()