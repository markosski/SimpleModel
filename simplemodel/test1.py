
import sys
sys.path.append("/home/pyprojects/pydbwrapper") 
# pydbwrapper = __import__("pydbwrapper")

import simplemodel, record, db_adapter
# from simplemodel.pydbwrapper import pydbwrapper
from pydbwrapper import pydbwrapper


db = pydbwrapper.PyDbWrapper({
	'user':'root',
	'password':'martek123',
	'host':'localhost',
	'dbname':'test'
	})
smdb = db_adapter.DbAdapter(db)

users = simplemodel.Make(smdb, 'users')
uaddress = simplemodel.Make(smdb, 'users_address')
# accounts = simplemodel.SimpleModelFactory(db_adapter.DbAdapter(db), 'accounts')

def get():
	model = users.getInstance()\
		.filter({'userID': 1})\
		.get()

	ur = uaddress.getInstance().filter({'userID': 1}).getAll()

	if model.userID:
		print 'Record %s loaded' % (model.userID)

	model.userName = 'new name'
	model._excludeColumns = []
	print model._properties


def getAll():
	model = users.getInstance()\
		.filter({'userEmail__includes': 'marcin'})\
		.getAll()

	if len(model) > 0:
		for record in model:
			print 'Record %s' % (record.userID,)


def insert():
	model = users.getInstance()\
		.create()

	model.userName = 'Marcelus'
	model.userEmail = 'marcin@basementsystems.com'
	model.save()

	if model.userID:
		print 'New userID is %s' % (model.userID,)


def delete():
	model = users.getInstance()\
		.filter({'userID': 21})\
		.get()
	
	if model.userID:
		model.delete()
		print 'Record has been deleted' 


def users_address_new():
	address = uaddress.getInstance().create()
	address.userID = 2
	address.addressName = 'Billing'
	address.save()


get()
# users_address_new()
# print dir(users)
# print len(model)
# for obj in model:
# 	print obj.userEmail

