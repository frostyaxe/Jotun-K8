from utils import *

class JotunDBUtils:
    """
    A utility class for performing database operations using SQLite.

    Author: Abhishek Prajapati
    Contact: prajapatiabhishek1996@gmail.com

    Description:
    This class contains helper methods to interact with a SQLite database.
    It supports operations such as connecting to the database, executing SQL queries,
    and managing database transactions (e.g., commit, rollback). It is designed
    to provide easy-to-use methods for common database tasks and ensure proper
    error handling and resource management.

    Usage:
    The methods in this class should be used to interact with the SQLite database.

    Methods:
        - __init__: Establishes a connection to the SQLite database.
        - create_table: Creates the table in the SQLite Database
        - commit_changes: Commits any changes made to the database.
        - rollback_changes: Rolls back any uncommitted changes.
        - close_connection: Closes the connection to the SQLite database.

    Notes:
        - Ensure that the SQLite database file is accessible and the correct path is provided.
        - Handle exceptions appropriately when using these methods.
        - Database connections and cursors are automatically managed.

    """

    def __init__(self, db_file : str):
        """
        Initializes the database connection using SQLite in the JotunDBUtils class.

        Args:
            db_file (str): The path to the SQLite database file to connect to.

        Attributes:
            connection (sqlite3.Connection): The connection object to the SQLite database if successful.
            error (Exception): Stores the error object if there is a failure in establishing the connection.

        Example:
            db = JotunDBUtils('path_to_db.db')
            If the connection is successful, `db.connection` is populated, and no error occurs.
            If there is an error, the `db.error` attribute contains the error details.
        """
        self.error = None
        try:
            self.connection = sqlite3.connect(db_file)
            self.connection.row_factory = sqlite3.Row
            print("Connection with database established successfully")
        except Error as e:
            self.error = e
    
    def create_table(self) -> Error:
        """
        Creates a new table in the database if it does not already exist.

        This method attempts to create the 'hash_tracker' table with three columns:
        - model_name (TEXT, primary key, not null)
        - dataset_hash (TEXT, not null)
        - previous_dataset_hash (TEXT, not null)

        Returns:
            Error: If an error occurs during the table creation process, an error object 
            (sqlite3.Error) is returned, otherwise None.
        """
        try:
            query = f'''CREATE TABLE IF NOT EXISTS hash_tracker (
                            model_name TEXT PRIMARY KEY NOT NULL,
                            dataset_hash TEXT NOT NULL,
                            previous_dataset_hash TEXT NOT NULL
                        );'''
            with self.connection:
                self.connection.execute(query)
                print("Table created or already exists.")
        except Error as e:
            return e

    def fetch_hashes(self) -> Union[dict, Error]:
        """
        Fetches model names, dataset hashes, and previous dataset hashes from the database.

        This method retrieves all rows from the 'hash_tracker' table and extracts the following columns:
        - model_name
        - dataset_hash
        - previous_dataset_hash

        Returns:
            dict: A dictionary containing model names as keys and another dictionary as the value
                with 'dataset_hash' and 'previous_dataset_hash' as key-value pairs.
            Error: Returns the error object if an exception is raised during the database fetch operation,
                otherwise, returns None.
        """
        try:
            sql_select = '''SELECT  model_name, dataset_hash, previous_dataset_hash FROM hash_tracker;'''
            @contextmanager
            def cusor_context():
                cursor = self.connection.cursor()
                try:
                    yield cursor
                finally:
                    cursor.close()
            with cusor_context() as cursor:
                cursor.execute(sql_select)
                rows = cursor.fetchall()
                result = { row["model_name"]: {k: v for k, v in dict(row).items() if k != "model_name"} for row in rows }
            return result, None
        except Error as e:
            return {}, e
        
    def insert_hash(self, model_name : str, hash : str) -> Union[None, Error]:
        """
        Inserts a new hash entry into the 'hash_tracker' table in the database.

        Parameters:
            model_name (str): The name of the model.
            hash (str): The dataset hash (used for both 'dataset_hash' and 'previous_dataset_hash').

        Returns:
            None: If the insertion is successful.
            Error: If an exception occurs during the insertion operation, the error is returned.
        """
        try:
            sql_insert = '''INSERT INTO hash_tracker (model_name, dataset_hash, previous_dataset_hash) VALUES (?, ?, ?);'''
            with self.connection:
                self.connection.execute(sql_insert, (model_name, hash, hash))
                print(f"Model '{model_name}' details inserted successfully with hash '{hash}'.")
        except Error as e:
            return e

    def update_hash(self, model_name : str, current_hash : str, previous_hash : str) -> Union[None, Error]:
        """
        Updates the dataset hash and previous dataset hash for a specific model in the 'hash_tracker' table.

        Parameters:
            model_name (str): The name of the model whose hash values need to be updated.
            current_hash (str): The new hash value for the 'dataset_hash' column.
            previous_hash (str): The new hash value for the 'previous_dataset_hash' column.

        Returns:
            None: If the update is successful.
            Error: If an exception occurs during the update operation, the error is returned.
        """
        try:
            sql_update = '''UPDATE hash_tracker SET dataset_hash = ? , previous_dataset_hash = ? WHERE model_name = ?;'''
            with self.connection:
                self.connection.execute(sql_update, (current_hash, previous_hash, model_name))
                print(f"Model '{model_name}' updated successfully with new dataset_hash '{current_hash}'.")
        except Error as e:
            return e

    
    