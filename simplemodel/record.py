"""
SimpleModel
record.py


TODO:
- improve type checking and validation in _validateData
"""
import sys

class Record(object):

	def __init__(self, simplemodel):
		self.__dict__['_simplemodel'] 		= simplemodel
		self.__dict__['_properties'] 		= {}
		self.__dict__['_excludeColumns'] 	= []

	def __setattr__(self, name, value):
		print 'setattr: '+name
		if name in self.__dict__: 
			self.__dict__[name] = value
			return 

		# Validate value
		data = {name: value}
		data = self._validateData(data).items()

		if data:
			name, value = data[0]
			self._properties[name] = value
		else:
			raise RecordError('Trying to set value for column "%s" that doesn\'t exist' % name)

	def __getattr__(self, name):
		return self._properties.get(name, None)

	def _validateData(self, data):
		types = {
			'char'		 :'string',
			'varchar'	 :'string',
			'text' 		 :'string',
			'tinytext' 	 :'string',
			'mediumtext' :'string',
			'longtext' 	 :'string',
			'int' 		 :'int',
			'tinyint' 	 :'int',
			'smallint'	 :'int',
			'mediumint'  :'int',
			'bigint'	 :'int',
			'float'		 :'float',
			'decimal'	 :'float',
			'double'	 :'float',
			'real'		 :'real'
		}

		# Remove arbitrary data that 
		# Remove data that needs to be excluded
		for key, value in data.items():
			if key not in self._simplemodel._columns or key in self._excludeColumns:
				del data[key]
				continue

			# Lookup data for this column
			columnKey = self._simplemodel._columns.index(key)
			if not value:
				continue
			elif types.get(self._simplemodel._columnsData[columnKey].get('DATA_TYPE')):
				type = types.get(self._simplemodel._columnsData[columnKey].get('DATA_TYPE'))
			else:
				type = 'string'
			
			if type == 'string' and isinstance(value, basestring):
				continue
			elif type == 'int' and isinstance(value, (int, long)):
				continue
			elif type == 'float' and isinstance(value, (float)):
				continue
			elif type == 'real' and isinstance(value, (int, long, float)):
				continue
			else:
				raise RecordError('Data type of field "{column}" does not match column data type in "{tableName}" table.'\
					.format(tableName=self._simplemodel._tableName, column=key))

		return data

	def setColumnProperties(self, data):
		data = self._validateData(data)

		for key, value in data.items():
			self._properties[key] = value

	def getColumnProperties(self):
		return self._properties

	def deleteColumnProperties(self):
		self._properties = []	

	def excludeColumns(self, toExclude):
		self._excludeColumns.append(toExclude)

	def load(self, data):
		self.setColumnProperties(data)

	def save(self):
		limit = ''
		where = ''
		insertOrUpdate = ''

		if len(self._simplemodel._pkName) > 1:
			insertOrUpdate = 'REPLACE INTO'
		elif self._properties.get(self._simplemodel._pkName[0]):
			insertOrUpdate = 'UPDATE'
			limit = 'LIMIT 1'
			where = 'WHERE `{column}` = "{value}"'.format(
				column 	=self._simplemodel._pkName[0],
				value  	=self._properties.get(self._simplemodel._pkName[0])
				)
		else: 
			insertOrUpdate = 'INSERT INTO'		
			
		# Exclude primary columns
		if len(self._simplemodel._pkName) == 1:
			self.excludeColumns(self._simplemodel._pkName[0])

		# Build filter string
		columnsToString = ', '.join([ '`%s` = "%s"' % (k,v) for k,v in self._properties.items() if k not in self._excludeColumns])

		query = """
		{insertOrUpdate} `{dbName}`.`{tableName}`
		SET
			{columns}
		{where}
		{limit}
		"""

		query = query.format(
			insertOrUpdate 	=insertOrUpdate,
			dbName 			=self._simplemodel._dbName,
			tableName 		=self._simplemodel._tableName,
			columns 		=columnsToString,
			where 			=where,
			limit 			=limit	
			)

		# Execute query
		self._simplemodel._db.execute(query)

		# Resert _excludeColumns
		self._excludeColumns = []

		# Load created record
		# If table has aa key then reload object by that id
		# We also have to reset filter list
		self._simplemodel._filters = []
		if len(self._simplemodel._pkName) == 1:
			self._simplemodel.filter({self._simplemodel._pkName[0]: self._simplemodel._db.insertId()})
		else:
			for pk in self._simplemodel._pkName:
				self._simplemodel.filter({pk: self._properties.get(pk)})

		self.setColumnProperties(self._simplemodel._read())
			
	def delete(self):
		for pk in self._simplemodel._pkName:
			if not self._properties.get(pk):
				raise RecordError('This table has compound primary key but one or more it\'s values are not set')

		where = ', '.join(['`%s` = "%s"' % (pk, self._properties.get(pk)) for pk in self._simplemodel._pkName])

		query = """
		DELETE FROM `{dbName}`.`{tableName}`
		WHERE
			{where}
		"""

		query = query.format(
			dbName 		= self._simplemodel._dbName,
			tableName 	= self._simplemodel._tableName,
			where 		= where 
			)

		self._simplemodel._db.execute(query)


class RecordError(Exception):
	pass