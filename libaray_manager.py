import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
import time
import random
import plotly.express as px
import plotly.graph_objects as go
from streamlit.logger import st_lottie
import requests 


# Set page configuration
st.set_page_config(
    page_title="Personal Library Management System",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)
#custom css for styling
st.markdown("""
 <style>
       .main-header{
       font-size:3rem 1important;
       color-weight:700;
       margin-bottom:1rem;
       text-align:center;
       text-shadow:2px 2px 4px rgba(0,0,0,1);
     }
       .sub_header{
       font-size:1.8rem !important;color:3882f6;
       font-weight: 600;
       margin-bottom:1rem;
       margin-bottom:1rem;
     }
       .sucess-message{
       padding:1rem;
       background-color:#ECFDFS;
       border-left: 5px solid #1089981;
       border-radius:0.375rem;
       backgroun-color:#fef3c7;
       border-radius:0.375rem;
}

.book-card{

       background-color:#f3f4f6;
       border-radius:0.5rem;
       padding:1rem;
       marging-bottom:1rem;
       border-left:5px solid #3882f6;
       transition:transfrom 0.3s ease;
       }

       .book-card-hover{
        transfrom:translatrY(-5px);
        box-shadow:0 10px 15px -3px rgba(0,0,0.1);
        }

        .red-badge{
         background-color:#108981;
         color:white;
         padding:0.25rem 0.75rem;
         border-radius:1rem;
         font-size:0.875rem;
         font-weight:600;
     }

     .unread_badge {
     background-color:#F87171;
         color:white;
         padding:0.25rem 0.75rem;
         border-radius:1rem;
         font-size:0.875rem;
         font-weight:600;
        
     }

     .action-button{
     margin-right: 0.5rem;

     }
     .stButton>button
     {
     border-redius:0.375rem;

     }
     </style>
""",unsafe_allow_html=True)

#next
def load_lottieur(url):
     try:
        r=requests.get(url)
        if r.status_code !=200:
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
          with open('labrary.json','r')as file:
             st.session_state.library =json.load (file)
             return True
          return False
    except Exception as e:
       st.error(f"Error loading library:(e)")
       return False
    
    # save library
def save_library():
    try:
        with open('library.json', 'w') as file:
            json.dump(st.session_state.library, file)
        return True
    except Exception as e:
        st.error(f"Error saving library: {e}")
        return False

#add a book to library
def add_book(title,author,publication_year,genre,read_status):
   book ={
      'title':title,
      'author':author,
      'publication_year':publication_year,
      'genre':genre,
      'read_status':read_status,
      'added_date' : datetime.now().strftime("%Y-%m-%d-%H:%M:%5")
   }
   st.seesion_state.library.append(book)
   save_library()
   st.session_state.book_added =True
   time.sleep(0.5) 

   #remove books
   def remove_book(index):
      if 0<= index <len(st.session_state.labrary):
         
         del st.seesion_state.library[index]
         save_library()
         st.session_state.book_removed =True
         return True
      return False
   
   #search books
   def search_books(search_term, search_by):
      search_term =search_term.lower()
      results = []

      for book in st.session_state.library:
        if search_by == "Title" and search_term in book['title'].lower():
          results.append(book)
        elif search_by == "Author" and search_term in book[author].lower():
          results.append(book)
        elif search_by =="Genre" and search_term in book['genre'].lower():
          results.append(book)
      st.session_state.search_results = results

# calculate libarary
def get_ibrary_stats():
    total_books=len(st.session_state.library)
    read_books =sum(1 for book in st.session_state.library if book['read status'])
    percentage =(read_books/total_books * 100)if total_books >0 else 0
 
genres = {}
authors ={}
decades={}

for book in st.session_state.library:
# count genres
 if book [' genre'] in genres:
   genres[book['genre']]+= 1
 else:
   genres[book['genre']]=+1
  
  # count author
if book [' author'] in authors:
   authors [book['author']]+= 1
else:
   authors[book['author']]=+1

   #count decades

   decades = (book['publication_year']// 10)* 10
   if decades in decades:
      decades [decades] +=1
   else:
      decades [decades] +=1

   #sort by dictionaries

   genres = dict(sorted(genres.items(),key=lambda x:x[1],reverse=True))
   author= dict(sorted(authors.items(),key=lambda x:x[1],reverse=True))
   decades = dict(sorted(decades.items()))
                  
   return {
        'total_books': total_books,
        'read_books': read_books,
        'percent_read': percent_read,
        'genres': genres,
        'authors': authors,
        'decades': decades
    }
def create_vlsulations(stats):
  if stats['total_books']>0:
    fig_read_status = go.Figure(data=(go.Pie(
      LABELS=["Read","Unread"],
      values=[ stats['state_books'],stats['total_books']- stats['read-books']],
      hole =.4,
      marker_colors=['#108989' ,'#f87171']
 )))
  fig_read_status.update_layout(
  title_text="Read vs Unread Books",
  showlegend=True,
  height=400
 )
  st.plotly_chart(fig_read_status, use_container_widtg=True)

 # bar chart
  if stats('genre'):
    genres_df = pd.DataFrame({
        'Genre': list(stats['genres'].keys()),
        'Count': list(stats['genres'].values())  # Fixed key name and column values
    })
 
  fig_genres = px.bar(
        genres_df,
        x='Genre',
        y='Count',
        color='Count',
        color_continuous_scale=px.colors.sequential.Blues
    )
  fig_genres.update_layout(
  title_text='Book by publication decade',
  xaxis_title='Decade',
  xyxis_title='Numbers of Books',
  height=400
)
  st.plotly_chart(fig_genres,ues_container_width=True)
  if stats['decade']:
    'Decade': [f"{decade}s" for decade in stats['decades'].keys()],
    'Count' : list(stats['decades'].values())
fig_decades = px.line(
  decades_df,
  x='Decade',
  y= 'Count'
  markers=True
  line_sape='spline'
)
fig_decades.update_layout(
  title-text='Book by Publication Decade',
  xaxis_title='Decade',
  yaxis_title='Nunbers of books',
  height=400
)
st.pyplot_chart(fig_decades,use_container_width= True)

# Load library
load_library()
st.sidebar.markdown("<h1 style='text-align:center;'>Navigation</h1>", unsafe_allow_html=True)

# Load Lottie animation (fixed URL and variable name)
lottie_book = load_lottieurl("https://assets9.lottiefiles.com/temp/1f20aKAfin.json")  # Fixed URL
st.sidebar.lottie(lottie_book, height=200, key='book_animation')

# Navigation radio buttons (fixed variable name and options)
nav_option = st.sidebar.radio(
    "Choose an option:",
    ["View Library", "Add Book", "Search Book", "Library Statistics"]  # Added missing options
)

# Handle navigation selection (fixed variable names and added missing options)
if nav_option == "View Library":
    st.session_state.current_view = "library"
elif nav_option == "Add Book":
    st.session_state.current_view = "add"
elif nav_option == "Search Book":
    st.session_state.current_view = "search"
elif nav_option == "Library Statistics":
    st.session_state.current_view = "stats"

st.markdown("<h1 className='main-header'>Personal Library Manger</h1>",unsafe_allow_html=True)
if st.session_state.current/_view == "add":
  st.markdown("<h2 className = 'sub-header'>Add a new book</h2>",unsafe_allow_html=True)

  #adding book input fore
  with st.form( key='add_book_form'):
    col1,col2=st.colums(2)
with col1:
  title= st.text_input("Book Title", max_chars=100)
  author =st_text_input("Author",max_chars=100)
  publication_year= st.number_input("Publication year",main_value=1000, max_value=datetime.now().year, step=1,value=2023)

with col2:
  genre =st.selectbox("Genre",[
    "Frication","Non-Frication","Science","Tecnology","Romance","Poetry","Self-help","Art","History","Music","Religion"
  ])
  read_status= st.radio("Read Status",["Read","Unread"],horizontal=True)
  read_bool =read_status == "Read"
  submit_button =st.form_submit_button(label="Add Book")

  if submit_button and title and author:
    add_book(title,author,publication_year,genre,read_bool)
    if st.session_state.book_added:
      st.markdown("<div class='success-message'> Book added sucessfully</div>",unsafe_allow_html=True)
      st.ballooms()
      st.session_state.book_added =False

  elif st.session_state.current_view =="library":
    st.markdown("<h2 class ='sub_header' Your Library></h2>",unsafe_allow_html=True")

  if not st.session_state.labrary:
    st.markdown("<div class='warning_message'>Your library is empty.Add some books to get started!</div>",ubsafe)_allow_html=True)
  else:
    cols =st.colums(2)
    for i,book in enumerate(st.session.library):
        with cols[i % 2]:
          st.markdown(f"""<div class ='book card'> 
           <h3>{book['title']}</h3>
           <p> <strong> Author:</strong>{book['publication_year']}</p>
           <p><strong>Publication Year:</strong>{book['Publication_year']}</p>
           <p><strong>Genre:</strong>{book["genre"]}></p>
           <p> <span class='{"read-badge" if book['read_status']else "unread-badge"}'>{
            "Read" if book ["read_status"]else "Unread"
           }</span></p>
          </div>
          """ ,unsafe_allow_html=True)

          col1 ,col2 =st.columns(2)
          with col1:
            if st.button(f" Remove",key=f"remove_{i},use_container_width=True"):
               if remove-book(i):
                  st.rerun()
               with col2: 
                new_status = not [ "read_status"]
                status_label="Matk as read" if not book [ 'read_status']else "Mark as Unread"
                if st.button(status_label,key =f"status_(i)",use_container_width=True):
                  st.session_state.labrary[i]["read_status"]=new_status
                  save_library()
                  st.rerun()
            if st.session_state.book_removed:
              st.markdown("<div class'sucess message '>Book removed sucessfully"></div>",unsafe_allow_html=True")
              st.session_state.book_removed =False
            elif st.session_state.current_view == "search":
              st.markdown ("<h2 class ='sub-header'>search books</h2>",unsafe_allow_html=True)
