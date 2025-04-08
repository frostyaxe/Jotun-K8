from pydantic import BaseModel
from .mem_manager import MemManagerImpl
from .replicas_manager import ReplicasManagerImpl
from .jotun_model import ModelInterface

class Customizer:
      
    def __init__(self):
        self.model_registry = {
                "mem_manager": MemManagerImpl,
                "replicas_manager": ReplicasManagerImpl,
            }

    def get_request_model(self, model_name: str):
        return self.model_registry[model_name]().get_request_model()
    
    def get_model_instance(self, model_name: str, request) -> BaseModel:
        request_model_class = self.get_request_model(model_name)
        return request_model_class(**request)
    
    def get_processed_result(self,model_name: str, result):
            return self.model_registry[model_name]().process_request(result)
    
    def get_prediction_features(self, model_name : str, request_dict):
        return self.model_registry[model_name]().get_prediction_features(request_dict)
    
    def validate_features(self, model_name: str, model, request_dict):
         return self.model_registry[model_name]().validate_features(model, request_dict)

    def train_and_save(self, model_name, model, dataset, save_path):
            trainer = self.model_registry[model_name]().get_trainer_class()(model, dataset)
            trainer.train_and_save(model_name,save_path)

    def validate(self, model_name):
        if model_name not in self.model_registry:
            return False
        clasz = self.model_registry[model_name]
        if not issubclass(clasz, ModelInterface):
            print(f"{clasz.__name__} does not inherit from {ModelInterface.__name__}.")
            return False

        # Check if the class has implemented all abstract methods
        if not all(hasattr(clasz, method) for method in ModelInterface.__abstractmethods__):
            print(f"{clasz.__name__} does not implement all abstract methods.")
            return False

        return True