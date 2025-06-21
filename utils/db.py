#  CybroX-UserBot - telegram userbot
#  Copyright (C) 2025 CybroX UserBot Organization
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.

#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.

#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

import re
import json
import threading
import sqlite3
from dns import resolver
import pymongo
from utils import config

resolver.default_resolver = resolver.Resolver(configure=False)
resolver.default_resolver.nameservers = ["1.1.1.1"]


class Database:
    def __init__(self):
        self.db_type = config.db_type.lower().strip()
        if self.db_type in ["mongo", "mongodb"]:
            self._mongo_init()
        elif self.db_type in ["sqlite", "sqlite3"]:
            self._sqlite_init()
        else:
            raise RuntimeError(
                f"Unknown database type: {self.db_type}. "
                "Expected: mongo, mongodb, sqlite or sqlite3"
            )

    def _mongo_init(self):
        self.db_name = config.db_name.strip()
        self.db_url = config.db_url.strip()

        self.mongo_client = pymongo.MongoClient(self.db_url)
        self.mongo_db = self.mongo_client[self.db_name]

        self._lock = threading.Lock()

    def _sqlite_init(self):
        self.db_name = config.db_name.strip()
        self.connection = sqlite3.connect(self.db_name, check_same_thread=False)
        self.cursor = self.connection.cursor()
        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS data (section TEXT, key TEXT, value TEXT)"
        )
        self.connection.commit()
        self._lock = threading.Lock()

    def get(self, section: str, key: str, default=None):
        if self.db_type in ["mongo", "mongodb"]:
            return self._mongo_get(section, key, default)
        else:
            return self._sqlite_get(section, key, default)

    def set(self, section: str, key: str, value):
        if self.db_type in ["mongo", "mongodb"]:
            return self._mongo_set(section, key, value)
        else:
            return self._sqlite_set(section, key, value)

    def remove(self, section: str, key: str):
        if self.db_type in ["mongo", "mongodb"]:
            return self._mongo_remove(section, key)
        else:
            return self._sqlite_remove(section, key)

    def get_collection(self, name: str):
        if self.db_type in ["mongo", "mongodb"]:
            return self.mongo_db[name]
        else:
            raise RuntimeError(
                "Collection is only available for mongo database type"
            )

    def _mongo_get(self, section: str, key: str, default=None):
        with self._lock:
            collection = self.mongo_db[section]
            result = collection.find_one({"_id": key})
            if result:
                return result.get("value", default)
            return default

    def _mongo_set(self, section: str, key: str, value):
        with self._lock:
            collection = self.mongo_db[section]
            return collection.update_one(
                {"_id": key}, {"$set": {"value": value}}, upsert=True
            )

    def _mongo_remove(self, section: str, key: str):
        with self._lock:
            collection = self.mongo_db[section]
            return collection.delete_one({"_id": key})

    def _sqlite_get(self, section: str, key: str, default=None):
        with self._lock:
            self.cursor.execute(
                "SELECT value FROM data WHERE section = ? AND key = ?",
                (section, key),
            )
            result = self.cursor.fetchone()
            if result is None:
                return default

            value = result[0]
            if re.match(r"^\[.*\]$", value) or re.match(r"^\{.*\}$", value):
                try:
                    return json.loads(value)
                except Exception:
                    pass
            elif value.lower() == "true":
                return True
            elif value.lower() == "false":
                return False
            elif value.isdigit():
                return int(value)
            elif value.replace(".", "", 1).isdigit():
                return float(value)
            return value

    def _sqlite_set(self, section: str, key: str, value):
        with self._lock:
            if isinstance(value, (dict, list, tuple)):
                value = json.dumps(value)
            elif isinstance(value, bool):
                value = "true" if value else "false"
            elif isinstance(value, (int, float)):
                value = str(value)

            self.cursor.execute(
                "SELECT value FROM data WHERE section = ? AND key = ?",
                (section, key),
            )
            result = self.cursor.fetchone()
            if result is None:
                self.cursor.execute(
                    "INSERT INTO data (section, key, value) VALUES (?, ?, ?)",
                    (section, key, value),
                )
            else:
                self.cursor.execute(
                    "UPDATE data SET value = ? WHERE section = ? AND key = ?",
                    (value, section, key),
                )
            self.connection.commit()

    def _sqlite_remove(self, section: str, key: str):
        with self._lock:
            self.cursor.execute(
                "DELETE FROM data WHERE section = ? AND key = ?",
                (section, key),
            )
            self.connection.commit()


db = Database()