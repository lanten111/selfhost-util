import json
import uuid
from datetime import datetime
from urllib.parse import urlparse
import logging
import os
import sqlite3

from flask import Flask, request, jsonify
from flask_restful import Api

main = Flask(__name__)

# secret_key = os.environ.get('SECRET_KEY', '3456346553553445')
# main.config['JWT_SECRET_KEY'] = secret_key
# api = Api(main)
# jwt = JWTManager(main)

homarr_config_folder = os.environ.get('homarr_config_folder', '/homarr_config_folder')
music_config_folder = os.environ.get('music_config_folder', '/music_config_folder')
flame_db_path = os.environ.get('flame_db_folder', '/flame_db_folder')

homarr_config_file = '/homarr_config_folder/default.json'
flame_db = flame_db_path + "/" + "db.sqlite"
# flame_db = 'C:\\Users\\makha\\Downloads\\db.sqlite'
artist_list_file_path = music_config_folder + "/" + "/artist.txt"
soundtracks_list_file_path = music_config_folder + "/" + "soundtracks.txt"
podcasts_list_file_path = music_config_folder + "/" + "podcast.txt"

@main.route('/makhadoni/api/utils', methods=['POST'])
# @jwt_required()
def utils():
    data_string = request.data.decode('utf-8')
    data_dict = json.loads(data_string)
    if data_dict["from"] == "add_spotify_artist" or data_dict["from"] == "add_spotify_soundtrack" or data_dict["from"] == "add_spotify_podcasts":
        return add_music(data_dict)
    if data_dict["from"] == "bookmark" or data_dict["from"] == "bookmark_local" or data_dict["from"] == "bookmark_online" or data_dict["from"] == "bookmark_tailscale":
        return add_bookmark_to_flame(data_dict)


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


def add_bookmark_to_flame(data):
    try:
        if data["from"] == "bookmark":
            categories = select_from_flame_db(data['category'], "categories")
            categoryid = categories[0]["id"] if categories and categories[0].get("id") is not None else ""
            name = urlparse(data["url"]).hostname if data["name"] is None or data["name"] == "" else data["name"]
            insert_to_flame_db(name, data["url"], categoryid, data["icon"], 1, 1, "bookmark")
            logging.info("added new bookmark"+ data["name"], data["url"])
        if data["from"] == "bookmark_local":
            name = urlparse(data["url"]).hostname if data["name"] is None or data["name"] == "" else data["name"]
            insert_to_flame_db(name, data["url"], -1, data["icon"], 1, 1, "apps")
            logging.info("added new bookmark" + data["name"], data["url"])
        if data["from"] == "bookmark_online":
            name = urlparse(data["url"]).hostname if data["name"] is None or data["name"] == "" else data["name"]
            categories = select_from_flame_db(data['category'], "categories")
            categoryid = categories[0]["id"] if categories and categories[0].get("id") is not None else ""
            insert_to_flame_db(name, data["url"], categoryid, data["icon"], 1, 1, "bookmark")
            logging.info("added new bookmark" + data["name"], data["url"])
        response = {'status': 'success', 'message': 'File updated successfully'}
        return jsonify(response), 200
    except Exception as e:
        error_message = str(e)
        response = {'status': 'error', 'message': error_message}
        return jsonify(response), 500


def add_bookmark_to_homarr(data):
    try:
        # Get JSON data from the request
        data_string = request.data.decode('utf-8')
        data_dict = json.loads(data_string)

        new_bookmark_item = {
            "id": str(uuid.uuid4()),
            "name": urlparse(data_dict["url"]).hostname if data_dict["name"] is None or data_dict["name"] == "" else
            data_dict["name"],
            "href": data_dict["url"],
            "iconUrl": data_dict["icon"],
            "openNewTab": True,
            "hideHostname": True,
            "hideIcon": False
        }

        if data_dict["from"] == "bookmark":

            with open(homarr_config_file, 'r', encoding='utf-8') as file:
                config_json = json.load(file)
            for item in config_json["widgets"]:
                if item["properties"].get("name", None) == "bookmark":
                    item["properties"]["items"].append(new_bookmark_item)

            with open(homarr_config_file, 'w', encoding='utf-8') as file:
                json.dump(config_json, file, indent=2)

        if data_dict["from"] == "bookmark_online":

            with open(homarr_config_file, 'r', encoding='utf-8') as file:
                config_json = json.load(file)
            for item in config_json["widgets"]:
                if item["properties"].get("name", None) == "online":
                    item["properties"]["items"].append(new_bookmark_item)

            with open(homarr_config_file, 'w', encoding='utf-8') as file:
                json.dump(config_json, file, indent=2)

        if data_dict["from"] == "bookmark_online_local":

            with open(homarr_config_file, 'r', encoding='utf-8') as file:
                config_json = json.load(file)
            for item in config_json["widgets"]:
                if item["properties"].get("name", None) == "tailscale":
                    item["properties"]["items"].append(new_bookmark_item)

            with open(homarr_config_file, 'w', encoding='utf-8') as file:
                json.dump(config_json, file, indent=2)

        if data_dict["from"] == "bookmark_local":
            new_local_bookmark_item = {
                "id": str(uuid.uuid4()),
                "name": urlparse(data_dict["url"]).hostname if data_dict["name"] is None or data_dict["name"] == "" else
                data_dict["name"],
                "url": data_dict["url"],
                "appearance": {
                    "iconUrl": data_dict["icon"],
                    "appNameStatus": "normal",
                    "positionAppName": "column",
                    "lineClampAppName": 1,
                    "appNameFontSize": 16
                },
                "network": {
                    "enabledStatusChecker": True,
                    "statusCodes": [
                        "200",
                        "301",
                        "302",
                        "304",
                        "307",
                        "308"
                    ]
                },
                "behaviour": {
                    "isOpeningNewTab": True,
                    "externalUrl": data_dict["url"]
                },
                "area": {
                    "type": "wrapper",
                    "properties": {
                        "id": "default"
                    }
                },
                "shape": {
                    "lg": {
                        "location": {
                            "x": 4,
                            "y": 0
                        },
                        "size": {
                            "width": 1,
                            "height": 1
                        }
                    },
                    "md": {
                        "location": {
                            "x": 4,
                            "y": 0
                        },
                        "size": {
                            "width": 1,
                            "height": 1
                        }
                    },
                    "sm": {
                        "location": {
                            "x": 3,
                            "y": 3
                        },
                        "size": {
                            "width": 1,
                            "height": 1
                        }
                    }
                },
                "integration": {
                    "type": "null",
                    "properties": []
                }
            }

            with open(homarr_config_file, 'r', encoding='utf-8') as file:
                config_json = json.load(file)
                config_json["apps"].append(new_local_bookmark_item)

            with open(homarr_config_file, 'w', encoding='utf-8') as file:
                json.dump(config_json, file, indent=2)

        response = {'status': 'success', 'message': 'File updated successfully'}
        return jsonify(response), 200

    except Exception as e:
        error_message = str(e)
        response = {'status': 'error', 'message': error_message}
        return jsonify(response), 500


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
    conn.commit()
    cursor.close()
    conn.close()


def select_from_flame_db(value, table_name):
    conn = sqlite3.connect(flame_db)
    cursor = conn.cursor()
    query = f"SELECT * FROM {table_name} WHERE name COLLATE NOCASE = ?"
    cursor.execute(query, (value,))
    rows = cursor.fetchall()
    column_names = [description[0] for description in cursor.description]
    result = [dict(zip(column_names, row)) for row in rows]
    cursor.close()
    conn.close()
    return result


if __name__ == '__main__':
    main.run(port=5000)
