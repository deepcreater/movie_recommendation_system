import pickle
import streamlit as st
import requests
import pandas as pd

# Function to fetch movie details from TMDB API
@st.cache_data
def get_movie_details(movie_id):
    """Fetches movie details including poster, popularity, rating, and overview from TMDB API."""
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
    data = requests.get(url).json()
    return data

# Function to fetch the movie poster
def fetch_poster(movie_id):
    """Fetches the movie poster URL from TMDB API."""
    data = get_movie_details(movie_id)
    if 'poster_path' in data and data['poster_path']:
        return f"https://image.tmdb.org/t/p/w500/{data['poster_path']}"
    return "https://via.placeholder.com/500x750?text=No+Image"

# Function to recommend movies
def recommend(movie, num_recommendations=5):
    """Recommends similar movies based on the input movie."""
    index_list = movies[movies['title'] == movie].index

    if index_list.empty:
        st.error("⚠️ Selected movie not found in dataset. Please choose a valid movie.")
        return [], []

    index = index_list[0]  # Get index safely
    if index >= len(similarity):
        st.error("⚠️ Similarity matrix mismatch. Try reloading data.")
        return [], []

    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])[1:num_recommendations + 1]

    recommended_movie_names = []
    recommended_movie_posters = []
    recommended_movie_ids = []

    for i in distances:
        if i[0] >= len(movies):  # Prevent out-of-bounds access
            print(f"Skipping invalid index: {i[0]} (Out of range)")
            continue

        movie_id = movies.iloc[i[0]].movie_id
        recommended_movie_ids.append(movie_id)
        recommended_movie_posters.append(fetch_poster(movie_id))
        recommended_movie_names.append(movies.iloc[i[0]].title)

    return recommended_movie_names, recommended_movie_posters, recommended_movie_ids

# Load data
try:
    movies = pickle.load(open('movie_list.pkl', 'rb'))
    similarity = pickle.load(open('similarity.pkl', 'rb'))

    # Ensure movies is a DataFrame
    if not isinstance(movies, pd.DataFrame):
        movies = pd.DataFrame(movies)

    print(f"✅ Movies Shape: {movies.shape}")
    print(f"✅ Similarity Matrix Shape: {similarity.shape}")

    if similarity.shape[0] != movies.shape[0]:
        raise ValueError("⚠️ Data Mismatch: Similarity matrix and movie list size do not match.")

except Exception as e:
    st.error(f"❌ Error loading dataset: {e}")
    st.stop()

# Streamlit UI
st.title("🎬 Movie Recommender System")

# Search and Filtering
st.sidebar.header("🔍 Filter Movies")
search_term = st.sidebar.text_input("Search for a movie")
if search_term:
    filtered_movies = movies[movies['title'].str.contains(search_term, case=False, na=False)]
else:
    filtered_movies = movies.copy()

# Assuming 'genres' and 'release_year' columns exist; adjust if needed
if 'genres' in movies.columns:
    all_genres = sorted(set([genre for sublist in movies['genres'].dropna() for genre in sublist]))
    selected_genres = st.sidebar.multiselect("Select genres", options=all_genres)
    if selected_genres:
        filtered_movies = filtered_movies[filtered_movies['genres'].apply(lambda x: any(genre in x for genre in selected_genres) if isinstance(x, list) else False)]

if 'release_year' in movies.columns:
    year_min, year_max = int(movies['release_year'].min()), int(movies['release_year'].max())
    selected_year_range = st.sidebar.slider("Select release year range", year_min, year_max, (year_min, year_max))
    filtered_movies = filtered_movies[(filtered_movies['release_year'] >= selected_year_range[0]) &
                                     (filtered_movies['release_year'] <= selected_year_range[1])]

# Movie Selection
selected_movie = st.selectbox("🎥 Type or select a movie", filtered_movies['title'].values)

# Customization Options
st.sidebar.header("⚙️ Customize Recommendations")
num_recommendations = st.sidebar.slider("Number of recommendations", min_value=1, max_value=10, value=5)
sort_by = st.sidebar.selectbox("Sort recommendations by", ["Relevance", "Popularity", "Rating"])

# Show Recommendations
if st.button('🎬 Show Recommendations'):
    recommended_movie_names, recommended_movie_posters, recommended_movie_ids = recommend(selected_movie, num_recommendations)

    if recommended_movie_names:
        # Sorting based on user choice
        if sort_by == "Popularity":
            popularity = [get_movie_details(movie_id).get('popularity', 0) for movie_id in recommended_movie_ids]
            sorted_indices = sorted(range(len(popularity)), key=lambda x: popularity[x], reverse=True)
        elif sort_by == "Rating":
            ratings = [get_movie_details(movie_id).get('vote_average', 0) for movie_id in recommended_movie_ids]
            sorted_indices = sorted(range(len(ratings)), key=lambda x: ratings[x], reverse=True)
        else:
            sorted_indices = list(range(len(recommended_movie_names)))

        # Display recommendations in columns
        cols = st.columns(5)
        for idx, i in enumerate(sorted_indices):
            if idx >= len(cols):  # Wrap to next row if more than 5
                cols = st.columns(5)
                idx = 0
            with cols[idx]:
                st.text(recommended_movie_names[i])
                st.image(recommended_movie_posters[i])
                with st.expander("More Details"):
                    data = get_movie_details(recommended_movie_ids[i])
                    st.write(f"**Overview:** {data.get('overview', 'No overview available')}")
                    st.write(f"**Popularity:** {data.get('popularity', 'N/A')}")
                    st.write(f"**Rating:** {data.get('vote_average', 'N/A')}/10")

# Footer
st.sidebar.markdown("---")
st.sidebar.write("Built with ❤️ using Streamlit")
st.sidebar.write("Built Deepak  Kumar Yadav")
