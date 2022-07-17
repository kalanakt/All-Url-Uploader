import pymongo
from sample_config import Config
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

DATABASE_URL = Config.DATABASE_URL
SESSION_NAME = Config.SESSION_NAME

myclient = pymongo.MongoClient(DATABASE_URL)
mydb = myclient[SESSION_NAME]

async def add_footer(userid, footer): 
    mycol = mydb["quickdb"]
    mydict = {"userid": str(userid), "footer": str(footer) }
    
    try:
        x = mycol.insert_one(mydict)
    except:
        logger.exception('Some error occured!', exc_info=True)
                
async def remove_footer(userid):
    mycol = mydb["quickdb"]
    myquery = { "userid": str(userid) }
    mycol.delete_one(myquery)
    
async def get_footer(userid):
    mycol = mydb["quickdb"]
    myquery = { "userid": str(userid) }
    mydoc = mycol.find(myquery)
    for x in mydoc:
      return x 
