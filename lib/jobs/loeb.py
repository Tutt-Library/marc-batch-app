__author__="Jason Stewart"
from marc_helpers import MARCModifier
NAME="Loeb Classical Library"

class LoebClassicalLibrary(MARCModifier):
    def __init__(self, marc_file, **kwargs):
        MARCModifier.__init__(self, marc_file, True)

    def processRecord(self,marc_record):
        ''' Method should be overriddden by derived classes.'''
        pass
    
    
    def validate710(self,marc_record):
        """
        :param marc_record: MARC record, required
        """
        self.__remove_field__(marc_record=marc_record,
                              tag='710')
        field730 = Field(tag='710',
                         indicators=['2',' '].
                         subfields=['a','Loeb Classical Library'])
    marc_record.add_field(field730)
    return marc_record
    
    
    def validate730(self,marc_record):
        """
        :param marc_record: MARC record, required
        """
        self.__remove_field__(marc_record=marc_record,
                              tag='730')
        field730 = Field(tag='730',
                         indicators=['0',' '].
                         subfields=['a','Loeb Classical Library'])
    marc_record.add_field(field730)
    return marc_record
