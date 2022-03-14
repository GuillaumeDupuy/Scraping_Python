from flask import Flask,render_template, request, redirect, url_for,jsonify, json, Response
from IPython.core.display import HTML
from flask_pymongo import PyMongo
from pymongo import MongoClient
from pathlib import Path
import pandas as pd
from MongoAPI import *
from bs4 import *
import requests 
import pymongo
import os
import csv
import json

app = Flask(__name__)

app.config["MONGO_URI"] = "mongodb://localhost:27017/scraping"
mongo = PyMongo(app)

# Upload folder
UPLOAD_FOLDER = 'static/files'
app.config['UPLOAD_FOLDER'] =  UPLOAD_FOLDER

@app.route("/", methods=['GET', 'POST'])
def home_page():
    return render_template("index.html")

@app.route("/db_post/", methods=['GET', 'POST'])
def db_post():
    donnes = MongoClient('localhost',27017)[str(request.form['db'])][str(request.form['coll'])].find({})
    return render_template("db_post.html",
        donnes=donnes)

@app.route('/mongodb/get', methods=['GET'])
def mongo_read():
    data = request.json
    if data is None or data == {}:
        return Response(response=json.dumps({"Error": "Please provide connection information"}),
                        status=400,
                        mimetype='application/json')
    obj1 = MongoAPI(data)
    response = obj1.read()
    return Response(response=json.dumps(response),
                    status=200,
                    mimetype='application/json')

@app.route('/mongodb/post', methods=['POST'])
def mongo_write():
    data = request.json
    if data is None or data == {} or 'Document' not in data:
        return Response(response=json.dumps({"Error": "Please provide connection information"}),
                        status=400,
                        mimetype='application/json')
    obj1 = MongoAPI(data)
    response = obj1.write(data)
    return Response(response=json.dumps(response),
                    status=200,
                    mimetype='application/json')
                
@app.route('/mongodb/put', methods=['PUT'])
def mongo_update():
    data = request.json
    if data is None or data == {} or 'Updated' not in data:
        return Response(response=json.dumps({"Error": "Please provide connection information"}),
                        status=400,
                        mimetype='application/json')
    obj1 = MongoAPI(data)
    response = obj1.update()
    return Response(response=json.dumps(response),
                    status=200,
                    mimetype='application/json')
                
@app.route('/mongodb/delete', methods=['DELETE'])
def mongo_delete():
    data = request.json
    if data is None or data == {} or 'Filter' not in data:
        return Response(response=json.dumps({"Error": "Please provide connection information"}),
                        status=400,
                        mimetype='application/json')
    obj1 = MongoAPI(data)
    response = obj1.delete(data)
    return Response(response=json.dumps(response),
                    status=200,
                    mimetype='application/json')

@app.route("/db/")
def db():
    cards = mongo.db.cards.find({})
    return render_template("db.html",
        cards=cards)

@app.route('/post_filtre/', methods=['GET', 'POST'])
def post_filtre(): 
    return render_template('post_filtre.html')

@app.route('/affich_filtre/', methods=['GET', 'POST'])
def affich_filtre():  
    cards = mongo.db.cards.find({})
    df = pd.DataFrame.from_records(cards)
    df = df.drop(["_id"], axis=1)
    cards_dict = df.to_dict()

    # for key,values in cards_dict.items():
    # rang.append(values) 
    # print(key)

    nom = []   
    for values in cards_dict['Nom'].items():
        nom.append(values) 
        # print(values)

    rang = []
    for values in cards_dict['Rang'].items():
        rang.append(values) 
        # print(values) 

    note = []
    for values in cards_dict['Notation /100'].items():
        note.append(values) 
        # print(values) 

    use = []
    for values in cards_dict['Utilisation %'].items():
        use.append(values) 
        # print(values) 

    vic = []
    for values in cards_dict['Victoire %'].items():
        vic.append(values) 
        # print(values)
    
    img = []
    for values in cards_dict['Image'].items():
        img.append(values) 
        # print(values) 

    # print(nom[int(request.form['number'])][1])

    # print(cards_dict['Nom'][0])
    # print(str(request.form['number']))

    # filtre = filter_set(test[int(request.form['number'])][1],str(request.form['input']))
    # filtre = list(filtre)
    # print(filtre)

    name = filter_set(nom, str(request.form['carte'].capitalize()))
    name = list(name)

    index = []
    for i in name:
        index.append(i[0])
        # print(index)

    rank = []
    for x in range(len(index)):   
        rank.append(rang[index[x]])
        # print(index[x])

    notes = []
    for x in range(len(index)):   
        notes.append(note[index[x]])
        # print(index[x])

    uses = []
    for x in range(len(index)):   
        uses.append(use[index[x]])
        # print(index[x])
    
    win = []
    for x in range(len(index)):   
        win.append(vic[index[x]])
        # print(index[x])

    imgs = []
    for x in range(len(index)):   
        imgs.append(img[index[x]])
        # print(index[x])

    search = []
    for x in range(len(index)):
        search.append(name[x])
        search.append(img[index[x]])
        search.append(rang[index[x]])
        search.append(note[index[x]])
        search.append(use[index[x]])
        search.append(vic[index[x]])

    chunked_list = list()
    chunk_size = 6
    for i in range(0, len(search), chunk_size):
        chunked_list.append(search[i:i+chunk_size])

    # name = nom[int(request.form['carte'])][1]
    # rank = rang[int(request.form['carte'])][1]
    # notes = note[int(request.form['carte'])][1]
    # uses = use[int(request.form['carte'])][1]
    # win = vic[int(request.form['carte'])][1]
    # imgs = img[int(request.form['carte'])][1]

    # return render_template('affich_filtre.html',name=name,rank=rank,notes=notes,uses=uses,win=win,imgs=imgs)
    return render_template('affich_filtre.html',search=chunked_list)

def filter_set(cards_dict, search_string):
    # print(cards_dict)
    # print(search_string)
    def iterator_func(x):
        # print(x)
        for v in x:
            if search_string in str(v):
                return True
        return False
    return filter(iterator_func, cards_dict)

@app.route('/brut/')
def dashboard():
    cards = mongo.db.cards.find({})
    # for cards in cards:
    #     print(cards)
    return render_template("brut.html",
        cards=cards)

@app.route('/upload/')
def upload():
     # Set The upload HTML template '\templates\index.html'
    return render_template('upload.html')

# Get the uploaded files
@app.route("/upload/", methods=['GET', 'POST'])
def uploadFiles():
      # get the uploaded file
      uploaded_file = request.files['file']
      if uploaded_file.filename != '':
           file_path = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file.filename)
          # set the file path
           uploaded_file.save(file_path)
           mongoimport(file_path)
          # save the file
      return redirect(url_for('upload'))

def mongoimport(file_path,coll_name='cards', db_name='scraping2',db_url='localhost', db_port=27017):
    client = MongoClient(db_url, db_port)
    db = client[db_name]
    coll = db[coll_name]
    data = pd.read_csv(file_path)
    data = data.rename(columns={'1': 'Nom', '2': 'Rang', '3': 'Notation /100', '4': 'Utilisation %', '5': 'Victoire %'})
    data = data.drop(["Unnamed: 0"], axis=1)
    data["Utilisation %"] = data["Utilisation %"].replace('\%','',regex=True).astype(int)
    data["Victoire %"] = data["Victoire %"].replace('\%','',regex=True).astype(int)
    # target URL
    url = "https://royaleapi.com/cards/popular?time=7d&mode=grid&cat=TopLadder&sort=rating"

    headers = {
        'User-Agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36"
        }

    response = requests.request("GET", url, headers=headers)

    img = BeautifulSoup(response.text, 'html.parser')

    # find all with the image tag
    images = img.find_all('img', src=True)

    # select src tag
    image_src = [x['src'] for x in images]

    # select format images
    image_src = [x for x in image_src if x.startswith('https://cdn.royaleapi.com/static/img/cards-150/')]

    image = image_src
    data['Image'] = image

    # Rendering the dataframe as HTML table
    data.to_html(escape=False, formatters=dict(Image=path_to_image_html))
    HTML(data.to_html(escape=False,formatters=dict(Image=path_to_image_html)))

    payload = data.to_dict('records')
    coll.drop()
    coll.insert_many(payload)
    return coll

def path_to_image_html(path):
    return '<img src="'+ path + '" width="60" >'

if __name__ == "__main__":
    app.run(debug="mongodb://localhost:27017/")