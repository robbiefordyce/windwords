import os
import dns
import certifi
from pymongo import MongoClient
from urllib.parse import quote_plus


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
