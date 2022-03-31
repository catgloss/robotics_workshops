"""Database."""

import logging
from typing import Union
from bson.objectid import ObjectId
import pymongo
import werkzeug
import gridfs
from pymongo.collection import ReturnDocument
from pymongo.errors import InvalidId

from utils.log import setup_logging
from constants import LOG_FILE_PATH, DB_TIMEOUT, LANGUAGE_CODE_MAP


# Logging.
LOGGER = logging.getLogger(__name__)
setup_logging(log_path=LOG_FILE_PATH, print_level="INFO", logger=LOGGER)


class Database:
    """Database class for adding and getting results from mongo DB.

    Attributes
    ----------
    client: pymongo.MongoClient
        Client object for interacting with DB server.
    database: pymongo.database.Database
        Pymongo's abstracted database object.
    grid: gridfs.GridFS
        GridFS store.

    """

    def __init__(
        self,
        database_string: str = "mongodb://localhost:27017",
        db_name: str = "asr_service_db",
    ) -> None:
        """Instantiate.

        Parameters
        ----------
        database_string: str
            URL string to connect to DB server.
        db_name:
            Name of document database to register on server.

        """
        self.client = pymongo.MongoClient(
            database_string, serverSelectionTimeoutMS=DB_TIMEOUT
        )
        self.database = self.client[db_name]
        self.grid = gridfs.GridFS(self.database)

    def add_file(
        self, file: werkzeug.datastructures.FileStorage, lang_code: str
    ) -> str:
        """Add file to the DB.

        Parameters
        ----------
        file: werkzeug.datastructures.FileStorage
            File to store in DB.
        lang_code: str
            Language of audio file.

        Returns
        -------
        str
            Document ID of stored file in database.

        """
        file_location = self.grid.put(file)
        collection = self.database[LANGUAGE_CODE_MAP[lang_code]]
        new_document_id = collection.insert_one({"file_location": file_location})
        return str(new_document_id.inserted_id)

    def add_results(self, results: dict, lang_code: str, object_id: str) -> None:
        """Add results to the the DB.

        Parameters
        ----------
        results: dict
            Results from trascription.
        lang_code: str
            Language of audio file.
        object_id: str
            Unique ID of input file sent for transcription, for which we are
            adding results.

        """
        collection = self.database[LANGUAGE_CODE_MAP[lang_code]]
        query = {"_id": ObjectId(object_id)}
        updated_document = collection.find_one_and_update(
            filter=query,
            update={"$set": results},
            return_document=ReturnDocument.AFTER,
        )
        LOGGER.info(updated_document)

    def get_result(self, object_id: str) -> Union[None, dict]:
        """Get result from the database, using the id generated previously.

        Parameters
        ----------
        object_id: str
            Unique ID of input file sent for transcription, for which we are
            fetching results.

        Returns
        -------
        Union[None, dict]
            Results dict for transcribed file, None if object_id is invalid.
        """
        collections = self.database.collection_names()
        result = None
        for collection_name in collections:
            try:
                result = self.database.get_collection(collection_name).find_one(
                    filter={"_id": ObjectId(object_id)}
                )
            except InvalidId:
                return None
            if result is not None:
                break
        return result


ASR_DB = Database()
