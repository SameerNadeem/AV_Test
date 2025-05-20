# Api specifications

1. **POST /users/login/{user_id}**  
   a. Description: Validate a user and start the session  
   b. Body:
      ```json
      {
        "user_id": "90138976",
        "password": "secret"
      }
      ```
   c. Returns: a token

2. **POST /watchlist/{user_id}/{movie_id}**  
   a. Description: Add a movie to the user's watchlist  
   b. Body:
      ```json
      {
        "movie_id": "tt0241527",
        "status": "want to watch",
        "rating": 9,
        "notes": "Magic",
        "mood_tags": ["fantasy", "adventure"]
      }
      ```
   c. Returns: It updates the watchlist LIST  
   d. Note: https://www.imdb.com/title/tt0241527/

3. **GET /watchlist/{user_id}/watched**  
   a. Description: Get any user's watchlist for movies they've watched  
   b. Body:
      ```json
      {
        "user_id": "3910876",
        "status": "watched"
      }
      ```
   c. Returns: a list of all movies on a user's watchlist  
   d. Example return:
      ```json
      [
        {
          "movie_id": "tt0241527",
          "status": "watched",
          "rating": 9,
          "notes": "Magic",
          "mood_tags": ["fantasy", "adventure"]
        },
        {
          "movie_id": "tt0117008",
          "status": "watched",
          "rating": 10,
          "notes": "Magic",
          "mood_tags": ["whimsical"]
        }
      ]
      ```

4. **PATCH /watchlist/{user_id}/{movie_id}**  
   a. Description: Edits a user's description/rating for a particular movie  
   b. Body:
      ```json
      {
        "user_id": "349103",
        "movie_id": "tt1517268",
        "Title": "Barbie",
        "status": "watched",
        "rating": 8
      }
      ```
   c. Returns: A confirmation that the movie description was changed  
   d. Example return:
      ```json
      {"message": "Successfully updated!"}
      ```

5. **GET /watchlist/{user_id}/statistics**  
   a. Description: Generate viewing statistics for the user's most watched genres and average ratings  
   b. Body:
      ```json
      {
        "user_id": "8239012",
        "average_rating": "7.2",
        "most_common_genres": ["action", "comedy"],
        "number_watched": 22
      }
      ```
   c. Returns: The user's list of statistics about the movies they have rated

6. **GET /recommended_movies/{user_id}**  
   a. Description: Creates a list of the recommended movies based on the user's preferences.  
   b. Body:
      ```json
      [
        {
          "movie_id": "tt1517268",
          "Title": "Gladiator",
          "rating": "9.8",
          "genre": "action"
        },
        {
          "movie_id": "tt1417298",
          "Title": "Good Will Hunting",
          "rating": "9.7",
          "genre": "drama"
        }
      ]
      ```
   c. Returns: A list of top recommended movies for the user

7. **DELETE /watchlist/{user_id}/{movie_id}**  
   a. Description: Removes a specified movie from the user's watchlist  
   b. Body: Empty  
   c. Returns: Success status code (204 No Content) or deletion message  
   d. Example return:
      ```json
      {"Message": "Successfully removed movie."}
      ```

8. **GET /ratings/{movie_id}**  
   a. Description: Retrieves a list of user ratings for a specified movie  
   b. Body: Empty  
   c. Returns: List of user ratings  
   d. Example return:
      ```json
      [
        {"user_id": 1231231, "rating": 7},
        {"user_id": 3213213, "rating": 8}
      ]
      ```

9. **POST /watchlist/{user_id}/{movie_id}/{user2_id}/comment**  
   a. Description: Adds a comment under a specific user's movie rating  
   b. Body:
      ```json
      {
        "User_id": "1391810",
        "User2_id": "381739",
        "Movie_id": "tt1517268",
        "comment": "completely agree with this rating"
      }
      ```
   c. Returns: A message saying that the comment was added  
   d. Example return:
      ```json
      {"message": "comment successfully added"}
      ```

---
