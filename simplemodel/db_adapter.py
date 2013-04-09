# -*- coding: utf-8 -*-

""" simplemodel.MySQLAdapter

This is the minimal database interface 
"""
class DbAdapter(object):

	_db = None

	def __init__(self, db):
		self._db = db

	def getDbName(self):
		return self._db._connInfo.get('dbname')

	def getDbInstance(self):
		return self._db

	def fetchAll(self, query):
		return self._db.fetchAll(query)

	def fetchFirst(self, query):
		return self._db.fetchFirst(query)

	def execute(self, query):
		self._db.execute(query)

	def insertId(self):
		return self._db.info.get('lastInsertId')
