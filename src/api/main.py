from fastapi import FastAPI
from customers import router as customers_router

app = FastAPI(title="Customer Log Stats API", version="1.0.0")

app.include_router(customers_router)

@app.get("/")
def read_root():
    return {"message": "API is up and running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
