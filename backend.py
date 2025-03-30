from fastapi import FastAPI, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient

app = FastAPI()

MONGO_URI = "mongodb+srv://admin:Admintest123@cluster0.upudd.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = AsyncIOMotorClient(MONGO_URI)
db = client["mydatabase"]
collection = db["library"]

@app.get("/books")
async def get_books():
    books = await collection.find({}, {"_id": 0}).to_list(1000)
    return books

@app.post("/books")
async def add_book(book: dict):
    await collection.insert_one(book)
    return {"message": "Book added successfully"}

@app.delete("/books/{title}")
async def remove_book(title: str):
    result = await collection.delete_one({"Title": title})
    if result.deleted_count:
        return {"message": "Book removed successfully"}
    raise HTTPException(status_code=404, detail="Book not found")

@app.get("/search")
async def search_books(query: str):
    books = await collection.find({"Title": {"$regex": query, "$options": "i"}}, {"_id": 0}).to_list(1000)
    return books

@app.get("/stats")
async def get_stats():
    books = await collection.find({}, {"_id": 0}).to_list(1000)
    total_books = len(books)
    read_books = sum(1 for book in books if book.get("Read", False))
    return {
        "total_books": total_books,
        "read_books": read_books,
        "percentage_read": (read_books / total_books * 100) if total_books > 0 else 0
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
