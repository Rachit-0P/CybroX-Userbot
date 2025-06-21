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

import os
from environs import Env
from os.path import exists

env = Env()
env.read_env()  # read .env file, if it exists

API_ID = env.int("API_ID", 0)
API_HASH = env.str("API_HASH", "")

STRINGSESSION = env.str("STRINGSESSION", None)

db_url = env.str("DATABASE_URL", None)
db_name = env.str("DATABASE_NAME", "cybrox_userbot")
db_type = env.str("DATABASE_TYPE", "sqlite3")

rmbg_key = env.str("RMBG_KEY", None)
apiflash_key = env.str("APIFLASH_KEY", None)
vt_key = env.str("VT_KEY", None)
gemini_key = env.str("GEMINI_KEY", None)
cohere_key = env.str("COHERE_KEY", None)
pm_limit = env.int("PM_LIMIT", 3)

test_server = env.bool("TEST_SERVER", False)
modules_repo = env.str("MODULES_REPO", "https://raw.githubusercontent.com/YourUsername/cybrox_modules/main/")

api_id = API_ID
api_hash = API_HASH