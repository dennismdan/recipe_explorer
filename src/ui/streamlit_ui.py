import streamlit as st

#from SPARQLWrapper import SPARQLWrapper, JSON
#from streamlit_agraph import agraph, Node, Edge, TripleStore, Config
from pyvis.network import Network
import streamlit.components.v1 as components

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
    st.text("In the left sidebar enter keywords to search for similar recipes.\nNext select the number of recipes you would like returned, and click Run.\n"
            "A network of recipes will appear below based on your search criteria, bon appetite!")
    sidebar = st.sidebar
    middle, rsidebar = st.beta_columns([3, 1])
    sidebar.title("Enter ingredients or any food related words")
    sidebar.text("The more detail you add to the\ningredients the better your\nresuls will be")

    # Dennis note: lets keep only one box for user input to simplify implementations, we can add the second one later
    userIngredientsInput = sidebar.text_input(label="Enter search terms")
    #st.text("\nShowing recipes based on the following ingredients: {}".format(userIngredientsInput))
    userTopNRecipes = sidebar.selectbox(label="Choose number of recipes to return", options=[10,20,30,40,50], index=1)

    runButton = sidebar.button("Run")

    status_text = sidebar.text("enter inputs and run")

    if runButton:
        print(userIngredientsInput)

        result = composeClusterApi(userIngredientsInput, userTopNRecipes)
        st.write(result)

        if result is None:
            status_text.text("Did not find a user input, please add ingredients")
        else:
            clusterApi = result #contains RecipeDf, and edgesDf
            status_text.text("Perfect, results are displayed\nin the graph")
            updateGraph(clusterApi,middle)





def updateGraph(clusterApi,middle):

    recipeDf = clusterApi.clusterTopDf
    st.write(recipeDf)
    edgesDf = clusterApi.edgesTopDf
    st.write(edgesDf)
    nodesAndWeights = clusterApi.nodesAndWeights
    st.write(nodesAndWeights)

    #nodes, edges = getNodesEdges(recipeDf, edgesDf, nodesAndWeights)
    network = getNodesEdges(recipeDf, edgesDf, nodesAndWeights)
    #generateGraph(nodes,edges,middle)
    generateGraph(network, middle)
    middle.text("Larger nodes represent recipes that best match your search.\n"
                "The edge thickness represents similarity between recipes.")

#def generateGraph(nodes,edges,middle):
def generateGraph(network, middle):
    # set network configuration
    # config = Config(height=300,
    #                 width=900,
    #                 nodeHighlightBehavior=True,
    #                 highlightColor="#F7A7A6",
    #                 directed=False,
    #                 collapsible=True,
    #                 node={'labelProperty': 'label'},
    #                 link={'labelProperty': 'label', 'renderLabel': False}
    #                 )


    # net.add_edges(edges)
    network.show('recipeNetwork.html')

    # add network to middle column of streamlit canvas
    with middle:

        # return_value = agraph(nodes=nodes,
        #                       edges=edges,
        #                       config=config)
        HtmlFile = open('recipeNetwork.html', 'r', encoding='utf-8')
        source_code = HtmlFile.read()
        components.html(source_code, height=400, width=900)

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
    net = Network(height="300px",
                  width="90%",
                  directed=False,
                  notebook=True,
                  bgcolor=None,
                  font_color='black',
                  layout="black")
    # nodes = []
    # edges = []
    net.set_options('''
    var options = {"physics":{
                    "barnesHut": {
                        "gravitationalConstanst":-8000,
                        "centralGravity": 20,
                        "springLength": 1000,
                        "springConstant":0.545,
                        "damping": 0.1,
                        "avoidOverlap":0.9},
                        "maxVelocity":10,
                        "minVelocity":0.75}
                        }''')
    #net.toggle_physics(True)
    #net.repulsion(node_distance=100, central_gravity=0.2,spring_length=200,spring_strength=0.05,damping=0.09)
    #net.set_edge_smooth('dynamic')
    existingEdges =[]
    nodeList["nodeSize"] = ((nodeList["nodeSize"] - nodeList["nodeSize"].min()) / (nodeList["nodeSize"].max() - nodeList["nodeSize"].min())) * 100 #2000
    for index,row in nodeList.iterrows():

        id = row["RecipeId"]
        nodeSize = row["nodeSize"]
        label = recipeDf[recipeDf.RecipeId == id].Name.tolist()[0]

        #nodes.append(Node(id = int(id), label = label, size = int(nodeSize)))
        net.add_node(int(id), label=label, size=int(nodeSize), font='20px arial black', title='https://www.food.com/recipe/{}'.format(int(id)))
    edgesDf["edge_weight"] = ((edgesDf["edge_weight"] - edgesDf["edge_weight"].min()) / (edgesDf["edge_weight"].max() - edgesDf["edge_weight"].min())) * 5
    for index, row in edgesDf.iterrows():
        if [int(row["recipeIdB"]), int(row["recipeIdA"])] not in existingEdges:
            existingEdges.append([int(row["recipeIdA"]),int(row["recipeIdB"])])
            #edges.append(Edge(source=int(row["recipeIdA"]), target=int(row["recipeIdB"]),strokeWidth = int(row["edge_weight"]), type="CURVE_SMOOTH"))
            net.add_edge(int(row["recipeIdA"]), int(row["recipeIdB"]))# weight=int(row["edge_weight"])
    #return nodes,edges
    return net



if __name__=='__main__':
    app()
