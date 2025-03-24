import json
import datetime
import streamlit as st
import pandas as pd
from pymongo import MongoClient


@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_books(query={}):
    return list(collection.find(query, {"_id": 0}))

# MongoDB Connection
MONGO_URI = "mongodb+srv://admin:Admintest123@cluster0.upudd.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(MONGO_URI)
db = client["mydatabase"]  # Replace with your actual database name
collection = db["library"]  # Replace with your collection name

# Predefined common genre tags
common_genre_tags = {
    "Fiction": ["Novel", "Literary Fiction", "Historical Fiction"],
    "Non-fiction": ["Memoir", "Biography", "Self-help"],
    "Mystery": ["Detective", "Crime", "Thriller"],
    "Fantasy": ["Epic Fantasy", "Urban Fantasy", "Dark Fantasy"],
    "Science Fiction": ["Sci-Fi", "Dystopian", "Time Travel"],
    "Romance": ["Contemporary Romance", "Historical Romance", "Romantic Suspense"],
    "Horror": ["Paranormal Horror", "Psychological Horror"],
    "History": ["World History", "Military History"],
    "Thriller": ["Psychological Thriller", "Spy Thriller"]
}

def match_genre_tags(user_genres):
    tags = set()
    for genre in user_genres:
        for key, values in common_genre_tags.items():
            if any(genre.lower() in value.lower() for value in values):
                tags.add(key.lower().replace(" ", "_"))
    return list(tags)   

def save_library(library):
    """Save library data to MongoDB."""
    collection.delete_many({})  # Clear old data
    if library:
        collection.insert_many(library)  # Insert new records

def is_valid_year(year):
    """Check if the entered year is valid."""
    current_year = datetime.datetime.now().year
    return year.isdigit() and 1000 <= int(year) <= current_year

st.set_page_config(layout="wide")  # Make display wide
st.title("📚 Personal Library Manager")

library = load_library()
menu = st.radio("Select an Option:", ["Add Book", "Remove Book", "Search Book", "Display All Books", "Statistics"], horizontal=True)

if menu == "Add Book":
    st.header("Add a New Book")
    title = st.text_input("Book Title")
    author = st.text_input("Author")
    year = st.selectbox("Publication Year", list(range(datetime.datetime.now().year, 999, -1)))
    genre_input = st.text_input("Enter genres (comma-separated)")
    genre = [g.strip().lower() for g in genre_input.split(",") if g.strip()]
    matched_tags = match_genre_tags(genre)
    read_status = st.selectbox("Have you read this book?", ("Yes", "No"))
    
    if st.button("Add Book"):
        if title and author:
            duplicate_books = [book for book in library if book["Title"].lower() == title.lower()]
            exact_duplicate = any(book for book in duplicate_books if book["Author"].lower() == author.lower())
            
            if exact_duplicate:
                st.error("This book is already in your library.")
            elif duplicate_books:
                if st.button("Yes, Add Book Anyway"):
                    new_book = {
                        "Title": title,
                        "Author": author,
                        "Year": int(year),
                        "Genre": genre,
                        "Tags": matched_tags,
                        "Read": read_status == "Yes"
                    }
                    library.append(new_book)
                    save_library(library)
                    st.success("Book added successfully!")
            else:
                new_book = {
                    "Title": title,
                    "Author": author,
                    "Year": int(year),
                    "Genre": genre,
                    "Tags": matched_tags,
                    "Read": read_status == "Yes"
                }
                library.append(new_book)
                save_library(library)
                st.success("Book added successfully!")
        else:
            st.error("Please enter valid book details!")

elif menu == "Remove Book":
    st.header("Remove a Book")
    book_titles = [book["Title"] for book in library]
    if book_titles:
        selected_book = st.selectbox("Select book to remove", ["Select a book"] + book_titles, index=0)
        if st.button("Remove Book"):
            if selected_book == "Select a book":
                st.error("Please select a valid book to remove.")
            else:
                library = [book for book in library if book["Title"] != selected_book]
                save_library(library)
                st.success("Book removed successfully!")
    else:
        st.info("No books available to remove.")

elif menu == "Search Book":
    st.header("Search for a Book")
    search_by = st.selectbox("Search by", ["Title", "Author", "Year", "Genre"])
    
    if search_by == "Year":
        search_keyword = st.selectbox("Select Year", list(range(datetime.datetime.now().year, 999, -1)))
    elif search_by == "Genre":
        search_keyword = st.multiselect("Select Genre Tags:", options=list(common_genre_tags.keys()), default=[])
    else:
        search_keyword = st.text_input("Enter search keyword")
    
    if st.button("Search"):
        if search_by == "Year":
            results = [book for book in library if book[search_by] == search_keyword]
        elif search_by == "Genre":
            results = [book for book in library if any(tag.strip().lower() in [g.strip().lower() for g in book.get("Genre", [])] for tag in search_keyword)]
        else:
            results = [book for book in library if search_keyword.lower() in str(book[search_by]).lower()]
        
        if results:
            df = pd.DataFrame(results)
            df.index = range(1, len(df) + 1)
            df["Year"] = df["Year"].astype(str)
            st.dataframe(df, width=1200)
        else:
            st.warning("No books found.")

elif menu == "Display All Books":
    st.header("Your Library")
    if library:
        df = pd.DataFrame(library)
        df.index = range(1, len(df) + 1)
        df["Genre"] = df["Genre"].apply(lambda x: ", ".join(x) if isinstance(x, list) else x)
        df["Read"] = df["Read"].apply(lambda x: "✅ Read" if x else "❌ Unread")
        df["Year"] = df["Year"].astype(str)
        st.dataframe(df, width=1200)
    else:
        st.info("No books in the library.")

elif menu == "Statistics":
    st.header("Library Statistics")
    total_books = len(library)
    read_books = sum(1 for book in library if book["Read"])
    percentage_read = (read_books / total_books * 100) if total_books > 0 else 0
    st.write(f"📚 Total books: {total_books}")
    st.write(f"✅ Percentage read: {percentage_read:.2f}%")
