from fastapi import FastAPI

app = FastAPI()

# app.include_router(inventory.router, prefix="/inventory")
# app.include_router(recipes.router, prefix="/recipes")

@app.get("/")
def root():
    return {"status": "PantryVision API is running YAY"}

@app.get("/health")
def health():
    return {"status": "ok"}