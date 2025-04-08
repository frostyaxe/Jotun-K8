from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import LabelEncoder
import numpy as np

class LabelEncoderTransformer(BaseEstimator, TransformerMixin):
    def __init__(self):
        self.encoders = []
    
    def fit(self, X, y=None):
        self.encoders = [LabelEncoder().fit(X[:, i]) for i in range(X.shape[1])]
        return self
    
    def transform(self, X):
        return np.column_stack([self.encoders[i].transform(X[:, i]) for i in range(X.shape[1])])
