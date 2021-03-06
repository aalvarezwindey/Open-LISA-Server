import ctypes
from enum import Enum

from open_lisa.exceptions.invalid_command_parameter_value_error import InvalidCommandParameterValueError


class CommandParameterType(Enum):
    FLOAT = "float"
    INT = "int"
    STRING = "string"

    def __str__(self):
        return self.name


class CommandParameter():
    def __init__(self, type, position, description=''):
        assert isinstance(type, CommandParameterType)
        self.type = type
        self.position = position
        self.description = description

    def validate_value(self, value):
        try:
            if self.type == CommandParameterType.FLOAT:
                return float(value)
            if self.type == CommandParameterType.INT:
                int(value)
                if str(int(value)) != str(value):  # it is a float
                    raise ValueError
                return int(value)
            if self.type == CommandParameterType.STRING:
                str(value)
                return str(value)
        except ValueError:
            raise InvalidCommandParameterValueError(
                value_provided=value, expected_type=self.type)

    @staticmethod
    def from_dict(parameter_dict):
        return CommandParameter(
            type=CommandParameterType[parameter_dict["type"]],
            position=parameter_dict["position"],
            description=parameter_dict["description"],
        )

    def to_dict(self):
        return {
            "position": self.position,
            "type": str(self.type),
            "description": self.description
        }

    def to_ctype(self):
        if self.type == CommandParameterType.INT:
            return ctypes.c_int
        elif self.type == CommandParameterType.FLOAT:
            return ctypes.c_float
        elif self.type == CommandParameterType.STRING:
            return ctypes.c_char_p
