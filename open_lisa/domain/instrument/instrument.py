from enum import Enum

from open_lisa.domain.instrument.constants import INSTRUMENT_STATUS_AVAILABLE, INSTRUMENT_STATUS_UNAVAILABLE
from open_lisa.exceptions.command_not_found_error import CommandNotFoundError
from open_lisa.exceptions.instrument_unavailable_error import InstrumentUnavailableError


class InstrumentType(Enum):
    SCPI = "scpi"
    CLIB = "clib"

    @staticmethod
    def from_str(self, string_type):
        if string_type == str(InstrumentType.CLIB):
            return InstrumentType.CLIB
        elif string_type == str(InstrumentType.SCPI):
            return InstrumentType.SCPI

    def __str__(self):
        return self.name


# TODO: change name to Instrument when all is integrated and legacy code removed
class InstrumentV2:
    def __init__(self, id, physical_address, brand, model, type, description="",
                 commands=[], pyvisa_resource=None):
        assert isinstance(type, InstrumentType)
        self.id = id
        self.physical_address = physical_address
        self.brand = brand
        self.model = model
        self.description = description
        self.pyvisa_resource = pyvisa_resource
        self._commands = commands

        if pyvisa_resource:
            self.status = INSTRUMENT_STATUS_AVAILABLE
        elif type == InstrumentType.CLIB:
            # TODO: if CLIB instruments are detected with pyvisa we can add
            # physical_address to them and set instrument status correctly
            self.status = INSTRUMENT_STATUS_AVAILABLE
        else:
            # Instrument is SCPI type and no pyvisa resource was provided
            self.status = INSTRUMENT_STATUS_UNAVAILABLE

    def to_dict(self):
        return {
            "id": self.id,
            "physical_address": self.physical_address,
            "brand": self.brand,
            "model": self.model,
            "description": self.description,
            "status": self.status,
        }

    def __str__(self):
        return self.to_dict()

    def send_command(self, command_name, command_parameters_values=[]):
        if not self.status == INSTRUMENT_STATUS_AVAILABLE:
            raise InstrumentUnavailableError(
                "instrument {} {} not available for sending command".format(self.brand, self.model))
        command = self.__get_command_by_name(command_name)
        return command.execute(command_parameters_values)

    def __get_command_by_name(self, command_name):
        for command in self._commands:
            if command.name == command_name:
                return command
        raise CommandNotFoundError("command {} not registered in instrument {} {}".format(
            command_name, self.brand, self.model))