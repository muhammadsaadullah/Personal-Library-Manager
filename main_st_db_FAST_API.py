import datetime
import streamlit as st
import pandas as pd
import requests

API_URL = "http://localhost:8000"  # Change to your deployed FastAPI URL later

@st.cache_data(ttl=300)
def load_library():
    response = requests.get(f"{API_URL}/books")
    return response.json() if response.status_code == 200 else []

def add_book(title, author, year, genre, read_status):
    book = {
        "Title": title,
        "Author": author,
        "Year": int(year),
        "Genre": genre,
        "Read": read_status == "Yes"
    }
    requests.post(f"{API_URL}/books", json=book)

def remove_book(title):
    requests.delete(f"{API_URL}/books/{title}")

def search_books(query):
    response = requests.get(f"{API_URL}/search", params={"query": query})
    return response.json() if response.status_code == 200 else []

def get_stats():
    response = requests.get(f"{API_URL}/stats")
    return response.json() if response.status_code == 200 else {}

st.set_page_config(layout="wide")
st.title("📚 Personal Library Manager")

if "library" not in st.session_state:
    with st.spinner("Loading Library..."):
        st.session_state.library = load_library()

library = st.session_state.library

menu = st.radio("Select an Option:", ["Add Book", "Remove Book", "Search Book", "Display All Books", "Statistics"], horizontal=True)

if menu == "Add Book":
    st.header("Add a New Book")
    title = st.text_input("Book Title")
    author = st.text_input("Author")
    year = st.selectbox("Publication Year", list(range(datetime.datetime.now().year, 999, -1)))
    genre_input = st.text_input("Enter genres (comma-separated)")
    genre = [g.strip().lower() for g in genre_input.split(",") if g.strip()]
    read_status = st.selectbox("Have you read this book?", ("Yes", "No"))
    
    if st.button("Add Book"):
        if title and author:
            add_book(title, author, year, genre, read_status)
            st.success("Book added successfully!")
            st.session_state.library = load_library()
        else:
            st.error("Please enter valid book details!")

elif menu == "Remove Book":
    st.header("Remove a Book")
    book_titles = [book["Title"] for book in library]
    if book_titles:
        selected_book = st.selectbox("Select book to remove", ["Select a book"] + book_titles, index=0)
        if st.button("Remove Book"):
            if selected_book != "Select a book":
                remove_book(selected_book)
                st.success("Book removed successfully!")
                st.session_state.library = load_library()
            else:
                st.error("Please select a valid book to remove.")
    else:
        st.info("No books available to remove.")

elif menu == "Search Book":
    st.header("Search for a Book")
    search_query = st.text_input("Enter search keyword")
    
    if st.button("Search"):
        results = search_books(search_query)
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
    stats = get_stats()
    total_books = stats.get("total_books", 0)
    read_books = stats.get("read_books", 0)
    percentage_read = stats.get("percentage_read", 0)
    st.write(f"📚 Total books: {total_books}")
    st.write(f"✅ Percentage read: {percentage_read:.2f}%")
