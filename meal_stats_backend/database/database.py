from pymongo import MongoClient


class Singleton(type):
    def __init__(cls, name, bases, dict):
        super(Singleton, cls).__init__(name, bases, dict)
        cls.instance = None

    def __call__(cls,*args,**kw):
        if cls.instance is None:
            cls.instance = super(Singleton, cls).__call__(*args, **kw)
        return cls.instance

class Database:
    __metaclass__ = Singleton

    def __init__(self):
        self.db = None
        self.client = None

    def connection( self, database = 'mealStatsdb' ):
        if self.db != None and self.db[1] == database:
            return self.db
        try:
            self.client = MongoClient()
            self.db = self.client[database]
        except ConnectionFailure as e:
            print 'error', e
        return self.db


    def getStats( self, category ):
         result = self.db.Food.find_one({'category': category })
         return result





#dataBaseObj = Database()
#dataBaseObj.connection('mealStatsdb')
#dataBaseObj.insertFood('Meat')
#dataBaseObj.viewFood('Meat')

#connection('mealStatsdb')
