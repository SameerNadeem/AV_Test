# 3 Distinct Example Flows
---
## 1. Watchlist User Makes a Comment Example Flow
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

## 2. Watchlist User Looks for a Movie to Watch Example Flow
Alice finishes watching *Barbie* and updates its status in her watchlist. She then checks Bob's watchlist and finally gets new recommendations for herself.

- Alice calls `PATCH /watchlist/456219/tt1517268`
  ```json
  {
    "user_id": "456219",
    "movie_id": "tt1517268",
    "status": "watched",
    "rating": 8
  }
  ```
- Server response:
  ```json
  { "message": "Successfully updated!" }
  ```
- Alice calls `GET /watchlist/876543/watched`
  ```json
  {
    "user_id": "876543",
    "status": "watched"
  }
  ```
- Server response:
 ```json
 [
   {
      "movie_id": "tt1517268",
      "title": "Gladiator",
      "status": "watched",
      "rating": "9.8",
      "genre": "action"
    },
    {
      "movie_id": "tt1417298",
      "title": "Good Will Hunting",
      "status": "watched",
      "rating": "9.7",
      "genre": "drama"
    }
 ]
``` 
- She then calls `GET /recommended_movies/456219` to receive personalized recommendations.

## 3. Watchlist User Adds and Removes Movies Example Flow
Eve gets a recommendation to watch *A Minecraft Movie*, but later changes her mind.

- Eve calls `GET /ratings/tt3566834` and sees strong user ratings.
- She adds the movie using `POST /watchlist/376541/tt3566834`
  ```json
  {
    "user_id": "376541",
    "movie_id": "tt3566834",
    "status": "want to watch"
  }
  ```
- After watching, Eve decides to remove it using:
  `DELETE /watchlist/376541/tt3566834`
- Server responds:
  ```json
  { "Message": "Successfully removed movie." }
  ```


