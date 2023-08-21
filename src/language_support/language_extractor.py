from abc import abstractclassmethod, ABC

class LanguageExtractor(ABC):
    
    @abstractclassmethod
    def extract_metadata(self, code):
        pass