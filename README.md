============
Simple Model 
============

SimpleModel is an Active Record implementation for MySQL. SimpleModel is still in early alpha stage.

Simplemodel is an active record library for MySQL.
It allows for retrieving records from table as well as creating, updating and 
deleting.
Simple model will work with the following table setups:

1. If table has one column primary key, it requires that columns to be 
    autoincrement. 

2. If table has compound primary key consisting of 2 or more columns, it will 
    require those columns to be set in the object before inserting or updating
    record. When inserting or updating simplemodel will use "REPLACE INTO" 
    statement.

USAGE
=====

This should be called only once in the script for the table.
This will create an instance of the table object.
    
    sm = simplemodel.Make(db, 'users')

This will return a record object coresponding to user ID = 1

    user = sm.getInstance().filter({'userID':1}).get()

To get all the users from the table you would use getAll() method
getAll() return iterable object that when accessed returns record object.

    users = sm.getInstance().getAll()
    for user in users:
        print user.userID

RETRIEVING RECORDS
------------------

1. How to deal with OR, AND statement in MySQL query.
This will return an object coresponding to users of name Marcin or Andrew.

    obj = users.getInstance()
    objects = obj.filter({'userName': 'Marcin', 'userName': 'Andrew'}).getAll()

In this example records we return records that corespond to user name 
Marcin and age 31.

    obj = users.getInstance()
    objects = obj.filter({'userName': 'Marcin').filter({'userAge': 31}).getAll()

2. Ordering records

    obj = users.getInstance()
    objects = obj.orderBy({'userAge': 'desc'}).getAll()

3. Limiting records
Limiting records is very important. You would not want to use getAll() on 
huge result set. Since simplemodel saves all results as dictionary 
internally and passes it to iterable object it's advisible to use limit.

    obj = users.getInstance()
    objects = obj.limit(10).getAll() # return first 10 records
    # or 
    objects = obj.limit(10, 10).getAll() # return 10 next records starting at 10
    
Now let's show an example of filter usage with orderBy and limit
    
    obj = users.getInstance()
    object = obj.filter({'userName': 'Marcin', 'userName': 'Andrew'})\
        .filter({'userActive': 1})
        .filter({'userDeleted': 0})
        .orderBy({'userAge': 'desc'})
        .limit(10)
        .getAll()
    
    for record in object:
        print record.userName

CREATING RECORD
---------------

    object = obj.getInstance().create() # this is our empty record object

Now we can set it's properties/columns one by one or pass a dictionary to
load() method. If you're creating new record from user submitted data you 
may pass POST data (before prior validation). Record object will additionally
validate type of each element. For example your table has "userAge" column
of int data type and you're assigning it a string, record object will raise
error.

    object.load(data)
    object.save() # record will be saved upon calling save() method

Now that record is saved in order to retrieve it's autoincrement primary
key value you can access it in object.userID.

UPDATING RECORD
---------------
    
This works very similarli to creating a record. The only difference is that
if record already exists it will be updated. 

    object = obj.getInstance().filter({'userID': 1}).get()
    object.load(data)
    object.save()

DELETING RECORD
---------------

You have to load record first before you can delete it.

    object = obj.getInstance().filter({'userID': 1}).get()
    if object.userID: object.delete()
