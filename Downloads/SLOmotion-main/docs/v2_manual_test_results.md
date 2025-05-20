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

## Testing results for flow 2
Alice updates Barbie to "watched" in her watchlist.
curl -X 'PATCH' \
  'https://slomotion.onrender.com/watchlist/4/254' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -H 'access_token: SLOmotion44' \
  -d '{
    "user_id": 4,
    "movie_id": 254,
    "status": "watched",
    "rating": 8,
    "notes": "Great movie, would watch again!"
  }'

Server response:
```json
{
  "message": "Successfully updated!"
}
```

To check Bob's watchlist she calls `GET /watchlist/5/watched` since Bob's user_id is 5.

curl -X 'GET' \
  'https://slomotion.onrender.com/watchlist/5/watched' \
  -H 'accept: application/json' \
  -H 'access_token: SLOmotion44'

Server response:
```json
 [
  {
    "movie_id": 40,
    "title": "Gladiator",
    "status": "watched",
    "rating": 6,
    "genre": "Action"
  },
  {
    "movie_id": 84,
    "title": "Good Will Hunting",
    "status": "watched",
    "rating": 7,
    "genre": "Drama"
  }
]
```
Alic calls `GET /recommended_movies/4` (her user_id is 4)

curl -X 'GET' \
  'https://slomotion.onrender.com/recommended_movies/4' \
  -H 'accept: application/json' \
  -H 'access_token: SLOmotion44'

  Server response:
  ```json
  [
    {
      "movie_id": 29,
      "name": "Life Is Beautiful",
      "genre": "Comedy"
    },
    {
      "movie_id": 50,
      "name": "Modern Times",
      "genre": "Comedy"
    },
    {
      "movie_id": 55,
      "name": "City Lights",
      "genre": "Comedy"
    },
    {
      "movie_id": 65,
      "name": "The Great Dictator",
      "genre": "Comedy"
    },
    {
      "movie_id": 71,
      "name": "Dr. Strangelove or: How I Learned to Stop Worrying and Love the Bomb",
      "genre": "Comedy"
    }
  ]
  ```

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

## Testing results for flow 3

Eve calls `GET /movies/ratings/254` to view the rating for *A Minecraft Movie*.

curl -X 'GET' \
  'https://slomotion.onrender.com/movies/ratings/254' \
  -H 'accept: application/json' \
  -H 'access_token: SLOmotion44'

Server response:
```json
[
  {
    "user_id": 4,
    "rating": 10
  },
  {
    "user_id": 5,
    "rating": 9
  }
]
```

Eve adds the movie by calling POST /watchlist/7/254.
curl -X 'POST' \
  'https://slomotion.onrender.com/watchlist/7/254' \
  -H 'accept: */*' \
  -H 'access_token: SLOmotion44' \
  -H 'Content-Type: application/json' \

```json
{
  "rating": null,
  "notes": "Can't Wait!",
  "status": "want to watch"
}
```

Server response:
 ```json
{
  "message": "Successfully added movie to watchlist."
}

```
Eve changes her mind and removes the movie with DELETE /watchlist/7/254.
curl -X 'DELETE' \
  'https://slomotion.onrender.com/watchlist/7/254' \
  -H 'accept: application/json' \
  -H 'access_token: SLOmotion44'

Server response:
```json
{
  "Message": "Successfully removed movie."
}
```

