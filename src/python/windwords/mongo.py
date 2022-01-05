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


def get_collection(name):
    """ Returns the MongoDB collection by name. 

    Args:
        name (str): The collection name.
    Returns:
        pymongo.Collection: The MongoDB collection instance.
    """
    client = get_client()
    database = client.get_database(constants.Database.DEFAULT_NAME.value)
    return database.get_collection(name)


def find_documents(collection, query, limit=None, sort=None):
    """ Returns the documents that match the query in the specified collection.

    Args:
        collection (str): The collection name to query.
        query (dict): The document criteria to match.
        limit (int, optional): If specified, limits the results to this number.
        sort (list(tuple(str, int)), optional): If specified, sorts the results
            by mutliple fields. Each field is specified by pairs of the field
            name (str) and the direction (ASCENDING=1, DESCENDING=-1).
    Yields:
        Dict: The matched document, or None.
    """
    cursor = get_collection(collection).find(query)
    if limit:
        cursor.limit(limit)
    if sort:
        cursor.sort(sort)
    for document in cursor:
        yield document


def find_document(collection, query):
    """ Returns the first document that matches the query in the specified
        collection.

    Args:
        collection (str): The collection name to query.
        query (dict): The document criteria to match.
    Returns:
        Dict: The matched document, or None.
    """
    return get_collection(collection).find_one(query)


def find_document_by_id(collection, objectID):
    """ Returns the document that matches the specified objectID.

    Args:
        collection (str): The collection name to insert into.
        objectID (bson.ObjectId): The database object identifier.
    Returns:
        Dict: The matched document, or None.
    """
    return find_one_document(collection, {"_id", objectID})


def find_all(collection):
    """ Returns all documents within the specified collection.

    Args:
        collection (str): The collection name to query.
    Yields:
        Dict: Documents within the collection.
    """
    return find_documents(collection, {})


def find_ids(collection, query, limit=None, sort=None):
    """ Returns the documents that match the query in the specified collection.

    Args:
        collection (str): The collection name to query.
        query (dict): The document criteria to match.
        limit (int, optional): If specified, limits the results to this number.
        sort (list(tuple(str, int)), optional): If specified, sorts the results
            by mutliple fields. Each field is specified by pairs of the field
            name (str) and the direction (ASCENDING=1, DESCENDING=-1).
    Yields:
        (bson.ObjectId): The database object identifier, or None.
    """
    for document in find_documents(collection, query, limit=limit, sort=sort):
        yield document.get("_id", None)


def find_id(collection, query):
    """ Returns the first document objectId that matches the query in the
        specified collection.

    Args:
        collection (str): The collection name to query.
        query (dict): The document criteria to match.
    Returns:
        (bson.ObjectId): The database object identifier, or None.
    """
    document = find_document(collection, query) or {}
    return document.get("_id", None)


def find_id_in_database(objectID):
    """ Returns the document that matches the specified objectID across all
        database collections.
        (If a collection name is known, it is recommended to use 
        `find_document_by_id` for performance.)

    Args:
        objectID (bson.ObjectId): The database object identifier.
    Returns:
        Dict: The matched document, or None.
    """
    collections = [c.value for c in constants.Collection]
    for collection in collections:
        document = find_document_by_id(collection, objectID)
        if document:
            return document
    return None


def count_documents(collection, query):
    """ Returns the total number of documents, within the specified collection,
        that match the provided criteria.

    Args:
        collection (str): The collection name.
        query (dict): The document criteria to match.
    Returns:
        int: The number of documents that match the query criteria.
    """
    return get_collection(collection).count_documents(query)


def count_collection(collection):
    """ Returns the total number of documents within the specified collection.

    Args:
        collection (str): The collection name.
    Returns:
        int: The number of documents within the collection.
    """
    return count_documents(collection, {})
    

def insert_documents(collection, documents):
    """ Inserts the provided documents into the specified database collection.

    Args:
        collection (str): The collection name to insert into.
        documents (dict): The documents to insert.
    Returns:
        List[bson.ObjectId]: The inserted document object ids.
    """
    collection = get_collection(collection)
    result = collection.insert_many(documents)
    return result.inserted_ids
