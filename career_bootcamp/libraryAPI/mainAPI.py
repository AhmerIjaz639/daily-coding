from fastapi import (HTTPException)

from fastapi import FastAPI
from pydantic import BaseModel, Field, validator
from datetime import datetime,date
from typing import Optional
from career_bootcamp.libraryAPI.databaseLibrary import get_db

app=FastAPI(
    title="Library API",
    version="0.1.0",
    description="API for tracking books"
)

class BookCreate(BaseModel):
    title:str=Field(...,min_length=1,max_length=100)
    author:str=Field(...,min_length=1,max_length=100)
    isbn:str=Field(...,min_length=1,max_length=100)

class BorrowBook(BaseModel):
    book_id:int
    borrower_name:str
    borrow_date: date
    return_date:Optional[date]=None

    @validator('return_date')
    def return_after_borrow(cls, v, values):
        if v and 'borrow_date' in values:
            if v < values['borrow_date']:
                raise ValueError('Return date must be after borrow date')
        return v

@app.post("/add_books")
def add_book(book:BookCreate):
    try:
        with get_db() as db:
            add_book_query="""
            insert into books
                (title,author,isbn,available)
                values (%s,%s,%s,True)
            """
            db.execute(add_book_query,(book.title,book.author,book.isbn))
            book_id= db.lastrowid
            return {
                    "message": "Book added successfully",
                    "book_id": book_id,
                     "title": book.title,
                     "isbn": book.isbn
                    }
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))
@app.get("/get_books")
def get_all_books():
    try:
        with get_db() as db:
            query = "SELECT * FROM books"
            db.execute(query)
            books = db.fetchall()
            return books

    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))

@app.post("/borrow_book")
def borrow_book(borrow_data:BorrowBook):
    try:
        with get_db() as db:
            check_query="""
                  select * from books where id=%s and available=True            
            """
            db.execute(check_query,(borrow_data.book_id,))
            book=db.fetchone()
            if not book:
                raise HTTPException(status_code=404,detail="Book not found")
            borrow_query="""
                   insert into borrowings
                       (book_id,borrower_name,borrow_date,return_date)
                       values(%s,%s,%s,%s)
            """
            db.execute(borrow_query,(borrow_data.book_id,borrow_data.borrower_name,borrow_data.borrow_date,borrow_data.return_date))

            update_query="""
                update books set available=False where id=%s
            """
            db.execute(update_query,(borrow_data.book_id,))
            return{
                "message": "Book borrowed successfully",
                "book_id": borrow_data.book_id,
                "borrower_name": borrow_data.borrower_name,
                "borrow_date": borrow_data.borrow_date,
            }
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))

@app.post("/return/{book_id}")
def return_book(book_id:int):
    try:
        with get_db() as db:
            return_query="""
               UPDATE books SET available=True WHERE id=%s
            """
            db.execute(return_query, (book_id,))
            remove_borrow_query = """ 
                              DELETE 
                              FROM borrowings 
                              WHERE book_id = %s 
                            """
            db.execute(remove_borrow_query, (book_id,))

            return {
                "message": "Book returned successfully",
                "Book_id": book_id,
                "return_date": datetime.now().date()
            }

    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))



@app.get("/borrowed_books")
def get_borrowed_books():
    try:
        with get_db() as db:
            query = "SELECT * FROM borrowings"
            db.execute(query)
            borrowed_books = db.fetchall()
            return borrowed_books
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/get_one_book/{book_id}")
def get_one_book(book_id:int):
    try:
        with get_db() as db:
            query = "SELECT * FROM books WHERE id=%s"
            db.execute(query,(book_id,))
            book = db.fetchone()
            return book
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))




