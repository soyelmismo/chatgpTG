import sys

from .typing import MetaModels, Union
from . import Providers


class Models(metaclass=MetaModels):
    
    class model:
        name: str
        base_provider: str
        best_site: str
    
    class gpt_35_turbo:
        name: str = 'gpt-3.5-turbo'
        base_provider: str = 'openai'
        best_site: str = Providers.Ails

    class gpt_4:
        name: str = 'gpt-4'
        base_provider: str = 'openai'
        best_site: str = Providers.Phind
        
class Utils:
    convert: dict = {
        'gpt-3.5-turbo': Models.gpt_35_turbo,
        'gpt-4': Models.gpt_4
    }

class ChatCompletion:
    @staticmethod
    def create(model: Models.model or str, messages: list, provider: Providers.Provider = None, stream: bool = False, **kwargs):
        try:
            if isinstance(model, str):
                model = Utils.convert[model]
            
            engine = model.best_site if not provider else provider
            return (engine._create_completion(model.name, messages, **kwargs)
                    if stream else ''.join(engine._create_completion(model.name, messages, **kwargs)))

        except TypeError as e:
            print(e)
            arg: str = str(e).split("'")[1]
            print(
                f"ValueError: {engine.__name__} does not support '{arg}' argument", file=sys.stderr)
            sys.exit(1)
