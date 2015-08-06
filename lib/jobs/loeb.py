__author__="Jason Stewart"
from marc_helpers import MARCModifier
NAME="Loeb Classical Library"

class LoebClassicalLibrary(MARCModifier):
    def __init__(self, marc_file, **kwargs):
        MARCModifier.__init__(self, marc_file, True)

    def processRecord(self,marc_record):
        ''' Method should be overriddden by derived classes.'''
        pass
