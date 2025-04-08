from loaders import *

def __get_model_files(directory : str):
    """
    This function retrieves all files with the '.pkl' extension from the specified directory.

    Parameters:
    - directory (str): The path to the directory where the model files are stored.

    Returns:
    - generator: A generator object that yields the paths to the model files with '.pkl' extension.

    Note:
    - The function assumes that the directory path is a valid string path and that the directory exists.
    """
    extension = "pkl"
    path = Path(directory)
    return path.glob(f'*.{extension}')

def __get_model_obj(filename : str):
    """
    This function loads a machine learning model from a file, ensuring thread-safety by using a file lock.

    Parameters:
    - filename (str): The path to the file containing the serialized machine learning model.

    Returns:
    - object: The loaded machine learning model object.

    Note:
    - The model file should be a valid `joblib`-serialized file.
    - The lock file (`.lock`) is created with the same name as the model file, but with an additional `.lock` extension.
    """
    lock_file = f"{filename}.lock"
    with filelock.FileLock(lock_file):
        with open(filename, "rb") as model:
            return joblib.load(model)
    
def get_models(directory : str):
    """
    This function retrieves and loads all machine learning models from a specified directory.

    Parameters:
    - directory (str): The path to the directory containing the model files.

    Returns:
    - dict: A dictionary where the keys are the model names (without extensions) and the values are 
      the corresponding loaded machine learning model objects.

    Note:
    - This function assumes the files in the directory are valid model files serialized with `joblib`.
    """
    model_files = __get_model_files(directory)
    return { Path(model.name).stem: __get_model_obj(model) for model in model_files}