from updater import *

def get_file_hash(file_path: str, hash_algo: str='sha256' ):
    """
    Computes the hash of a file using the specified hashing algorithm.

    Args:
        file_path (str): The path to the file for which the hash needs to be computed.
        hash_algo (str): The hashing algorithm to use. Defaults to 'sha256'.
                         Supported algorithms include 'sha256', 'md5', etc.

    Returns:
        str: The hexadecimal digest of the file's hash.
        
    """
    hash_function = hashlib.new(hash_algo)
    with open(file_path, 'rb') as file:
        while chunk := file.read(8192):
            hash_function.update(chunk)
    return hash_function.hexdigest()

class JotunUpdater:
    """
    This class handles updating machine learning models based on changes in the dataset files.

    Attributes:
    - models (dict): A dictionary containing the machine learning models. The keys are model names, 
                     and the values are the model objects that will be updated based on dataset changes.

    Methods:
    - __init__(self, models): Initializes the JotunUpdater with a dictionary of models.
    - fetch_all_dataset(self): Retrieves all dataset files from the "datasets" directory.
    - update(self): Compares the current dataset hashes with the stored hashes, and updates the models 
                    if any dataset has changed. Returns a boolean indicating whether any models were updated.
    """
    def __init__(self, models : dict):
        """
        Initializes the JotunUpdater class with the provided dictionary of models.

        Parameters:
        - models (dict): A dictionary of machine learning models, where keys are model names and 
                         values are model objects.
        """
        self.models = models

    def fetch_all_dataset(self):
        """
        Fetches all dataset files from the 'datasets' directory.

        Returns:
        - list: A list of dataset file names.
        - str: The full path to the 'datasets' directory.
        
        The method constructs the path to the 'datasets' directory and retrieves the list of files
        in that directory.
        """
        dataset_dir = os.path.join(os.getcwd(), "datasets")
        return os.listdir(dataset_dir), dataset_dir
        
    def update(self):
        """
        Checks for updates in the dataset files, compares their hashes with the stored hashes in the 
        database, and updates the corresponding machine learning models if any dataset has changed.

        Returns:
        - bool: True if any models were updated, False otherwise.
        """
        isUpdated = False
        isHashNotPresent = False
        models_update_status = []
        print("Checking for updates...")
        print("Loading model dataset hashes from database...")      # Load details from the database

        db = JotunDBUtils("hash_tracker.db")
        hashes, err = db.fetch_hashes()

        if err != None:
            raise Error(err)

        print("Fetching all dataset files...")
        dataset_files, dataset_dir = self.fetch_all_dataset()

        print("Calculating hash for all datasets...")
        latest_calc_details = { Path(dataset).stem: { "hash": get_file_hash(os.path.join(dataset_dir, dataset)), "filepath": os.path.join(dataset_dir, dataset) } for dataset in dataset_files }

        for model, details in latest_calc_details.items():
            if model not in hashes:
                current_db_hash = ""
                isHashNotPresent = True
            else:
                current_db_hash = hashes[model]["dataset_hash"]
           
            if details["hash"] != current_db_hash:
                print(f"Proceeding to update the following model :: {model}")
                customize = Customizer()
                isValidationSuccess = customize.validate(model)
                if not isValidationSuccess:
                    return Exception(f"Validation failed for the following model :: {model}")
                customize.train_and_save(model, self.models[f'{model}'], details["filepath"], os.path.join(os.getcwd(), "models"))
                isUpdated = True
                if isHashNotPresent:
                    db.insert_hash(model, details["hash"])
                else:
                    db.update_hash(model, details["hash"], current_db_hash)
                models_update_status.append({"model": model, "current_hash": details["hash"][0:8], "previous_hash": current_db_hash[0:8]})
            else:
                print(f"No update found :: {model}")
        print(tabulate(models_update_status, headers="keys", tablefmt="grid"))        
        return isUpdated
