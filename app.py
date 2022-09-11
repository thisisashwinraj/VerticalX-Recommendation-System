#Import required Libraries
import streamlit as st
import pickle
import pandas as pd
import requests

#Hide Streamlit Menu and Default Footer
hide_menu_style = """
<style>
#MainMenu  {visibility: hidden;}
footer {visibility: hidden;}
</style>
"""
st.markdown(hide_menu_style, unsafe_allow_html=True)

#Fetch posters from TMDb Database
def fetch_poster(movie_id):
	response = requests.get('https://api.themoviedb.org/3/movie/{}?api_key=8d2beee4b9a58936c45ec0e107239142&language=en-US'.format(movie_id))
	data = response.json()
	return "https://image.tmdb.org/t/p/w500/" + data['poster_path']

#Recommend movies based on  content
def recommend(movie):
	movie_index = movies[movies['original_title'] == movie].index[0]
	distances = similarity[movie_index]
	movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x:  x[1])[1:6]

	recommended_movies = []
	recommended_movies_poster = []
	for  i in movies_list:
		movie_id = movies.iloc[i[0]].id
		recommended_movies.append(movies.iloc[i[0]].original_title)
		recommended_movies_poster.append(fetch_poster(movie_id))
	return recommended_movies,recommended_movies_poster

#Frontend Design for StreamLit WebApp Sidebar
st.sidebar.subheader(" ")

st.sidebar.subheader("Technology:")
st.sidebar.text("Natural Language Processing")

st.sidebar.subheader("Developed By")
st.sidebar.text("Ashwin Raj, Student at UCEK")

movies_dict = pickle.load(open('pickle/movie_dict.pkl','rb'))
movies = pd.DataFrame(movies_dict)

similarity = pickle.load(open('pickle/similarity.pkl','rb'))

#Frontend Hero Section
st.title("Movie Recommender System")

selected_movie_name = st.selectbox(
'Select a movie to recommend',
movies['original_title'].values)

#Output Recommendations with Posters
if st.button('Recommend'):
	name, posters = recommend(selected_movie_name)
	
	col1, col2, col3, col4,  col5 = st.columns(5)
	with col1:
		st.text(name[0])
		st.image(posters[0])
	with col2:
		st.text(name[1])
		st.image(posters[1])
	with col3:
		st.text(name[2])
		st.image(posters[2])
	with col4:
		st.text(name[3])
		st.image(posters[3])
	with col5:
		st.text(name[4])
		st.image(posters[4])
