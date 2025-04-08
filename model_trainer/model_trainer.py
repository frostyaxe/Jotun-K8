from pandas import read_csv
import joblib
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import os
import filelock

class ModelTrainer:

    def __init__(self, model, dataset_path):
        self.model = model
        self.dataset_path = dataset_path
        self.df = None
        self.x = None
        self.y = None
        self.columns = []  # Store column names for X and Y
        self.preprocessor = None

    def load_dataset(self, x_cols=None, y_cols=None):
        """Load dataset and set x (features) and y (target)"""
        self.df = read_csv(self.dataset_path)
        
        if x_cols is None or y_cols is None:
            raise ValueError("x_cols and y_cols must be specified.")
        
        self.x = self.df[x_cols].values
        self.y = self.df[y_cols].values
        self.columns = [x_cols, y_cols]  # Store column names for future use

    def display_dataset(self):
        """Display x and y"""
        print("Features (X):")
        print(self.x)
        print("Target (y):")
        print(self.y)

    def train_and_save(self, model_name, models_dir):
        pipeline = Pipeline(steps=[('model', self.model)])
        pipeline.fit(self.x, self.y)
        export_file = os.path.join(models_dir, f'{model_name}.pkl')
        export_file_lock = os.path.join(models_dir, f'{model_name}.pkl.lock')
        export_file_tmp = os.path.join(models_dir, f'{model_name}_tmp.pkl')
        with open(export_file_tmp, 'wb') as file:
            joblib.dump(pipeline, file)
        with filelock.FileLock(export_file_lock):
            os.replace(export_file_tmp,export_file)
        print(f"Model trained and saved as '{export_file}'.")
