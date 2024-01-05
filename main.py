import json
import uuid
from urllib.parse import urlparse
import os

from flask import Flask, request, jsonify
from flask_cors import CORS

main = Flask(__name__)

secret_key = os.environ.get('SECRET_KEY', 'default_secret_key')
main.config['SECRET_KEY'] = secret_key

homarr_config_file = os.environ.get('SECRET_KEY', 'default_secret_key')
artist_list_file_path = os.environ.get('SECRET_KEY', 'default_secret_key')
soundtracks_list_file_path = os.environ.get('SECRET_KEY', 'default_secret_key')
podcasts_list_file_path = os.environ.get('SECRET_KEY', 'default_secret_key')



# Use the configured secret key
main.secret_key = main.config['SECRET_KEY']

@main.route('/makhadoni/api/utils', methods=['POST'])
def update_file():
    try:
        # Get JSON data from the request
        data_string = request.data.decode('utf-8')
        data_dict = json.loads(data_string)

        new_bookmark_item = {
            "id": str(uuid.uuid4()),
            "name": urlparse(data_dict["url"]).hostname if data_dict["name"] is None or data_dict["name"] == "" else data_dict["name"],
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

        if data_dict["from"] == "add_spotify_artist":

            artist_id = data_dict["url"].split('/')[-1]

            with open(artist_list_file_path, 'r') as file:
                existing_list = file.read().splitlines()
            existing_list.append(artist_id)

            with open(artist_list_file_path, 'w') as file:
                for item in existing_list:
                    file.write(item + '\n')

        if data_dict["from"] == "add_spotify_soundtrack":

            artist_id = data_dict["url"].split('/')[-1]

            with open(soundtracks_list_file_path, 'r') as file:
                existing_list = file.read().splitlines()
            existing_list.append(artist_id)

            with open(artist_list_file_path, 'w') as file:
                for item in existing_list:
                    file.write(item + '\n')

        if data_dict["from"] == "add_spotify_podcasts":

            with open(podcasts_list_file_path, 'r') as file:
                existing_list = file.read().splitlines()
            existing_list.append(data_dict["url"])

            with open(podcasts_list_file_path, 'w') as file:
                for item in existing_list:
                    file.write(item + '\n')

        response = {'status': 'success', 'message': 'File updated successfully'}
        return jsonify(response), 200

    except Exception as e:
        error_message = str(e)
        response = {'status': 'error', 'message': error_message}
        return jsonify(response), 500

if __name__ == '__main__':
    main.run(port=5000)