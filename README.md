
![image](https://user-images.githubusercontent.com/7568793/116161536-e96bff00-a6c1-11eb-8a62-946addbb24c0.png)


## 1. DESCRIPTION 

The recipe explorere presents users a novel way to explore recipes in the following way: 
* Input a set of ingredients into the text box
* Select how many recipes to return
* Click run, and wait for results
* The user can explore the returned recipes by going to the recipe home paige with all the instructions and ingredients.
* Users can then continue their discovery journey by selecting one of the returned recipes as input for new recipe recomendatoins.  


## 2. INSTALLATION

To run this application you will need to things:

#### a. Application files:
Install the application from github and run locally on your machine. Python dependencies are recorded in the requirements.txt

A web application will be life for a limited amount of time for users to explore the application. 

Here is the link:

https://share.streamlit.io/lfegenbush3/cse6242_project/main/__main__.py


#### b. Data file: 

Datafile is a siple csv called recipe_clusters.csv and 	with about 320k recipes to pull from for the application. The file is too big in size to be stored on github and will need to be loaded separatelly. 	
	
	Download it from here:  
	******* add link to datafile ********

		save the datafile in the following folder structure 			relative to the application folder:

		 -someUserFolder
              |
		  |___reipe_explorer
		  |   |
		  |   |______all project files (src...)
		  |
		  |
		  |___data
		      |______ recipe_clusters.csv







## 3. EXECUTION

When the application is installed on a local machine, users will first need to install streamlit with the following command:  pip 

install streamlit

If you don't have your pip configured, go to the streamlit instalation page for indepth instalation instructions: 

https://docs.streamlit.io/en/stable/troubleshooting/clean-install.html


Once you have streamlit installed, open a command propt window inside the root directory of the projectand (recipe_explorer folder), or navigate to the folder within a prompt winodw. Once in the folder,run the following command:

streamlit run main.py

## 4. DEMO VIDEO

