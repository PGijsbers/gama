from abc import ABC
from typing import List, Dict, Tuple, Any, Union

import pandas as pd

from gama.genetic_programming.operator_set import OperatorSet
from gama.genetic_programming.components import Individual


class BaseSearch(ABC):

    def __init__(self):
        # hyperparameters can be used to safe/process search hyperparameters
        self.hyperparameters: Dict[str, Tuple[Any, Any]] = dict()
        self.output: List[Individual] = []

    def dynamic_defaults(
            self,
            x: pd.DataFrame,
            y: Union[pd.DataFrame, pd.Series],
            time: int) -> None:
        # updates self.hyperparameters defaults
        raise NotImplementedError("Must be implemented by child class.")

    def search(self, operations: OperatorSet, start_candidates: List[Individual]):
        raise NotImplementedError("Must be implemented by child class.")


def _check_base_search_hyperparameters(
        toolbox,
        output: List[Individual],
        start_candidates: List[Individual]
) -> None:
    """ Checks that search hyperparameters are valid.

    :param toolbox:
    :param output:
    :param start_candidates:
    :return:
    """
    if not isinstance(start_candidates, list):
        raise TypeError(f"'start_population' must be a list but was {type(start_candidates)}")
    if not all(isinstance(x, Individual) for x in start_candidates):
        raise TypeError(f"Each element in 'start_population' must be Individual.")
