import os
import json
import datetime
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Get MongoDB connection details from environment variables
MONGO_URI = os.getenv("MONGO_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME", "mydatabase")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "library")

# Ensure MongoDB URI is set
if not MONGO_URI:
    raise ValueError("⚠️ MONGO_URI is not set in environment variables.")

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]

def load_library():
    """Loads books from MongoDB instead of a text file."""
    return list(collection.find({}, {"_id": 0}))  # Fetch all books, excluding `_id`

def save_library(library):
    """Saves books to MongoDB instead of a text file."""
    collection.delete_many({})  # Clear the collection
    if library:
        collection.insert_many(library)  # Insert all books

def is_valid_year(year):
    current_year = datetime.datetime.now().year
    return year.isdigit() and 1000 <= int(year) <= current_year

def add_book(library):
    title = input("Enter the book title: ")
    author = input("Enter the author: ")
    
    while True:
        year = input("Enter the publication year (4-digit, valid year): ")
        if is_valid_year(year):
            year = int(year)
            break
        else:
            print("Invalid input. Please enter a valid 4-digit year.")
    
    genre = input("Enter the genre: ")
    
    while True:
        read_status_input = input("Have you read this book? (yes/no): ").strip().lower()
        if read_status_input in ["yes", "y"]:
            read_status = True
            break
        elif read_status_input in ["no", "n"]:
            read_status = False
            break
        else:
            print("Invalid input. Please enter 'yes' or 'no'.")

    book = {
        "Title": title,
        "Author": author,
        "Year": year,
        "Genre": genre,
        "Read": read_status
    }

    library.append(book)
    collection.insert_one(book)  # Save to MongoDB
    print("Book added successfully!")

def remove_book(library):
    title = input("Enter the title of the book to remove: ")
    for book in library:
        if book["Title"].lower() == title.lower():
            library.remove(book)
            collection.delete_one({"Title": title})  # Remove from MongoDB
            print("Book removed successfully!")
            return
    print("Book not found.")

def search_books(library):
    while True:
        choice = input("Search by:\n1. Title\n2. Author\nEnter your choice: ")
        if choice in ["1", "2"]:
            break
        else:
            print("Invalid choice. Please enter 1 or 2.")

    keyword = input("Enter search keyword: ").lower()
    results = [
        book for book in library
        if (choice == "1" and keyword in book["Title"].lower()) or (choice == "2" and keyword in book["Author"].lower())
    ]
    
    if results:
        print("Matching Books:")
        for book in results:
            status = "Read" if book["Read"] else "Unread"
            print(f"{book['Title']} by {book['Author']} ({book['Year']}) - {book['Genre']} - {status}")
    else:
        print("No books found.")

def display_books(library):
    if not library:
        print("📭 No books in the library.")
        return
    print("\n📚 Your Library:")
    for idx, book in enumerate(library, 1):
        status = "Read" if book["Read"] else "Unread"
        print(f"{idx}. {book['Title']} by {book['Author']} ({book['Year']}) - {book['Genre']} - {status}")

def display_statistics(library):
    total_books = len(library)
    read_books = sum(1 for book in library if book["Read"])
    percentage_read = (read_books / total_books * 100) if total_books > 0 else 0
    print(f"📖 Total books: {total_books}")
    print(f"✅ Books read: {read_books}")
    print(f"📊 Percentage read: {percentage_read:.2f}%")
def main():
    while True:
        library = load_library()
        while True:
            print("\n📚 Personal Library Manager")
            print("1. Add a book")
            print("2. Remove a book")
            print("3. Search for a book")
            print("4. Display all books")
            print("5. Display statistics")
            print("6. Exit")
            
            choice = input("Enter your choice: ")
            if choice == "1":
                add_book(library)
            elif choice == "2":
                remove_book(library)
            elif choice == "3":
                search_books(library)
            elif choice == "4":
                display_books(library)
            elif choice == "5":
                display_statistics(library)
            elif choice == "6":
                save_library(library)
                print("Library saved to MongoDB. Goodbye!\n")
                print("Press Enter to Start App Again")
                input()
                main()
            else:
                print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
