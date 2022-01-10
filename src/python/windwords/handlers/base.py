from abc import ABC, abstractmethod

from windwords import mongo


class DocumentHandler(ABC):
    def __init__(self, obj):
        assert self.accepts(obj), f"Class {self.__class__} cannot accept: {obj}"
        self._python_object = obj

    @property
    def python_object(self):
        """ Returns the internal object wrapped by this handler.

        Returns:
            (object): The internal python object.
        """
        return self._python_object

    def database_object_id(self):
        """ Returns the objectID in the database that matches the internal
            object handled by this handler.

        Returns:
            bson.ObjectId: The object Id of the database document, or None.
        """
        return mongo.find_id(self.collection(), self.primary_data())

    def find(self):
        """ Returns a document in the database that matches the internal object
            handled by this handler.
        """
        return mongo.find_document(self.collection(), self.primary_data())

    def exists_in_database(self):
        """ Returns whether the associated document exists in the database.

        Returns:
            bool: True if the document exists in the database.
        """
        return bool(self.find())

    def insert(self):
        """ Attempts to insert this document into the database.

        Returns:
            bson.ObjectId: The inserted document objectId.
        Raises:
            AssertionError: If the document already exists in the database.
        """
        # Ensure we are not about to add an entry that already exists!
        assert not self.exists_in_database(), "Document already exists in the database!"
        # Construct the document
        document = self.primary_data()
        document.update(self.secondary_data())
        # Insert into the database
        return mongo.insert_documents(self.collection(), [document])[0]

    @abstractmethod
    def primary_data(self):
        """ Resolves the primary fields and values.
            Primary fields are used for database lookups and therefore should
            not consist of complex objects.

        Returns:
            dict: The primary fields and associated values.
        """
        pass

    def secondary_data(self):
        """ Resolves the secondary fields and values.
            Secondary fields are not necessary to uniquely identify a document.
            Secondary fields may have a greater computation complexity and are
            only intended to be computed prior to insertion.

        Returns:
            dict: The secondary fields and associated values.
        """
        return {}

    @classmethod
    @abstractmethod
    def accepts(cls, obj):
        """ Returns true if this handler can accept the specified object.

        Args:
            (obj, object): Any provided python object.
        Returns:
            bool: True if the handler can handle the provided object.
        """
        pass

    @classmethod
    @abstractmethod
    def collection(cls):
        """ Returns the database collection name associated with this handler.
            This property must be overridden by subclasses.

        Returns:
            (str): The collection name.
        """
        pass
