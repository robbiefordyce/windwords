import os
import dns
import certifi
from urllib.parse import quote_plus
from pymongo import MongoClient

from windwords import constants


__CLIENT = None # The Mongo DB client


def get_client():
    """ Connects to MongoDB.

    Returns:
        pymongo.MongoClient: The MongoDB client.
    """
    global __CLIENT
    if not __CLIENT:
        __CLIENT = connect_to_mongo_client()
    return __CLIENT


def connect_to_mongo_client(username=None, password=None, cluster=None):
    """ Connects to MongoDB.

    Args:
        username (str, optional): The username of the connecting user.
            Defaults to the `MONGO_USERNAME` environment variable.
        password (str, optional): The password of the connecting user.
            Defaults to the `MONGO_PASSWORD` environment variable. 
        cluster (str, optional): The mongoDB cluster name to connect to.
            Defaults to the `MONGO_CLUSTER` environment variable.  
    Returns:
        pymongo.MongoClient: The MongoDB client.
    """
    username = username or os.getenv("MONGO_USERNAME")
    password = password or os.getenv("MONGO_PASSWORD")
    cluster = cluster or os.getenv("MONGO_CLUSTER")
    return MongoClient(
        (
            f"mongodb+srv://{quote_plus(username)}:{quote_plus(password)}"
            f"@{cluster}.mongodb.net"
        ),
        tlsCAFile=certifi.where(),
    )


def insert_documents(collection, documents, database=None):
    """ Inserts the provided documents into the specified database collection.

    Args:
        collection (str): The collection name to insert into.
        documents (dict): The documents to insert.
        database (str, optional): The database name.
            Defaults to the `DEFAULT_DATABASE_NAME` constant.  
    Returns:
        List[str]: The inserted document object ids.
    """
    client = get_client()
    database = client.get_database(database or constants.DEFAULT_DATABASE_NAME)
    collection = database.get_collection(collection)
    result = collection.insert_many(documents)
    return result.inserted_ids
