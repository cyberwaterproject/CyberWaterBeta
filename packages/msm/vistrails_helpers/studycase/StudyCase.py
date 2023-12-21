from vistrails.core.modules.vistrails_module import NotCacheable, Module
from vistrails_helpers.utils.vistrail_types import VARIANT_TYPE
from ui_model.StudyCaseModel import StudyCaseModel

class StudyCase(Module, NotCacheable):
    
    TIMERANGE = "timerange"
    SPACERANGE = "spacerange"
    STUDYCASE = "studycase"
    
    _input_ports = [(TIMERANGE, VARIANT_TYPE),
                    (SPACERANGE, VARIANT_TYPE)]
    _output_ports = [(STUDYCASE, VARIANT_TYPE),]

    def compute(self):
        time_range = self.force_get_input(self.TIMERANGE)
        space_range = self.force_get_input(self.SPACERANGE)
        
        study_case = StudyCaseModel(space_range, time_range)
        self.setResult(self.STUDYCASE, study_case)
        