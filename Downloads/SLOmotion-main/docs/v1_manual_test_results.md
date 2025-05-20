# Example Work Flow 
## Watchlist User Makes a Comment Example Flow
Bob just finished watching *Good Will Hunting* for a second time and had some thoughts about the movie. He wants to leave a comment on his friend Joe's watchlist.

- Bob calls `GET /watchlist/876543` to see Joe’s recently watched list.
- He sees *Good Will Hunting* under `movie_id tt1417298`.
- He then calls `GET /watchlist/876543/tt1417298` to view the movie entry.
- Bob submits a comment with:
  ```json
  {
    "comment": "I really connected with the character Will in the movie."
  }
  ```
- Request: `POST /watchlist/876543/tt1417298/1391810/comment`
- Server response:
  ```json
  { "message": "Comment added." }
  ```
## Get movies on user's watchlist
### `GET /watchlist/{user_id}`
Bob wants to see Joe's watchlist and knows Joe's user_id is 6
- Bob calls (Joe's id is 6):
  curl -X 'GET' \
  'https://slomotion.onrender.com/watchlist/6' \
  -H 'accept: application/json' \
  -H 'access_token: SLOmotion44'
- The server responds with the list of movies on Joe's watchlist
```json
[
  {
    "watchlist_id": 6,
    "movie_id": 254,
    "name": "A Minecraft Movie",
    "status": "want to watch"
  },
  {
    "watchlist_id": 6,
    "movie_id": 84,
    "name": "Good Will Hunting",
    "status": "watched"
  }
]
```

## Get Movie Rating by User

### `GET /watchlist/{user_id}/{movie_id}`
Bob wants to check the rating Joe gave to *Good Will Hunting*.

- Bob knows:
  - `user_id = 6`
  - `movie_id = 84`

- He sends a request to:
```bash
[GET /watchlist/6/84](http://127.0.0.1:3000/watchlist/6/84)
```

## Testing results
- Bob calls ():
  curl -X 'GET' \
  'https://slomotion.onrender.com/watchlist/6/84' \
  -H 'accept: application/json' \
  -H 'access_token: SLOmotion44'

- The server returns Joe's review, rating, and status.
  ```json
  {
  "movie_id": 84,
  "user_id": 6,
  "notes": "amazing cinematography",
  "rating": 5,
  "status": "watched"
  }
  ```

- If the input is invalid or missing, the server responds with:
  ```json
  {
    "detail": "Movie rating not found for this user."
  }
  ```
  
## Comment on Another User's Movie Rating
### 'POST /watchlist/{user_id}/{movie_id}/{user2_id}/comment'
Bob wants to leave a comment on Joe's movie review of _Good Will Hunting_
- Bob's user_id = 5, Joe's user_id = 6, and the movie_id of _Good Will Hunting_ is 84:
- Bob calls: curl -X 'POST' \
  'https://slomotion.onrender.com/watchlist/6/84/5/comment' \
  -H 'accept: */*' \
  -H 'access_token: SLOmotion44' \
  -H 'Content-Type: application/json' \
  -d '{
  "comment_text": "I agree with your rating! However, I feel like I connected more with Chuckie."
}'
- The server responds with confirmation.
  ```json
  {
  "message": "Comment added."
  }
  ```
- If the movie rating does not exist:
  ```json
  {
    "detail": "Movie rating not found for this user."
  }
  ```
