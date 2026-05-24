from fastapi import FastAPI

# Create the API app
app = FastAPI()

# Your first endpoint - a simple GET request
@app.get("/")
def home():
    return {"message": "Finance API is running! 🚀"}

# A greeting endpoint with a parameter
@app.get("/greet/{name}")
def greet(name: str):
    return {"greeting": f"Hello {name}, welcome to finance bootcamp!"}

