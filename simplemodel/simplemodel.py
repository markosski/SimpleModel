# -*- coding: utf-8 -*-

""" 
SimpleModel is the base class that loads table structure and creates record objects.
"""

import sys
from record import Record
from copy import deepcopy

class SimpleModel:

	def __init__(self, db, tableName):
		self._db 			= db
		self._dbName	 	= None
		self._object		= None
		self._tableName 	= tableName
		self._pkName	 	= []
		self._columns 		= []
		self._columnsData 	= []
		self._defaultData	= []
		self._filters		= []
		self._orderBy		= []
		self._groupBy		= []
		self._limit			= []

		# We need database name in order to retrieve all the 
		# columns in a table
		if not self._dbName:
			self._dbName = self._db.getDbName()

		self._getColumns()

	def _getColumns(self):
		""" We get all columns from the table and primary key.
		If simplemodel object is instantiated directly 
		"""


		query = """
		SELECT 
			`COLUMN_NAME`
			,`DATA_TYPE`
			,`CHARACTER_MAXIMUM_LENGTH`
			,`NUMERIC_PRECISION`
			,`COLUMN_KEY`
		FROM 
			`information_schema`.`columns` 
		WHERE 
			`TABLE_SCHEMA` = "{dbName}" 
			AND `TABLE_NAME` = "{tableName}"
		"""

		query = query.format(dbName=self._dbName, tableName=self._tableName)

		columns = self._db.fetchAll(query)

		# not columns error
		if not columns:
			raise SimpleModelError('No columns found for table %s. Does this table exist?' % (self._tableName,))

		for column in columns:
			self._columns.append(column.get('COLUMN_NAME'))
			self._columnsData.append({
				'DATA_TYPE': column['DATA_TYPE'],
				'CHARACTER_MAXIMUM_LENGTH': column['CHARACTER_MAXIMUM_LENGTH']
			})
			# Get primary key
			if column.get('COLUMN_KEY') == 'PRI':
				self._pkName.append(column.get('COLUMN_NAME'))

	def _read(self, **opts):

		filterString = self._processFilters()

		query = """
		SELECT
            *
        FROM `{dbName}`.`{tableName}`
    	{WHERE}
    		{filters};
		"""

		query = query.format(
			dbName 		= self._dbName,
			tableName 	= self._tableName,
			WHERE		= 'WHERE' if filterString else '',
			filters 	= filterString
		)

		if opts.get('returnSql'):
			return query
		elif opts.get('getAll'):
			data = self._db.fetchAll(query)
			return data
		else:
			# This has to return one value, if there's more, inform user
			data = self._db.fetchAll(query)
			if len(data) > 0:	
				return data[0]

		# If we got here, return empty
		return []

	def _buildFilterString(self, keyValue, filterType, filterTokens):
		
		filterString = ''

		if not filterType:
			filterString = filterTokens.get('is').format(
					column 	=keyValue[0],
					value 	=keyValue[1]
				)
		elif filterType in filterTokens:
			filterString = filterTokens.get(filterType).format(
					column 	=keyValue[0],
					value 	=keyValue[1]
				)
		else:
			# wrong filter type given throw error
			pass

		return filterString

	def _processFilters(self):
		filterTokens = {
			'starts_with' 		: '`{column}` LIKE "{value}%"',
			'not_starts_with' 	: '`{column}` NOT LIKE "{value}%"',
			'ends_with'			: '`{column}` LIKE "%{value}"',
			'not_ends_with'		: '`{column}` NOT LIKE "%{value}"',
			'includes'			: '`{column}` LIKE "%{value}%"',
			'not_includes'		: '`{column}` NOT LIKE "%{value}%"',
			'is' 				: '`{column}` = "{value}" ',
			'not_is' 			: '`{column}` != "{value}" ',
			'is_gt'				: '`{column}` > "{value}"',
			'is_gte'			: '`{column}` >= "{value}"',
			'is_lt'				: '`{column}` < "{value}"',
			'is_lte'			: '`{column}` <= "{value}"',
			'limit'				: ' LIMIT {start},{limit}',
			'order'				: ' ORDER BY {columns}',
			'group'				: ' GROUP BY {columns}'
		}
		filterStrings = []
		output = None

		# Process _filters list
		# This will convert _filters into list of sql parts
		outputFilters = ''

		for filter in self._filters:
			filterSize = len(filter)
			# If dict has only one element
			if filterSize == 1:
				filterPieces = filter[0].keys()[0].split('__')
				filterType = filterPieces[1] if len(filterPieces) == 2 else None

				filterStrings.append(self._buildFilterString((filterPieces[0], filter[0].values()[0]), filterType, filterTokens))

			# If dict has more than 1 element
			elif filterSize > 1:
				filterPartStrings = []

				for filterPart in filter:
					key, value = filterPart.items()[0]
					filterPieces = key.split('__')
					filterType = filterPieces[1] if len(filterPieces) == 2 else None

					filterPartStrings.append(self._buildFilterString((filterPieces[0], value), filterType, filterTokens))

				filterStrings.append('(' + 'OR '.join(filterPartStrings) + ')')

		outputFilters = 'AND '.join(filterStrings)

		# Process _orderBy
		outputOrderBy = ''
		orderByParts = []
		if self._orderBy:
			for orderPart in self._orderBy:
				key, value = orderPart.items()[0]
				orderByParts.append('`%s` %s' % (key, value.upper()))
			outputOrderBy = filterTokens.get('order').format(columns=', '.join(orderByParts))


		# Process _groupBy
		outputGroupBy = ''
		groupByParts = []
		if self._groupBy:
			for groupBy in self._groupBy:
				groupByParts.append('`%s`' % (groupBy,))
			outputGroupBy = filterTokens.get('group').format(columns=', '.join(groupByParts))

		# Process _limit
		outputLimit = ''
		if self._limit:
			outputLimit = filterTokens.get('limit').format(
				start=self._limit.get('start'), 
				limit=self._limit.get('limit')
				)

		# Build SQL query from filter parts
		output = outputFilters + outputGroupBy + outputOrderBy + outputLimit

		return output

	def filter(self, *filter):
		"""
		Parameters:
			filter - list of arrays 
		"""
		self._filters.append(filter)

		return self

	def orderBy(self, *orderBy):
		for order in orderBy:
			self._orderBy.append(order)

		return self

	def groupBy(self, *groupBy):
		for group in groupBy:
			self._groupBy.append(group)
		
		return self

	def limit(self, limit, start=0):
		self._limit = {'limit': limit, 'start': start}
		return self
	
	def create(self):
		return Record(simplemodel=self)

	def get(self, **opts):
		data = self._read(**opts)

		if not data:
			data = {}

		record = Record(simplemodel=self)
		record.load(data)
		return record

	def getAll(self, **opts):
		data = self._read(**dict({'getAll': True}.items() + opts.items()))	

		# return self._recordsIterator(data)
		return RecordsIterator(self, data)


class RecordsIterator:
    
    def __init__(self, simplemodel, data):
    	self._simplemodel = simplemodel
        self._data = data
        self._index = 0
        self._total = len(data)
    
    def __iter__(self):
        return self

    def __len__(self):
    	return self._total
    
    def next(self):
		if self._index == self._total:
			raise StopIteration
		record = Record(self._simplemodel)
		record.setColumnProperties(self._data[self._index])
		
		self._index += 1
		return record


class Make:

	def __init__(self, db, table_name):
		self._simplemodel = SimpleModel(db, table_name)

	def getInstance(self):
		return deepcopy(self._simplemodel)


class SimpleModelError(Exception):
	pass
