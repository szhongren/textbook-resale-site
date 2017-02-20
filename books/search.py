from amazon.api import AmazonAPI

ASSOCIATE_TAG = "<amazon associate tag>"
ACCESS_KEY_ID = "<amazon access key id>"
SECRET_ACCESS_KEY = "<amazon secret access key>"

def ISBNSearch(ISBN):
    amzn = AmazonAPI(ACCESS_KEY_ID, SECRET_ACCESS_KEY, ASSOCIATE_TAG)
    product = amzn.lookup(ItemId=ISBN, IdType='ISBN', SearchIndex='Books')
    return product
