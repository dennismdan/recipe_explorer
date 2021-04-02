import streamlit as st

#from SPARQLWrapper import SPARQLWrapper, JSON
from streamlit_agraph import agraph, Node, Edge, TripleStore, Config
#from pyvis.network import Network

from ..backend.cluster_api import ClusterAPI

topNrRecipes = 10

def app():
    userIngredientsInput = None
    userTopNRecipes = None

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
    sidebar.title("Enter ingredients or any food related words")
    sidebar.text("The more detail you add to the\ningredients the better your\nresuls will be")

    # Dennis note: lets keep only one box for user input to simplify implementations, we can add the second one later
    initialIngridientsInput = sidebar.text_input(label="Enter search terms")
    initialRecipeCountInput = sidebar.selectbox(label="Choose number of recipes to return", options=[10,20,30,40,50], index=1)

    runButton = sidebar.button("Run")

    status_text = sidebar.text("enter inputs and run")

    if runButton:
        print(userIngredientsInput)
        recipeUpdate:bool = None
        recipeCountUpdate:bool = None

        #check if only the nr of clusters was updated
        if userIngredientsInput != initialIngridientsInput:
            userIngredientsInput = initialIngridientsInput
            recipeUpdate = True
        else:
            recipeUpdate = False

        if userTopNRecipes != initialRecipeCountInput:
            userTopNRecipes = initialRecipeCountInput
            recipeCountUpdate = True
        else:
            recipeCountUpdate = False

        # run scenarios
        if recipeUpdate:
            result = composeClusterApi(userIngredientsInput, userTopNRecipes)
            st.write(result)

            if result is None:
                status_text.text("Did not find a user input, please add ingredients")
            else:
                clusterApi = result #contains RecipeDf, and edgesDf
                status_text.text("Perfect, results are displayed in the graph")
                #sidebar.success('Perfect, results are displayed in the graph')

                updateGraph(clusterApi,middle)

        if not recipeUpdate and recipeCountUpdate:
            clusterApi = clusterApi.updateRecipeData(userTopNRecipes)
            updateGraph(clusterApi, middle)
            status_text.text("Updated to only show top ",str(userTopNRecipes)," recipes")
            print("unly updating top N")

        if not recipeCountUpdate and not recipeCountUpdate:
            status_text.text("No changes to the input found")


    st.text("Showing recipes based on the following ingredients: {}".format(userIngredientsInput))




def updateGraph(clusterApi,middle):
    recipeDf = clusterApi.clusterTopDf
    st.write(recipeDf)
    edgesDf = clusterApi.edgesTopDf
    st.write(edgesDf)
    nodesAndWeights = clusterApi.nodesAndWeights
    st.write(nodesAndWeights)

    nodes, edges = getNodesEdges(recipeDf, edgesDf, nodesAndWeights)
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
        return None

    return clusterApi

def getNodesEdges(recipeDf,edgesDf,nodeList):
    nodes = []
    edges = []
    existingEdges =[]
    nodeList["nodeSize"] = ((nodeList["nodeSize"] - nodeList["nodeSize"].min()) / (nodeList["nodeSize"].max() - nodeList["nodeSize"].min())) * 2000
    for index,row in nodeList.iterrows():

        id = row["RecipeId"]
        nodeSize = row["nodeSize"]
        label = recipeDf[recipeDf.RecipeId == id].Name.tolist()[0]

        nodes.append(Node(id = int(id), label = label, size = int(nodeSize)))
    edgesDf["edge_weight"] = ((edgesDf["edge_weight"] - edgesDf["edge_weight"].min()) / (edgesDf["edge_weight"].max() - edgesDf["edge_weight"].min())) * 5
    for index, row in edgesDf.iterrows():
        if [int(row["recipeIdB"]), int(row["recipeIdA"])] not in existingEdges:
            existingEdges.append([int(row["recipeIdA"]),int(row["recipeIdB"])])
            edges.append(Edge(source=int(row["recipeIdA"]), target=int(row["recipeIdB"]),strokeWidth = int(row["edge_weight"]), type="CURVE_SMOOTH"))

    return nodes,edges



if __name__=='__main__':
    app()
