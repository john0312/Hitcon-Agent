# -*- coding: utf-8 -*-
# Copyright (c) 2020 HITCON Agent Contributors
# See CONTRIBUTORS file for the list of HITCON Agent Contributors

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import sqlite3
import logging
from config import Config
from concurrent import futures

class Database:
    def __init__(self):
        self._conn = None
        # The database can only be accessed on the thread it is created.
        self.executor = futures.ThreadPoolExecutor(max_workers=1)
        self.executor.submit(lambda: self.Connect()).result()

    # All of the methods below can only run in the executor thread.

    def Connect(self):
        if self._conn == None:
            try:
                self._conn = sqlite3.connect(Config.conf()["scoreboardDBPath"])
                logging.info("Database connected")
            except Error as e:
                logging.error(e)
                raise

    def Execute(self, command, values=()):
        for i in range(Config.conf()["dbRetryTimes"]):
            try:
                cursor = self._conn.cursor()
                return cursor.execute(command, values)
            except sqlite3.Error as e:
                logging.error(e)
                self._conn = None
                self.Connect()
                continue
    
    def ExecuteMany(self, command, values=[]):
        for i in range(Config.conf()["dbRetryTimes"]):
            try:
                cursor = self._conn.cursor()
                return cursor.executemany(command, values)
            except sqlite3.Error as e:
                logging.error(e)
                self._conn = None
                self.Connect()
                continue

    def Commit(self):
        self._conn.commit()
