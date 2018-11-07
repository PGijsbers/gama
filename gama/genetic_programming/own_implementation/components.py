from collections import defaultdict
import random
from typing import List
import uuid

import sklearn


DATA_TERMINAL = 'data'

class Terminal:
    """ Specifies a specific value for a specific type or input, e.g. a value for a hyperparameter for an algorithm. """

    def __init__(self, value, output: str, identifier: str):
        self.value = value
        self.output = output
        self._identifier = identifier

    def str_format_value(self):
        if isinstance(self.value, str):
            return "'{}'".format(self.value)
        elif callable(self.value):
            return "{}".format(self.value.__name__)
        else:
            return str(self.value)

    def __str__(self):
        return "{}={}".format(self.output, self.str_format_value())

    def __repr__(self):
        return "{}={}".format(self._identifier, self.str_format_value())


class Primitive:
    """ Defines an operator which takes input and produces output, e.g. a preprocessing or classification algorithm. """

    def __init__(self, input_: List[str], output: str, identifier: str):
        self.input = input_
        self.output = output
        self._identifier = identifier

    def __str__(self):
        return self._identifier

    def __repr__(self):
        return self._identifier


class PrimitiveNode:
    """ An instantiation for a Primitive with specific Terminals. """

    def __init__(self, primitive: Primitive, data_node, terminals: List[Terminal]):
        self._primitive = primitive
        self._data_node = data_node
        self._terminals = terminals

    def __str__(self):
        if self._terminals:
            terminal_str = ", ".join([str(terminal) for terminal in self._terminals])
            return "{}({}, {})".format(self._primitive._identifier, str(self._data_node), terminal_str)
        else:
            return "{}({})".format(self._primitive._identifier, str(self._data_node))


class Individual:
    """ A collection of PrimitiveNodes which together specify a machine learning pipeline. """

    def __init__(self, main_node: PrimitiveNode):
        self.fitness = None
        self.main_node = main_node
        self._id = uuid.uuid4()

    def pipeline_str(self):
        return str(self.main_node)

    def __eq__(self, other):
        return isinstance(other, Individual) and other._id == self._id

    def __repr__(self):
        super().__repr__(self)

    def __str__(self):
        return """Individual {}\nPipeline: {}\nFitness: {}""".format(self._id, self.pipeline_str(), self.fitness)

    @property
    def primitives(self) -> List[PrimitiveNode]:
        yield self.main_node
        current_node = self.main_node._data_node
        while current_node != DATA_TERMINAL:
            yield current_node
            current_node = current_node._data_node

    @property
    def terminals(self):
        terminal_index = 0
        for primitive in self.primitives:
            for terminal in primitive._terminals:
                yield (terminal_index, terminal)
                terminal_index += 1

    def replace_terminal(self, position: int, new_terminal: Terminal):
        scan_position = 0
        for primitive in self.primitives:
            if scan_position + len(primitive._terminals) > position:
                terminal_to_be_replaced = primitive._terminals[position - scan_position]
                if terminal_to_be_replaced._identifier == new_terminal._identifier:
                    primitive._terminals[position - scan_position] = new_terminal
                    return
                else:
                    raise ValueError("New terminal does not share output type with the one at position {}."
                                     "Old: {}. New: {}.".format(position,
                                                                terminal_to_be_replaced._identifier,
                                                                new_terminal._identifier))
            else:
                scan_position += len(primitive._terminals)
        if scan_position < position:
            raise ValueError("Position {} is out of range with {} terminals.".format(position, scan_position))


def pset_from_config(configuration):
    """ Create a pset for the given configuration dictionary.

    Given a configuration dictionary specifying operators (e.g. sklearn
    estimators), their hyperparameters and values for each hyperparameter,
    create a gp.PrimitiveSetTyped that contains:
        - For each operator a primitive
        - For each possible hyperparameter-value combination a unique terminal

    Side effect: Imports the classes of each primitive.

    Returns the given Pset.
    """

    pset = defaultdict(list)
    parameter_checks = {}

    shared_hyperparameter_types = {}
    # We have to make sure the str-keys are evaluated first: they describe shared hyperparameters
    # We can not rely on order-preserving dictionaries as this is not in the Python 3.5 specification.
    sorted_keys = reversed(sorted(configuration.keys(), key=lambda x: str(type(x))))
    for key in sorted_keys:
        values = configuration[key]
        if isinstance(key, str):
            # Specification of shared hyperparameters
            for value in values:
                pset[key].append(Terminal(value=value, output=key, identifier=key))
        elif isinstance(key, object):
            # Specification of operator (learner, preprocessor)
            hyperparameter_types = []
            for name, param_values in sorted(values.items()):
                # We construct a new type for each hyperparameter, so we can specify
                # it as terminal type, making sure it matches with expected
                # input of the operators. Moreover it automatically makes sure that
                # crossover only happens between same hyperparameters.
                if isinstance(param_values, list) and not param_values:
                    # An empty list indicates a shared hyperparameter
                    hyperparameter_types.append(name)
                elif name == "param_check":
                    # This allows users to define illegal hyperparameter combinations, but is not a terminal.
                    parameter_checks[key.__name__] = param_values[0]
                else:
                    hyperparameter_types.append(key.__name__+'.'+name)
                    for value in param_values:
                        pset[key.__name__+'.'+name].append(
                            Terminal(value=value, output=name, identifier=key.__name__+'.'+name))

            # After registering the hyperparameter types, we can register the operator itself.
            transformer_tags = ["DATA_PREPROCESSING", "FEATURE_SELECTION", "DATA_TRANSFORMATION"]
            if (issubclass(key, sklearn.base.TransformerMixin) or
                    (hasattr(key, 'metadata') and key.metadata.query()["primitive_family"] in transformer_tags)):
                pset[DATA_TERMINAL].append(Primitive(input_=hyperparameter_types, output=DATA_TERMINAL, identifier=key.__name__))
            elif (issubclass(key, sklearn.base.ClassifierMixin) or
                  (hasattr(key, 'metadata') and key.metadata.query()["primitive_family"] == "CLASSIFICATION")):
                pset["prediction"].append(Primitive(input_=hyperparameter_types, output="prediction", identifier=key.__name__))
            elif (issubclass(key, sklearn.base.RegressorMixin) or
                  (hasattr(key, 'metadata') and key.metadata.query()["primitive_family"] == "REGRESSION")):
                pset["prediction"].append(Primitive(input_=hyperparameter_types, output="prediction", identifier=key.__name__))
            else:
                raise TypeError("Expected {} to be either subclass of "
                                "TransformerMixin, RegressorMixin or ClassifierMixin.".format(key))
        else:
            raise TypeError('Encountered unknown type as key in dictionary.'
                            'Keys in the configuration should be str or class.')

    return pset, parameter_checks


def random_terminals_for_primitive(primitive_set: dict, primitive: Primitive):
    return [random.sample(primitive_set[needed_terminal_type], k=1)[0]
            for needed_terminal_type in primitive.input]


def create_random_individual(primitive_set: dict, min_length: int=1, max_length: int=3) -> Individual:
    individual_length = random.randint(min_length, max_length)
    primitive, = random.sample(primitive_set['prediction'], k=1)
    learner_node = PrimitiveNode(primitive,
                                 data_node=DATA_TERMINAL,
                                 terminals=random_terminals_for_primitive(primitive_set, primitive))
    last_primitive_node = learner_node
    for _ in range(individual_length - 1):
        primitive, = random.sample(primitive_set[DATA_TERMINAL], k=1)
        primitive_node = PrimitiveNode(primitive,
                                       data_node=DATA_TERMINAL,
                                       terminals=random_terminals_for_primitive(primitive_set, primitive))
        last_primitive_node._data_node = primitive_node
        last_primitive_node = primitive_node

    return Individual(learner_node)


if __name__ == '__main__':
    from gama.configuration.classification import clf_config
    pset, param = pset_from_config(clf_config)
    i = create_random_individual(pset)