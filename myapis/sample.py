from fastapi import FastAPI

# Create the app instance
app = FastAPI(title="My First API")

# Define a GET route at the root URL
@app.get("/")
def home():
    return {"message": "Hello from FastAPI!"}

@app.get("/greet")
def greet(name: str):
    return {"message": f"Hello, {name}!"}

@app.get("/age")
def age(age: int):
    return {"message": f"Your age is {age}"}
