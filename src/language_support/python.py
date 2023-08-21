import ast
from typing import Dict

from language_support.language_extractor import LanguageExtractor

class PythonExtractor(LanguageExtractor):
    
    @staticmethod
    def extract_metadata(code)-> Dict:

        tree = ast.parse(code)

        class_definitions = []
        function_definitions = []
        imports = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_definitions.append(node.name)
            elif isinstance(node, ast.FunctionDef):                
                function_definitions.append(node.name)
            elif isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
                imports.append(",".join([n.name for n in node.names]))

        return {"classes": ",".join(class_definitions), "functions": ",".join(function_definitions), "imports": ",".join(imports)}


