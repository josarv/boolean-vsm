# boolean model class (takes in ast (per query) and inverted index)
from typing import Callable
from re import compile, split

def preserve_boolean_operators(preprocessing_pipeline: Callable[[str], list[str]]) -> Callable[[str], str]:
    operator_regex = compile(r"&&|\|\||!!|\(\(|\)\)")
    def wrapper(query_string: str) -> str:
        try:
            substrings = split(operator_regex, query_string)
            operators = operator_regex.findall(query_string)
            processed_substrings = []
            for i, substring in enumerate(substrings):
                if substring.strip():
                    preprocessed_tokens = preprocessing_pipeline(substring)
                    preprocessed_strings = " ".join(preprocessed_tokens)
                    processed_substrings.append(preprocessed_strings)
                if i < len(operators):
                    processed_substrings.append(operators[i])

            return " ".join(processed_substrings)
        except Exception as e:
            print(f"An error occurred during query preprocessing: {e}")
            return query_string
    return wrapper
