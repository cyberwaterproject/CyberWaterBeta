import msm_core
version = "6.0.0"
name = "msm"
identifier = "edu.pitt.hydro.msm"

import os
import sys

curr_dir = r''+os.path.dirname(os.path.abspath(__file__))
sys.path.append(curr_dir)
print "----- INITIALIZING CYBERWATER -----"
def package_dependencies():
    return ['org.vistrails.vistrails.vtk','org.vistrails.vistrails.control_flow']

def package_requirements():
    import vistrails.core.requirements
    from vistrails.core import debug

    if not vistrails.core.requirements.python_module_exists('vtk'):
        debug.warning('vtk is not available. msm will not be able to show grids')
    import vistrails.packages.vtk

    #if not vistrails.core.requirements.python_module_exists('controlflow'):
    #    debug.warning('controlflow is not available. msm will not be able to run iterations')
    #import vistrails.packages.controlflow
