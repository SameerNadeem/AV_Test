from fastapi import FastAPI
from src.api import user, watchlist, recommended, movies
from starlette.middleware.cors import CORSMiddleware

description = """
SLOmotion allows you to track movies.
"""
tags_metadata = [
    {"name": "user", "description": "Create a user account"},
    {"name": "watchlist", "description": "View and comment on watchlists."},
    {"name": "recommended", "description": "Get recommended movies based on your watchlist"},
    {"name": "movies", "description": "Get information on specific movies"}
]

app = FastAPI(
    title="SLOmotion",
    description=description,
    version="0.0.1",
    terms_of_service="http://example.com/terms/",
    # contact={
    #     "name": "Lucas Pierce",
    #     "email": "lupierce@calpoly.edu",
    # },
    openapi_tags=tags_metadata,
)

origins = ["https://potion-exchange.vercel.app"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(user.router)
app.include_router(watchlist.router)
app.include_router(recommended.router)
app.include_router(movies.router)


@app.get("/")
async def root():
    return {"message": "Shop is open for business!"}
