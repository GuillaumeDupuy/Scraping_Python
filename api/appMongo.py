from flask import Flask,render_template, request, redirect, url_for
from IPython.core.display import HTML
from flask_pymongo import PyMongo
from pymongo import MongoClient
from pathlib import Path
import pandas as pd
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

@app.route("/")
def home_page():
    cards = mongo.db.cards.find({})
    return render_template("index.html",
        cards=cards)

@app.route('/dashboard/')
def dashboard():
    cards = mongo.db.cards.find({})
    # for film in films:
    #     print(film)
    return render_template("dashboard.html",
        cards=cards)

@app.route('/upload/')
def upload():
     # Set The upload HTML template '\templates\index.html'
    return render_template('upload.html')

# Get the uploaded files
@app.route("/upload/", methods=['POST'])
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

def mongoimport(file_path,coll_name='cards', db_name='scraping',db_url='localhost', db_port=27017):
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
    app.run(debug="mongodb://localhost:27017/scraping")