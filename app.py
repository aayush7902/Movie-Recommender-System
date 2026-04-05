import streamlit as st
import pickle
import pandas as pd
import requests



movies = pickle.load(open('movies.pkl', 'rb'))
tfidf_sim = pickle.load(open('tfidf_sim.pkl', 'rb'))
bert_sim = pickle.load(open('bert_sim.pkl', 'rb'))











import base64

def set_bg(image_file):
    with open(image_file, "rb") as f:
        data = f.read()
    encoded = base64.b64encode(data).decode()

    page_bg = f"""
    <style>
    .stApp {{
        background-image: url("data:image/jpg;base64,{encoded}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
    }}
    </style>
    """

    st.markdown(page_bg, unsafe_allow_html=True)


set_bg("MRS.jpg")

if 'watchlist' not in st.session_state:
    st.session_state['watchlist'] = []


def fetch_poster(movie_id):
    url = "https://api.themoviedb.org/3/movie/{}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US".format(movie_id)
    data = requests.get(url)
    data = data.json()
    poster_path = data['poster_path']
    full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
    return full_path



def fetch_trailer(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}/videos?api_key=8265bd1679663a7ea12ac168da84d2e8"
        data = requests.get(url).json()

        for video in data.get('results', []):
            if video['type'] == 'Trailer' and video['site'] == 'YouTube':
                return f"https://www.youtube.com/watch?v={video['key']}"
    except:
        pass

    return None


def fetch_details(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
        data = requests.get(url).json()

        poster_path = data.get('poster_path')
        rating = data.get('vote_average', 'N/A')

        if poster_path:
            poster = "https://image.tmdb.org/t/p/w500/" + poster_path
        else:
            poster = ""

        return poster, rating

    except:
        return "", "N/A"


def recommend(movie):

    index = movies[movies['title'] == movie].index[0]

    hybrid = 0.5 * tfidf_sim[index] + 0.5 * bert_sim[index]

    distances = list(enumerate(hybrid))
    distances = sorted(distances, reverse=True, key=lambda x: x[1])

    selected_universe = movies.iloc[index]['universe']

    recommended_movie_names = []
    recommended_movie_posters = []

    for i in distances[1:50]:
        movie_data = movies.iloc[i[0]]

        score = hybrid[i[0]]

        if movie_data['universe'] == selected_universe:
            score += 0.2

        if "horror" in movie_data['genres'].lower():
            score += 0.1

        recommended_movie_names.append(movie_data['title'])
        recommended_movie_posters.append(fetch_poster(movie_data['id']))

    return recommended_movie_names[:5], recommended_movie_posters[:5]


st.title('Movie Recommender System')
selected_movie_name = st.selectbox(
'Select a movie',
movies['title'].values)



if st.button('Recommend'):
   names,posters =  recommend(selected_movie_name)



   col1, col2, col3, col4, col5 =st.columns(5)
   with col1:
       st.text(names[0])
       st.image(posters[0])
   with col2:
       st.text(names[1])
       st.image(posters[1])
   with col3:
       st.text(names[2])
       st.image(posters[2])
   with col4:
       st.text(names[3])
       st.image(posters[3])
   with col5:
       st.text(names[4])
       st.image(posters[4])





def fetch_details(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
        data = requests.get(url).json()

        poster = "https://image.tmdb.org/t/p/w500/" + data.get('poster_path', "")
        rating = data.get('vote_average', "N/A")
        overview = data.get('overview', "No description")

        return poster, rating, overview
    except:
        return "", "N/A", "No data"

def fetch_trailer(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}/videos?api_key=8265bd1679663a7ea12ac168da84d2e8"
        data = requests.get(url).json()

        for video in data.get('results', []):
            if video['type'] == 'Trailer':
                return f"https://www.youtube.com/watch?v={video['key']}"
    except:
        pass
    return None


if st.button('🚀 Recommend Movies with Trailers and ratings'):
    names, posters = recommend(selected_movie_name)

    st.session_state['names'] = names

if 'names' in st.session_state:

    for idx, movie_name in enumerate(st.session_state['names']):

        index = movies[movies['title'] == movie_name].index[0]
        movie_id = movies.iloc[index]['id']

        poster, rating, overview = fetch_details(movie_id)
        trailer = fetch_trailer(movie_id)

        st.markdown(f"## 🎬 {movie_name}")

       
        col1, col2 = st.columns([1, 2])

       
        with col1:
            if poster:
                st.image(poster)

       
        with col2:
            st.markdown(f"⭐ Rating: {rating}")
            st.markdown(f"📝 {overview}")

            if trailer:
                st.video(trailer)


            else:
                st.write("🚫 Trailer not available")

