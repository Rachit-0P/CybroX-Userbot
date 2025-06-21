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

import asyncio
import logging
from datetime import datetime, timedelta

from utils.db import db


async def rentry_cleanup_job():
    """A periodic job to clean up old rentry entries"""
    try:
        while True:
            # Run every hour
            await asyncio.sleep(3600)
            
            # Get all rentry URLs from the database
            try:
                collection = db.get_collection("rentry_urls")
                cursor = collection.find({})
                
                # Check each entry for expiration
                for doc in cursor:
                    url_id = doc.get("_id")
                    created_at = doc.get("created_at")
                    
                    # If created more than 7 days ago, delete it
                    if created_at and (datetime.now() - created_at) > timedelta(days=7):
                        collection.delete_one({"_id": url_id})
                        logging.info(f"Deleted expired rentry URL: {url_id}")
            except Exception as e:
                logging.error(f"Error in rentry cleanup job: {e}")
                
    except asyncio.CancelledError:
        pass