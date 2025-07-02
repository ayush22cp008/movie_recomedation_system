import pandas as pd
import pickle
import streamlit as st
import requests
import time

API_KEY = "b1e9d3b7bd4b3930679e686ae66ba769"

def fetch_poster(movie_id):
    """
    Fetch the poster URL for a given movie_id.
    If no poster or request fails, return None.
    """
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US"
    tries = 3
    for attempt in range(tries):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            poster_path = data.get("poster_path")
            if poster_path:
                return "https://image.tmdb.org/t/p/w500" + poster_path
            else:
                # No poster available
                return None
        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            time.sleep(2)
    # All attempts failed
    return None


def Recommend(movie):
    """
    Recommend 5 movies similar to the given movie.
    Returns two lists: titles and poster URLs (or None).
    """
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]
    recommended_movie = []
    recommended_movie_posters = []
    for i in movie_list:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movie.append(movies.iloc[i[0]].title)
        poster_url = fetch_poster(movie_id)
        recommended_movie_posters.append(poster_url)
    return recommended_movie, recommended_movie_posters


# Load data
st.title('Movie Recommendation System')
movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)
# similarity = pickle.load(open('similarity.pkl', 'rb'))
import gdown
import os
SIMILARITY_FILE = "similarity.pkl"
if not os.path.exists(SIMILARITY_FILE):
    st.write("Downloading similarity matrix, please wait...")
    file_id = "1TyvWqa0-WImBDbHM9uIgh0FON0QN4Dsx"   # Replace with your real file ID
    url = f"https://drive.google.com/uc?id={file_id}"
    gdown.download(url, SIMILARITY_FILE, quiet=False)

similarity = pickle.load(open(SIMILARITY_FILE, 'rb'))

selected_movie_name = st.selectbox('Select a movie:', movies['title'].values)

if st.button('Recommend'):
    names, posters = Recommend(selected_movie_name)

    # Create 5 columns
    columns = st.columns(5)

    # Loop over recommendations
    for idx, col in enumerate(columns):
        with col:
            st.text(names[idx])
            if posters[idx]:
                # Display poster if available
                st.image(posters[idx])
            else:
                # No poster found
                st.write("No poster fetched")
