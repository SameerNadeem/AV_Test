# User Stories and Exceptions

---

1. As a college student, I want to be able to see top-rated movies so I can easily get recommendations on what to watch next.  
   *Exception:* Unable to show top movies.  
   If the system is unable to retrieve the top movies, it will display an error message and prompt the user to try again later.

2. As a movie critic, I want to be able to add detailed notes on the movies I watch so I can refer back to my original opinions.  
   *Exception:* Notes exceed the allowed character limit.  
   If the notes exceed the character limit, the system will show an error and ask the user to shorten their input.

3. As an avid movie watcher, I want to store my movie ratings on a personal account online so everything is organized.  
   *Exception:* Incorrect password entered.  
   If the user enters the wrong password, they will be notified and prompted to re-enter their credentials.

4. As a data nerd, I want to see statistics about my habits so that I can analyze my viewing trends.  
   *Exception:* Statistics generation failed.  
   If stats cannot be generated, the system will notify the user to refresh the page or try again later.

5. As a friend, I want to leave comments on someone else’s shared movie list so that I can recommend or comment on the movies they added.  
   *Exception:* Not logged in or lacking comment permissions.  
   If the user is not logged in or lacks permission, they will be prompted to log in or informed that commenting is disabled.

6. As a mood-based viewer, I want to tag movies with moods (e.g., "emotional" or "feel-good") so that I can pick what to watch based on how I’m feeling.  
   *Exception:* Invalid tag input.  
   If the tag is invalid (e.g., too long or incorrectly formatted), the system will suggest valid options or allow the creation of a compliant new tag.

7. As a movie enthusiast, I want to create a detailed profile that includes personal scores, stats, and favorite genres so that I can showcase my watch history and share my movie list with others.  
   *Exception:* Invalid score input.  
   If a user inputs an out-of-range score (e.g., 11/10), they will be prompted to enter a valid value.

8. As a social user, I want to view other users' watchlists so I can discover new movies based on their suggestions.  
   *Exception:* Private watchlist access.  
   If the watchlist is private, the system will hide it and notify the viewer that access is restricted.

9. As an indecisive movie watcher, I want to add and remove movies from my watchlist so that I can keep my list updated.  
   *Exception:* Movie title not found.  
   If a movie isn’t recognized by the database, the user will be prompted to re-enter a valid title.

10. As a movie watcher, I want to filter my movies based on genre so that I can find something that matches my taste.  
   *Exception:* No results from genre filter.  
   If no movies match the selected genre, the system will notify the user and suggest a related genre.

11. As a user who wants different visual effects, I want the site to have dark mode and color customization so I can personalize my experience.  
   *Exception:* Color customization failed.  
   If color settings fail to load, the system will revert to default settings and direct the user to a help page.

12. As a bilingual user, I want to view movie titles and descriptions in another language to better understand what I am watching.  
   *Exception:* Translation unavailable.  
   If translation isn't available, the system will list supported languages and default back to English.
