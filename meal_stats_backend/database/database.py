from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

class Singleton(type):
    def __init__(cls, name, bases, dict):
        super(Singleton, cls).__init__(name, bases, dict)
        cls.instance = None

    def __call__(cls,*args, **kw):
        if cls.instance is None:
            cls.instance = super(Singleton, cls).__call__(*args, **kw)
        return cls.instance

class Database(object):
    __metaclass__ = Singleton

    def __init__(self, database = 'mealStatsdb', host='localhost', port=27017):
        self.db = None
        self.client = None
        self.connection(database, host, port)

    def connection( self, database = 'mealStatsdb', host='localhost', port=27017):
        print database, host, port
        if self.db != None and self.db[1] == database:
            return self.db
        try:
            self.client = MongoClient(host, port)
            self.db = self.client[database]
        except ConnectionFailure as e:
            print 'error', e
        return self.db


    def getStats( self, category ):
         result = self.db.Food.find_one({'category': category })
         return result

    def close_client(self):
        self.client.close()


#dataBaseObj = Database()
#dataBaseObj.connection('mealStatsdb')
#dataBaseObj.insertFood('Meat')
#dataBaseObj.viewFood('Meat')

#connection('mealStatsdb')
