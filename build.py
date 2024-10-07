import yaml
import json
# from PyMovieDb import IMDB
import traceback
from imdb import IMDb
from liquid import Template

imdb = IMDb()

with open('data.yml', 'r') as file:
    data = yaml.safe_load(file)

with open('imdb_result.json', 'r') as file:
    imdb_result = json.load(file)

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
            imdb_result.append({
                "imdb": item['imdb'],
                "name": movie["title"],
                "country": movie["country"],
                "poster": movie["cover url"],
                "description": movie["plot"][0],
                "rating": movie["rating"],
                "genre": movie["genre"],
                "duration": movie["runtime"],
                "director": [d["name"] for d in movie["director"]],
                "actor": movie["stars"],
                "date": movie["original air date"],
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
        except:
            print(movie)
            traceback.print_exc()
            break
    with open('imdb_result.json', 'w') as file:
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
        x['date'] = x['date'].split()[2]
    html = template.render(data=imdb_result)
    with open('result.html', 'w') as file:
        file.write(html)


sanity_check()
#check_if_imdb_is_update()
#generate_html()