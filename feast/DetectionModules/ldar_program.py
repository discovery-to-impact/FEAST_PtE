"""
This module defines the LDARProgram class.
"""

import numpy as np
import copy
from .repair import Repair


class LDARProgram:
    """
    An LDAR program contains one or more detection methods and one or more repair methods. Each LDAR program records
    the find and repair costs associated with all detection and repair methods in the program. The LDAR program
    deploys runs the action methods of each detection and repair method contained in the program. The detection and
    repair methods determine their own behavior at each time step.
    """
    def __init__(self, gas_field, tech_dict):
        """
        :param gas_field: a GasField object
        :param tech_dict: a dict containing all of the detection methods to be employed by the LDAR program. The dict
            must have the form {"name": DetectionMethod}. All of the relationships between detection methods and between
            detection methods and repair methods must be defined by the dispatch_objects specified for each method.
        """
        self.emissions = copy.deepcopy(gas_field.emissions)
        self.emissions_timeseries = []
        self.vents_timeseries = []
        self.tech_dict = tech_dict
        self.repair = {}
        for tech_name, tech in tech_dict.items():
            if type(tech.dispatch_object) is Repair:
                self.repair[tech_name + ' ' + tech.dispatch_object.name] = tech.dispatch_object

    def action(self, time, gas_field):
        """
        Runs the detect method for every tech in tech_dict and runs the repair method
        :param time: the simulation time object
        :param gas_field: the simulation gas_field object
        :return:
        """
        for tech in self.tech_dict.values():
            if hasattr(tech, 'survey_interval') and tech.survey_interval \
                    and np.mod(time.current_time, tech.survey_interval) < time.delta_t:
                tech.action(list(np.linspace(0, gas_field.n_sites - 1, gas_field.n_sites, dtype=int)))
            tech.detect(time, gas_field, self.emissions.get_current_emissions(time))
        for rep in self.repair.values():
            rep.repair(time, self.emissions)
