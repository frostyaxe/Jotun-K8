from model_trainer.model_trainer import ModelTrainer
from pydantic import BaseModel
from .jotun_model import ModelInterface

class MemManagerRequest(BaseModel):
    namespace: str
    deployment: str
    requestsCount: int
    time: int

class MemManagerTrainer:

    def __init__(self, model, dataset):
        self.model = model
        self.dataset = dataset

    def train_and_save(self, model_name, save_path):
        trainer = ModelTrainer(self.model, self.dataset)
        trainer.load_dataset(x_cols=["namespace", "deployments","requestsCount", "time"], y_cols=["cpu", "memory"])
        trainer.train_and_save(model_name, save_path)


class MemManagerImpl(ModelInterface):

    def get_request_model(self) :
        return MemManagerRequest

    def process_request(self, result) :
        return {"cpu": result[0][0], "memory": result[0][1]}

    def get_trainer_class(self):
        return MemManagerTrainer
    
    def get_prediction_features(self, request: MemManagerRequest):
        return [[request.namespace, request.deployment, request.requestsCount, request.time]]
    
    def validate_features(self, model, request_dict):
        errors = []
        namespace_classes = model.named_steps['model'].named_steps['preprocessor'].transformers_[1][1].encoders[0].classes_
        app_classes = model.named_steps['model'].named_steps['preprocessor'].transformers_[2][1].encoders[0].classes_
        if request_dict.namespace not in namespace_classes:
            errors.append(f"Current namespace value [ {request_dict.namespace} ] is invalid. Valid namespaces are {namespace_classes}")
        if request_dict.deployment not in app_classes:
            errors.append(f"Current deployment name [ {request_dict.deployment} ] is invalid. Valid deployment values are {app_classes}")
        return errors
    

