import requests
from bs4 import BeautifulSoup

URL = "https://web.archive.org/web/20200518073855/https://www.empireonline.com/movies/features/best-movies-2/"

# Write your code below this line 👇
response = requests.get(url=URL)
movies_webpage = response.text
soup = BeautifulSoup(movies_webpage, "html.parser")
all_movie = soup.find_all(name="h3", class_="title")
movie_titles = [movie.getText() for movie in all_movie]
movie_titles.reverse()
with open("movies.txt", mode="w", encoding="utf-8") as file:
    for title in movie_titles:
        file.write(f"{title}\n")

