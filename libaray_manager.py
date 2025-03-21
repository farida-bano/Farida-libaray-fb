import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
import time
import requests
import plotly.express as px
import plotly.graph_objects as go
from streamlit_lottie import st_lottie

# --- Set Page Configuration ---
st.set_page_config(
    page_title="Personal Library Management System",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Ensure Required Files Exist ---
LIBRARY_FILE = "library.json"

def initialize_library():
    """Creates an empty library.json file if it doesn't exist."""
    if not os.path.exists(LIBRARY_FILE):
        with open(LIBRARY_FILE, "w") as f:
            json.dump([], f)

initialize_library()  # Ensure the file exists before loading

# --- Background Image Styling ---
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
            margin-bottom: 1rem;
            border-radius: 10px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

set_bg_image()

# --- Initialize Session State Variables ---
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

# --- Load and Save Library Data ---
def load_library():
    """Loads books from JSON file into session state."""
    try:
        with open(LIBRARY_FILE, "r") as file:
            st.session_state.library = json.load(file)
    except Exception as e:
        st.error(f"Error loading library: {e}")

def save_library():
    """Saves session state library to JSON file."""
    try:
        with open(LIBRARY_FILE, "w") as file:
            json.dump(st.session_state.library, file, indent=4)
    except Exception as e:
        st.error(f"Error saving library: {e}")

# Load library at startup
load_library()

# --- Add a Book ---
def add_book(title, author, year, genre, read_status):
    new_book = {
        "title": title,
        "author": author,
        "publication_year": year,
        "genre": genre,
        "read_status": read_status,
        "added_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    st.session_state.library.append(new_book)
    save_library()
    st.session_state.book_added = True

# --- Remove a Book ---
def remove_book(index):
    if 0 <= index < len(st.session_state.library):
        del st.session_state.library[index]
        save_library()
        st.session_state.book_removed = True

# --- Search Books ---
def search_books(term, search_by):
    term = term.lower()
    st.session_state.search_results = [
        book for book in st.session_state.library if term in book[search_by].lower()
    ]

# --- Sidebar Navigation ---
st.sidebar.header("📚 Navigation")
nav_option = st.sidebar.radio(
    "Select an option:",
    ["🏠 View Library", "➕ Add Book", "🔍 Search Books", "📊 Library Statistics"]
)

if nav_option == "🏠 View Library":
    st.session_state.current_view = "library"
elif nav_option == "➕ Add Book":
    st.session_state.current_view = "add"
elif nav_option == "🔍 Search Books":
    st.session_state.current_view = "search"
elif nav_option == "📊 Library Statistics":
    st.session_state.current_view = "stats"

# --- Main Content ---
st.title("📚 Personal Library Manager")

if st.session_state.current_view == "add":
    st.subheader("➕ Add a New Book")
    with st.form("add_book_form"):
        title = st.text_input("Book Title", max_chars=100)
        author = st.text_input("Author", max_chars=100)
        year = st.number_input("Publication Year", min_value=1000, max_value=datetime.now().year, value=2023)
        genre = st.selectbox("Genre", ["Fiction", "Non-Fiction", "Science", "Technology", "History", "Romance", "Poetry"])
        read_status = st.radio("Read Status", ["Read ✅", "Unread 📖"])
        
        if st.form_submit_button("Add Book"):
            if title and author:
                add_book(title, author, year, genre, read_status == "Read ✅")
                st.success("Book added successfully!")
                st.balloons()
            else:
                st.warning("Please fill in all fields!")

elif st.session_state.current_view == "library":
    st.subheader("📚 Your Library")
    if not st.session_state.library:
        st.info("No books found. Add some books to get started!")
    else:
        for i, book in enumerate(st.session_state.library):
            with st.expander(f"{book['title']} by {book['author']}"):
                st.write(f"**Publication Year:** {book['publication_year']}")
                st.write(f"**Genre:** {book['genre']}")
                st.write(f"**Status:** {'✅ Read' if book['read_status'] else '📖 Unread'}")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Remove", key=f"remove_{i}"):
                        remove_book(i)
                        st.experimental_rerun()
                with col2:
                    if st.button("Toggle Read Status", key=f"toggle_{i}"):
                        st.session_state.library[i]['read_status'] = not book['read_status']
                        save_library()
                        st.experimental_rerun()

elif st.session_state.current_view == "search":
    st.subheader("🔍 Search Books")
    search_by = st.selectbox("Search by", ["title", "author", "genre"])
    search_term = st.text_input("Enter search term")
    if st.button("Search"):
        if search_term:
            search_books(search_term, search_by)
            if st.session_state.search_results:
                st.success(f"Found {len(st.session_state.search_results)} result(s).")
                for book in st.session_state.search_results:
                    st.write(f"📖 **{book['title']}** by {book['author']} ({book['publication_year']})")
            else:
                st.warning("No matching books found.")

elif st.session_state.current_view == "stats":
    st.subheader("📊 Library Statistics")
    total_books = len(st.session_state.library)
    read_books = sum(book['read_status'] for book in st.session_state.library)
    unread_books = total_books - read_books
    st.metric("Total Books", total_books)
    st.metric("Books Read", read_books)
    st.metric("Books Unread", unread_books)
    
    if total_books:
        fig = go.Figure(data=[go.Pie(labels=["Read", "Unread"], values=[read_books, unread_books], hole=0.4)])
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No books in library to generate statistics.")

st.write("©️ 2024 Personal Library Manager | Developed by Farida Bano")
