import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
import time
import random
import plotly.express as px
import plotly.graph_objects as go
from streamlit_lottie import st_lottie
import requests

# Set page configuration
st.set_page_config(
    page_title="Personal Library Management System",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add background image
def set_bg_image():
    st.markdown(
        """
        <style>
        .stApp {
            background-image: url("https://images.unsplash.com/photo-1497633762265-9d179a990aa6?ixlib=rb-1.2.1&auto=format&fit=crop&w=1920&q=80");
            background-size: cover;
            background-position: center;
        }
        .content-wrapper {
            background-color: rgba(255, 255, 255, 0.9);
            padding: 2rem;
           
        }
        </style>
        """,
        unsafe_allow_html=True
    )

set_bg_image()

# Custom CSS for styling
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem !important;
        font-weight: 700;
        margin-bottom: 1rem;
        text-align: center;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        color: #2c3e50;
    }
    .sub-header {
        font-size: 1.8rem !important;
        color: #3882f6;
        font-weight: 600;
        margin-bottom: 1rem;
    }
    .success-message {
        padding: 1rem;
        background-color: #ECFDF5;
        border-left: 5px solid #10B981;
        border-radius: 0.375rem;
        margin: 1rem 0;
    }
    .warning-message {
        padding: 1rem;
        background-color: #fef3c7;
        border-left: 5px solid #F59E0B;
        border-radius: 0.375rem;
        margin: 1rem 0;
    }
    .book-card {
        background-color: #f3f4f6;
        border-radius: 0.5rem;
        padding: 1rem;
        margin-bottom: 1rem;
        border-left: 5px solid #3882f6;
        transition: transform 0.3s ease;
    }
    .book-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1);
    }
    .read-badge {
        background-color: #10B981;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        font-size: 0.875rem;
        font-weight: 600;
    }
    .unread-badge {
        background-color: #F87171;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        font-size: 0.875rem;
        font-weight: 600;
    }
    .stButton>button {
        border-radius: 0.375rem !important;
    }
    </style>
""", unsafe_allow_html=True)

def load_lottieurl(url):
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None

# Initialize session state
if 'library' not in st.session_state:
    st.session_state.library = []
if 'search_results' not in st.session_state:
    st.session_state.search_results = []
if 'book_added' not in st.session_state:
    st.session_state.book_added = False
if 'book_removed' not in st.session_state:
    st.session_state.book_removed = False
if 'current_view' not in st.session_state:
    st.session_state.current_view = "library"

def load_library():
    try:
        if os.path.exists('library.json'):
            with open('library.json', 'r') as file:
                st.session_state.library = json.load(file)
            return True
        return False
    except Exception as e:
        st.error(f"Error loading library: {e}")
        return False

def save_library():
    try:
        with open('library.json', 'w') as file:
            json.dump(st.session_state.library, file)
        return True
    except Exception as e:
        st.error(f"Error saving library: {e}")
        return False

def add_book(title, author, publication_year, genre, read_status):
    book = {
        'title': title,
        'author': author,
        'publication_year': publication_year,
        'genre': genre,
        'read_status': read_status,
        'added_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    st.session_state.library.append(book)
    save_library()
    st.session_state.book_added = True
    time.sleep(0.5)

def remove_book(index):
    if 0 <= index < len(st.session_state.library):
        del st.session_state.library[index]
        save_library()
        st.session_state.book_removed = True
        return True
    return False

def search_books(search_term, search_by):
    search_term = search_term.lower()
    results = []
    for book in st.session_state.library:
        if search_by == "Title" and search_term in book['title'].lower():
            results.append(book)
        elif search_by == "Author" and search_term in book['author'].lower():
            results.append(book)
        elif search_by == "Genre" and search_term in book['genre'].lower():
            results.append(book)
    st.session_state.search_results = results

def get_library_stats():
    total_books = len(st.session_state.library)
    read_books = sum(1 for book in st.session_state.library if book['read_status'])
    percent_read = (read_books / total_books * 100) if total_books > 0 else 0
    
    genres = {}
    authors = {}
    decades = {}
    
    for book in st.session_state.library:
        # Count genres
        if book['genre'] in genres:
            genres[book['genre']] += 1
        else:
            genres[book['genre']] = 1
        
        # Count authors
        if book['author'] in authors:
            authors[book['author']] += 1
        else:
            authors[book['author']] = 1
        
        # Count decades
        decade = (book['publication_year'] // 10) * 10
        if decade in decades:
            decades[decade] += 1
        else:
            decades[decade] = 1
    
    return {
        'total_books': total_books,
        'read_books': read_books,
        'percent_read': percent_read,
        'genres': dict(sorted(genres.items(), key=lambda x: x[1], reverse=True)),
        'authors': dict(sorted(authors.items(), key=lambda x: x[1], reverse=True)),
        'decades': dict(sorted(decades.items()))
    }

def create_visualizations(stats):
    if stats['total_books'] > 0:
        # Read status pie chart
        fig_read_status = go.Figure(data=[go.Pie(
            labels=["Read 📖", "Unread 📘"],
            values=[stats['read_books'], stats['total_books'] - stats['read_books']],
            hole=0.4,
            marker_colors=['#10B981', '#F87171']
        )])
        fig_read_status.update_layout(
            title_text="Read vs Unread Books",
            showlegend=True,
            height=400
        )
        st.plotly_chart(fig_read_status, use_container_width=True)
        
        # Genre distribution bar chart
        if stats['genres']:
            genres_df = pd.DataFrame({
                'Genre': list(stats['genres'].keys()),
                'Count': list(stats['genres'].values())
            })
            fig_genres = px.bar(
                genres_df,
                x='Genre',
                y='Count',
                color='Count',
                color_continuous_scale=px.colors.sequential.Blues
            )
            fig_genres.update_layout(
                title_text='Books by Genre 📚',
                xaxis_title='Genre',
                yaxis_title='Number of Books',
                height=400
            )
            st.plotly_chart(fig_genres, use_container_width=True)
        
        # Decade distribution line chart
        if stats['decades']:
            decades_df = pd.DataFrame({
                'Decade': [f"{decade}s" for decade in stats['decades'].keys()],
                'Count': list(stats['decades'].values())
            })
            fig_decades = px.line(
                decades_df,
                x='Decade',
                y='Count',
                markers=True,
                line_shape='spline'
            )
            fig_decades.update_layout(
                title_text='Books by Publication Decade 📅',
                xaxis_title='Decade',
                yaxis_title='Number of Books',
                height=400
            )
            st.plotly_chart(fig_decades, use_container_width=True)

# Load library
load_library()

# Sidebar
st.sidebar.markdown("<h1 style='text-align:center;'>Navigation 📚</h1>", unsafe_allow_html=True)
lottie_book = load_lottieurl("https://assets9.lottiefiles.com/packages/lf20_aukcraoi.json")
if lottie_book:
    st.sidebar.lottie(lottie_book, height=150, key='book_animation')

nav_option = st.sidebar.radio(
    "Choose an option:",
    ["🏠 View Library", "➕ Add Book", "🔍 Search Books", "📊 Library Statistics"]
)

if "🏠 View Library" in nav_option:
    st.session_state.current_view = "library"
elif "➕ Add Book" in nav_option:
    st.session_state.current_view = "add"
elif "🔍 Search Books" in nav_option:
    st.session_state.current_view = "search"
elif "📊 Library Statistics" in nav_option:
    st.session_state.current_view = "stats"

# Main content
st.markdown("<h1 class='main-header'>Personal Library Manager 📚</h1>", unsafe_allow_html=True)

with st.container():
    if st.session_state.current_view == "add":
        st.markdown("<h2 class='sub-header'>📖 Add a New Book</h2>", unsafe_allow_html=True)
        with st.form(key='add_book_form'):
            col1, col2 = st.columns(2)
            with col1:
                title = st.text_input("Book Title", max_chars=100)
                author = st.text_input("Author", max_chars=100)
                publication_year = st.number_input(
                    "Publication Year",
                    min_value=1000,
                    max_value=datetime.now().year,
                    value=2023
                )
            with col2:
                genre = st.selectbox("Genre", [
                    "Fiction", "Non-Fiction", "Science", "Technology",
                    "Romance", "Poetry", "Self-help", "Art", "History",
                    "Music", "Religion"
                ])
                read_status = st.radio(
                    "Read Status",
                    ["Read ✅", "Unread 📖"],
                    horizontal=True
                )
                read_bool = read_status == "Read ✅"
            
            if st.form_submit_button("Add Book 📚"):
                if title and author:
                    add_book(title, author, publication_year, genre, read_bool)
                    if st.session_state.book_added:
                        st.markdown(
                            "<div class='success-message'>Book added successfully! 🎉</div>",
                            unsafe_allow_html=True
                        )
                        st.balloons()
                        st.session_state.book_added = False
                else:
                    st.warning("Please fill in all required fields!")

    elif st.session_state.current_view == "library":
        st.markdown("<h2 class='sub-header'>📚 Your Library</h2>", unsafe_allow_html=True)
        if not st.session_state.library:
            st.markdown(
                "<div class='warning-message'>Your library is empty. Add some books to get started! 📖</div>",
                unsafe_allow_html=True
            )
        else:
            cols = st.columns(2)
            for i, book in enumerate(st.session_state.library):
                with cols[i % 2]:
                    status = "Read ✅" if book['read_status'] else "Unread 📖"
                    st.markdown(f"""
                    <div class='book-card'>
                        <h3>{book['title']}</h3>
                        <p><strong>👤 Author:</strong> {book['author']}</p>
                        <p><strong>📅 Publication Year:</strong> {book['publication_year']}</p>
                        <p><strong>📚 Genre:</strong> {book['genre']}</p>
                        <p><span class='{"read-badge" if book['read_status'] else "unread-badge"}'>
                            {status}
                        </span></p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button(f"Remove 🗑️", key=f"remove_{i}"):
                            if remove_book(i):
                                st.rerun()
                    with col2:
                        new_status = not book['read_status']
                        status_label = "Mark as Read ✅" if not book['read_status'] else "Mark as Unread 📖"
                        if st.button(status_label, key=f"status_{i}"):
                            st.session_state.library[i]['read_status'] = new_status
                            save_library()
                            st.rerun()
                    
            if st.session_state.book_removed:
                st.markdown(
                    "<div class='success-message'>Book removed successfully! 🗑️</div>",
                    unsafe_allow_html=True
                )
                st.session_state.book_removed = False

    elif st.session_state.current_view == "search":
        st.markdown("<h2 class='sub-header'>🔍 Search Books</h2>", unsafe_allow_html=True)
        search_by = st.selectbox("Search by:", ["Title", "Author", "Genre"])
        search_term = st.text_input("Enter search term:")
        if st.button("Search 🔎"):
            if search_term:
                with st.spinner("Searching..."):
                    time.sleep(0.5)
                    search_books(search_term, search_by)
                    if hasattr(st.session_state, 'search_results'):
                        st.markdown(
                            f"<h3>Found {len(st.session_state.search_results)} results 🎯</h3>",
                            unsafe_allow_html=True
                        )
                        for book in st.session_state.search_results:
                            status = "Read ✅" if book['read_status'] else "Unread 📖"
                            st.markdown(f"""
                            <div class='book-card'>
                                <h3>{book['title']}</h3>
                                <p><strong>👤 Author:</strong> {book['author']}</p>
                                <p><strong>📅 Publication Year:</strong> {book['publication_year']}</p>
                                <p><strong>📚 Genre:</strong> {book['genre']}</p>
                                <p><span class='{"read-badge" if book['read_status'] else "unread-badge"}'>
                                    {status}
                                </span></p>
                            </div>
                            """, unsafe_allow_html=True)
                        if not st.session_state.search_results:
                            st.markdown(
                                "<div class='warning-message'>No books found matching your search. 😞</div>",
                                unsafe_allow_html=True
                            )

    elif st.session_state.current_view == "stats":
        st.markdown("<h2 class='sub-header'>📊 Library Statistics</h2>", unsafe_allow_html=True)
        if not st.session_state.library:
            st.markdown(
                "<div class='warning-message'>Your library is empty. Add some books to see statistics! 📈</div>",
                unsafe_allow_html=True
            )
        else:
            stats = get_library_stats()
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📚 Total Books", stats['total_books'])
            with col2:
                st.metric("✅ Books Read", stats['read_books'])
            with col3:
                st.metric("📈 Percentage Read", f"{stats['percent_read']:.1f}%")
            
            create_visualizations(stats)
st.markdown("<div style='text-align: center; color: #666;'>Copyright © 2024 Farida Bano - Personal Library Manager 📚</div>", 
            unsafe_allow_html=True)  # 34 line main error araha hy
