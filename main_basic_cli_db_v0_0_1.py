import os
import json
import datetime
import time
from pymongo import MongoClient
from dotenv import load_dotenv

# Show Loading Message
print("\nLoading... Please wait.")
time.sleep(1)  # Simulate loading time

# Load environment variables from .env
load_dotenv()

# Get MongoDB connection details from environment variables
MONGO_URI = os.getenv("MONGO_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME", "mydatabase")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "library")

# Ensure MongoDB URI is set
if not MONGO_URI:
    raise ValueError("⚠ MONGO_URI is not set in environment variables.")

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]

def load_library():
    return list(collection.find({}, {"_id": 0}))

def save_library(library):
    collection.delete_many({})
    if library:
        collection.insert_many(library)

def is_valid_year(year):
    current_year = datetime.datetime.now().year
    return year.isdigit() and 1000 <= int(year) <= current_year

def add_book(library):
    print("\n--- Add a New Book ---")
    print("(Type 'back' at any step to return to the main menu.)")

    title = input("Enter the book title: ")
    if title.lower() == "back":
        return
    
    author = input("Enter the author: ")
    if author.lower() == "back":
        return
    
    while True:
        year = input("Enter the publication year (4-digit, valid year): ")
        if year.lower() == "back":
            return
        if is_valid_year(year):
            year = int(year)
            break
        else:
            print("Invalid input. Please enter a valid 4-digit year.")

    genre = input("Enter the genre: ")
    if genre.lower() == "back":
        return

    while True:
        read_status_input = input("Have you read this book? (yes/no): ").strip().lower()
        if read_status_input == "back":
            return
        elif read_status_input in ["yes", "y"]:
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
    collection.insert_one(book)
    print("\nBook added successfully!")

def remove_book(library):
    print("\n--- Remove a Book ---")
    title = input("Enter the title of the book to remove: ")
    for book in library:
        if book["Title"].lower() == title.lower():
            library.remove(book)
            collection.delete_one({"Title": title})
            print("\nBook removed successfully!")
            return
    print("\nBook not found.")

def search_books(library):
    print("\n--- Search for a Book ---")
    print("1. Search by Title")
    print("2. Search by Author")

    choice = input("\nEnter your choice: ")
    if choice not in ["1", "2"]:
        print("Invalid choice. Returning to main menu.")
        return
    
    keyword = input("Enter search keyword: ").lower()
    results = [
        book for book in library
        if (choice == "1" and keyword in book["Title"].lower()) or (choice == "2" and keyword in book["Author"].lower())
    ]
    
    if results:
        print("\nMatching Books:")
        for book in results:
            status = "Read" if book["Read"] else "Unread"
            print(f"- {book['Title']} by {book['Author']} ({book['Year']}) - {book['Genre']} - {status}")
    else:
        print("\nNo books found.")

def display_books(library):
    print("\n--- Your Library ---")
    
    if not library:
        print("No books in the library.")
    else:
        for idx, book in enumerate(library, 1):
            status = "Read" if book["Read"] else "Unread"
            print(f"{idx}. {book['Title']} by {book['Author']} ({book['Year']}) - {book['Genre']} - {status}")

def display_statistics(library):
    print("\n--- Library Statistics ---")
    
    total_books = len(library)
    read_books = sum(1 for book in library if book["Read"])
    percentage_read = (read_books / total_books * 100) if total_books > 0 else 0
    
    print(f"Total books: {total_books}")
    print(f"Percentage read: {percentage_read:.2f}%")

def main():
    try:
        while True:
            library = load_library()
            print("\n=== Personal Library Manager ===")
            print("1. Add a book")
            print("2. Remove a book")
            print("3. Search for a book")
            print("4. Display all books")
            print("5. Display statistics")
            print("6. Exit")
            print("===============================")

            choice = input("\nEnter your choice: ")
            print("-------------------------------")

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
                print("\nLibrary saved to MongoDB. Goodbye!")
                print("-------------------------------")
                print("Press Enter to Start App Again")
                input()
                main()
            else:
                print("Invalid choice. Please try again.")
    except KeyboardInterrupt:
        print("\nExiting safely... Have a great day!\n")

if __name__ == "__main__":
    main()
