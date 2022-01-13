from abc import ABC, abstractmethod

from windwords import constants, mongo


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
        return mongo.find_id(
            self.collection(),
            self.prune_data(self.primary_data())
        )

    def find(self):
        """ Returns a document in the database that matches the internal object
            handled by this handler.
        """
        return mongo.find_document(
            self.collection(),
            self.prune_data(self.primary_data())
        )

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
        document = self.prune_data(self.primary_data())
        document.update(self.prune_data(self.secondary_data()))
        # Insert into the database
        return mongo.insert_documents(self.collection(), [document])[0]

    def link(self, other):
        """ Links this handler's document to the other handler's document in
            the database.

        Args:
            other (windwords.handlers.DocumentHandler): A document handler
        Returns:
            dict: This document with the link applied.
        Raises:
            AssertionError: If either of the handlers do not have corresponding
                documents in the database.
            ValueError: If the given handler is not linkable to this handler.
        """
        # Ensure both handlers exist in the database
        for handler in (self, other):
            assert handler.exists_in_database(), (
                f"Handler {handler} must exist in database. Please insert()"
            )
        # Ensure link schema is defined for the `other` handler
        document = self.find()
        schema = self.get_link_schema().get(type(other).__name__)
        if not schema:
            raise ValueError(
                f"{type(self)} handlers do not link to {type(other)} handlers"
            )
        # Change modification based on link type
        field = schema.get("field")
        link_type = schema.get("type")
        assert bool(field) and link_type is not None, (
            f"Failed to find a field or type for schema: {schema}"
        )
        operator = (
            "$addToSet"
            if schema.get("type") == constants.LinkType.TO_MANY.value else
            "$set"
        )
        # Perform the link in the database
        return mongo.update_document_by_id(
            self.collection(),
            str(self.database_object_id()),
            {f"link.{field}": other.database_object_id()},
            operator=operator,
        )

    def is_linked(self, other):
        """ Returns true if the specified handler is linked to this one in the
            database.

        Args:
            other (windwords.handlers.DocumentHandler): A document handler
        Returns:
            bool: True if these documents are linked.
        """
        # Ensure a schema exists
        schema = self.get_link_schema().get(type(other).__name__) or {}
        field = schema.get("field")
        if not field:
            return False
        # Ensure a document exists
        document = self.find()
        if not document:
            return False
        # Ensure the other document exists
        object_id = other.database_object_id()
        links = self.get_linked_ids(field)
        return object_id and (object_id == links or object_id in links)

    def get_linked_ids(self, field):
        """ Returns the linked object id(s) for the specified field.

        Args:
            field (str): A link field name.
        Returns:
            List[bson.ObjectId]: A list of linked object ids, under the
                specified field.
        """
        document = self.find()
        ids = document.get("link", {}).get(field, [])
        return ids if isinstance(ids, list) else [ids]

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
    def from_object_id(cls, object_id):
        """ Instantiates this handler from a database object id. 

        Args:
            object_id (bson.ObjectId): A database object id.
        Returns:
            DocumentHandler: The instantiated handler.
        """
        pass

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

    @classmethod
    def get_link_schema(cls):
        """ Returns a link schema that describes how this handler's document
            should link to the documents of other handlers.
            Link schema is a dictionary: {
                `handlerClassName`: {
                    "field": `str`,
                    "type": `windwords.constants.LinkType`
                }
            } 

        Returns:
            dict: The link schema for this handler.
        """
        return {}

    @classmethod
    def get_document_from_object_id(cls, object_id):
        """ Returns the document that matches the specified objectID in this
            handler's collection.

        Args:
            object_id (bson.ObjectId): The database object identifier.
        Returns:
            Dict: The matched document, or None.
        """
        return mongo.find_document_by_id(cls.collection(), object_id)

    @staticmethod
    def prune_data(data, prune=None, recursive=True):
        """ Returns a copy of the input dictionary with empty values removed.

        Args:
            data (dict): An input dictionary
            prune (Optional[List[obj]]): A list of values to remove.
                Defaults to None types, empty dicts/lists and the empty string.
            recursive (bool): If true will recursively remove empty values from
                sub-dictionaries. Defaults to True. 
        Returns:
            dict: A copy of the dictionary with the empty values pruned.
        """
        data = dict(data) # ensure we create a clean copy
        if recursive:
            for key, value in data.items():
                if isinstance(value, dict):
                    data.update({
                        key: DocumentHandler.prune_data(
                            value, prune=prune, recursive=recursive
                        )
                    })
        prune = prune or (None, "", [], {})
        return {k:v for (k,v) in data.items() if v not in prune}
