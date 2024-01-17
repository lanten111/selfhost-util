import json
import uuid
from datetime import datetime
from urllib.parse import urlparse
from pathlib import Path
import logging
import os
import sqlite3
from requests.models import Response

from flask import Flask, request, jsonify
from flask_restful import Api

main = Flask(__name__)

# secret_key = os.environ.get('SECRET_KEY', '3456346553553445')
# main.config['JWT_SECRET_KEY'] = secret_key
# api = Api(main)
# jwt = JWTManager(main)

homarr_config_folder = os.environ.get('homarr_config_folder', Path.home() / ".self-utils")
music_config_folder = os.environ.get('music_config_folder', Path.home()  / ".self-utils")
flame_db_path = os.environ.get('flame_db_folder', Path.home() / ".self-utils")

homarr_config_file = '/homarr_config_folder/default.json'
flame_db = flame_db_path / "db.sqlite"
# flame_db = 'C:\\Users\\makha\\Downloads\\db.sqlite'
artist_list_file_path = music_config_folder / "/artist.txt"
soundtracks_list_file_path = music_config_folder / "soundtracks.txt"
podcasts_list_file_path = music_config_folder /  "podcast.txt"

@main.route('/makhadoni/api/utils', methods=['POST'])
# @jwt_required()
def utils():
    data_string = request.data.decode('utf-8')
    data_dict = json.loads(data_string)
    if data_dict["from"] == "download_spotify":
        return add_music(data_dict)
    if data_dict["from"] == "bookmark" or data_dict["from"] == "application":
        return add_bookmark_to_flame(data_dict)

def add_bookmark_to_flame(data):
    try:
        if data["from"] == "bookmark":
            bookmark = select_from_flame_db(data['url'], "url", "bookmarks")
            categories = select_from_flame_db(data['category'], "name", "categories")
            categoryid = categories[0]["id"] if categories and categories[0].get("id") is not None else 56
            if len(bookmark) != 0:
                if len(bookmark) > 1:
                    delete_row("bookmarks", "name", data['name'])
                update_row3("bookmarks", "url", "icon", "categoryId", data['url'], data['icon'], categoryid, "name", data['name'])
                logging.info("updated " + data["name"], data["url"])
            else:
                name = urlparse(data["url"]).hostname if data["name"] is None or data["name"] == "" else data["name"]
                insert_to_flame_db(name, data["url"], categoryid, data["icon"], 1, 1, "bookmark")
                logging.info("added new bookmark" + data["name"], data["url"])
        if data["from"] == "application":
            apps = select_from_flame_db(data['name'], "name", "apps")
            if len(apps) != 0:
                if len(apps) > 1:
                    delete_row("apps", "name", data['name'])
                update_row2("apps", "url", "icon", data['url'], data['icon'], "name", data['name'])
                logging.info("updated " + data["name"], data["url"])
            else:
                name = urlparse(data["url"]).hostname if data["name"] is None or data["name"] == "" else data["name"]
                insert_to_flame_db(name, data["url"], -1, data["icon"], 1, 1, "apps")
                logging.info("added new app" + data["name"], data["url"])

        response = {'status': 'success', 'message': 'File updated successfully'}
        return ('Hello, this is a custom HTTP response.', 200)
    except Exception as e:
        error_message = str(e)
        response = {'status': 'error', 'message': error_message}
        return  ('Hello, this is a custom HTTP response.', 200)

def update_row2(table_name, update_column1, update_column2, update_value1, update_value2, condition_column, condition_value):

    conn = sqlite3.connect(flame_db)
    cursor = conn.cursor()

    query = f"UPDATE {table_name} SET {update_column1} = ?, {update_column2} = ? WHERE {condition_column} = ?"
    update_params = (update_value1, update_value2, condition_value)
    cursor.execute(query, update_params)

    conn.commit()

def update_row3(table_name, update_column1, update_column2, update_column3,
               update_value1, update_value2, update_value3, condition_column, condition_value):

    conn = sqlite3.connect(flame_db)
    cursor = conn.cursor()

    query = f"UPDATE {table_name} SET {update_column1} = ?, {update_column2} = ?, {update_column3} = ? WHERE {condition_column} = ?"
    update_params = (update_value1, update_value2, update_value3, condition_value)
    cursor.execute(query, update_params)

    conn.commit()

def delete_row(table_name, condition_column, condition_value):

    conn = sqlite3.connect(flame_db)
    cursor = conn.cursor()

    query = f"DELETE FROM {table_name} WHERE {condition_column} = ?"
    cursor.execute(query, (condition_value,))

    conn.commit()



def insert_to_flame_db(name, url, categoryid, icon, ispublic, ispinned, type):
    conn = sqlite3.connect(flame_db)
    cursor = conn.cursor()
    if type == "apps":
        data_to_insert = (name, url, icon, ispinned, datetime.now(), datetime.now(), ispublic, categoryid)
        cursor.execute(
            "INSERT INTO apps (name, url, icon, isPinned, createdAt, updatedAt, isPublic, categoryId) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            data_to_insert)
    if type == "bookmark":
        data_to_insert = (name, url, categoryid, icon, datetime.now(), datetime.now(), ispublic)
        cursor.execute(
            "INSERT INTO bookmarks (name, url,categoryId, icon, createdAt, updatedAt, isPublic) VALUES (?, ?, ?, ?, ?, ?, ?)",
            data_to_insert)
    # if type == "category":
    #     data_to_insert = (name, ispinned, datetime.now(), datetime.now(), ispublic)
    #     cursor.execute(
    #         "INSERT INTO bookmarks (name, url,categoryId, icon, createdAt, updatedAt, isPublic) VALUES (?, ?, ?, ?, ?, ?, ?)",
    #         data_to_insert)
    conn.commit()
    cursor.close()
    conn.close()


def select_from_flame_db(value, column, table_name):
    conn = sqlite3.connect(flame_db)
    cursor = conn.cursor()
    query = f"SELECT * FROM {table_name} WHERE {column} COLLATE NOCASE = ?"
    cursor.execute(query, (value,))
    rows = cursor.fetchall()
    column_names = [description[0] for description in cursor.description]
    result = [dict(zip(column_names, row)) for row in rows]
    cursor.close()
    conn.close()
    return result



def add_music(data):
    try:

        artist_id = data["url"].split('/')[-1]
        if data["from"] == "add_spotify_artist":

            with open(artist_list_file_path, 'r') as file:
                existing_list = file.read().splitlines()
            existing_list.append(artist_id)

            with open(artist_list_file_path, 'w') as file:
                for item in existing_list:
                    file.write(item + '\n')
            logging.info("added new artist " + data["url"])

        if data["from"] == "add_spotify_soundtrack":

            with open(soundtracks_list_file_path, 'r') as file:
                existing_list = file.read().splitlines()
            existing_list.append(artist_id)

            with open(artist_list_file_path, 'w') as file:
                for item in existing_list:
                    file.write(item + '\n')
            logging.info("added new soundtrack " + data["url"])

        if data["from"] == "add_spotify_podcasts":

            with open(podcasts_list_file_path, 'r') as file:
                existing_list = file.read().splitlines()
            existing_list.append(data["url"])

            with open(podcasts_list_file_path, 'w') as file:
                for item in existing_list:
                    file.write(item + '\n')
            logging.info("added new podcasts " + data["url"])

        response = {'status': 'success', 'message': 'File updated successfully'}
        return jsonify(response), 200
    except Exception as e:
        error_message = str(e)
        response = {'status': 'error', 'message': error_message}
        return jsonify(response), 500



if __name__ == '__main__':
    main.run(port=5000)
