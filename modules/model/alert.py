from dataclasses import dataclass


@dataclass
class Alert:
    '''A module-level docstring

    Notice the comment above the docstring specifying the encoding.
    Docstrings do appear in the bytecode, so you can access this through
    the ``__doc__`` attribute. This is also what you'll see if you call
    help() on a module or any other Python object.
    '''
    symbol: str
    reference_point: float
    target_point: float

    def __str__(self) -> str:
        return f'{self.symbol.upper()} {self.target_point}'

    def __init__(self, dictionary: dict):
        for k, v in dictionary.items():
            setattr(self, k, v)
