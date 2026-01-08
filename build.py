import yaml
import json
# from PyMovieDb import IMDB
import traceback
from imdb import IMDb
from liquid import Template
import os

imdb = IMDb()

with open('data.yml', 'r') as file:
    data = yaml.safe_load(file)

imdb_result = []

for i in range(len(data)):
    print(i + 1, data[i]["name"])

def sanity_check():
    d = {}
    for item in data:
        if item['imdb'] in d:
            print(f"duplicate imdb {item['imdb']}: {item['name']} and {d[item['imdb']]}")
            exit(0)
        d[item['imdb']] = item['name']

def emit_imdb(from_idx):
    global imdb_result
    imdb_result = imdb_result[:from_idx]
    for item in data[from_idx:]:
        try:
            print(f"fetching {item['name']}")
            # movie = imdb.get_by_id(item["imdb"])
            # movie = json.loads(movie)
            movie = imdb.get_movie(item["imdb"][2:])

            # Safely get values with defaults for missing fields
            country = movie.get("countries", ["N/A"])[0] if movie.get("countries") else "N/A"
            poster = movie.get("cover url", movie.get("full-size cover url", ""))
            plot = movie.get("plot", ["No description available."])[0] if movie.get("plot") else "No description available."
            rating = movie.get("rating", "N/A")
            genres = movie.get("genres", ["N/A"])
            runtime = movie.get("runtimes", ["N/A"])[0] if movie.get("runtimes") else "N/A"
            directors = [d.get("name", "Unknown") for d in movie.get("directors", [])] if movie.get("directors") else ["Unknown"]
            original_air_date = movie.get("original air date", movie.get("year", "N/A"))

            imdb_result.append({
                "imdb": item['imdb'],
                "name": movie.get("title", item["name"]),  # fallback to name from data.yml
                "country": country,
                "poster": poster,
                "description": plot,
                "rating": rating,
                "genre": genres,
                "duration": runtime,
                "director": directors,
                "actor": [], #movie["stars"],
                "date": original_air_date,
            })
            # print(movie)
            # if "status" in movie and movie["status"] == 404:
            #     print(f"Warn: not found {item['name']}")
            #     imdb_result.append({
            #         "imdb": item['imdb'],
            #         "name": item["name"],
            #     })
            # else:
            #     imdb_result.append({
            #         "imdb": item['imdb'],
            #         "name": movie["name"],
            #         "poster": movie["poster"],
            #         "description": movie["description"],
            #         "rating": movie["rating"]["ratingValue"],
            #         "genre": movie["genre"],
            #         "duration": movie["duration"],
            #         "director": [d["name"] for d in movie["director"]],
            #         "actor": [d["name"] for d in movie["actor"]],
            #     })
        except Exception as e:
            print(f"Error processing {item['name']}: {str(e)}")
            traceback.print_exc()
            break
    with open('dist/imdb_result.json', 'w') as file:
        json.dump(imdb_result, file)
                

def check_if_imdb_is_update():
    for i in range(len(imdb_result)):
        if imdb_result[i]['imdb'] != data[i]['imdb']:
            print(f"not updated for {data[i]['imdb']}")
            emit_imdb(i)
    if len(imdb_result) != len(data):
        print(f"not updated is imdb_result.json")
        emit_imdb(len(imdb_result))

def generate_html():
    with open('template.html', 'r') as file:
        template = file.read()
    template = Template(template)
    for x in imdb_result:
        # Handle date parsing more safely
        if isinstance(x['date'], str) and x['date'] != 'N/A':
            date_parts = x['date'].split()
            if len(date_parts) >= 3:
                x['date'] = date_parts[2]  # year is typically the third element
            elif len(date_parts) == 1:
                x['date'] = date_parts[0]  # if only year is provided
        # If date is 'N/A' or not properly formatted, leave it as is
    html = template.render(data=imdb_result)
    with open('dist/index.html', 'w') as file:
        file.write(html)

os.system("rm -rf dist")
os.system("mkdir dist")
sanity_check()
check_if_imdb_is_update()
generate_html()
