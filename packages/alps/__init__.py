# VisTrails package for ALPS, Algorithms and Libraries for Physics Simulations
#
# Copyright (C) 2009 - 2010 by Matthias Troyer <troyer@itp.phys.ethz.ch>,
#                              Synge Todo <wistaria@comp-phys.org>
#
# Distributed under the Boost Software License, Version 1.0. (See accompany-
# ing file LICENSE_1_0.txt or copy at http://www.boost.org/LICENSE_1_0.txt)
#
#
##############################################################################

from core.configuration import ConfigurationObject
import platform

identifier = 'org.comp-phys.alps'
version = '2.2.0' # release 2.2.0
name = 'ALPS'


##############################################################################

def package_dependencies():
  return ['edu.utah.sci.vistrails.control_flow', 'edu.utah.sci.vistrails.matplotlib', 'edu.utah.sci.vistrails.spreadsheet', 'edu.utah.sci.vistrails.vtlcreator']


if platform.system()=='Windows':
  configuration = ConfigurationObject(alpspath="C:\\Program Files\\ALPS\\bin",toolpath="C:\\Program Files\\ALPS\\bin",mpirun="",mpiprocs=0,browser="['start','C:\\Program Files\\Internet Explorer\\iexplore.exe']",archives="{}")
else:
  if platform.system()=='Darwin':
    configuration = ConfigurationObject(alpspath="/opt/alps/bin",toolpath="/opt/local/bin",mpirun="['/opt/alps/bin/mpirun','-np']",mpiprocs=0,browser="['open', '-a', 'Safari']",archives="{}",xdisplay=":0.",gnuplot_term="aqua")
  else:
    configuration = ConfigurationObject(alpspath="C:/Program Files/alps/bin",toolpath="",mpirun="['mpirun','-np']",mpiprocs=0,browser="['firefox']",archives="{}",xdisplay="",gnuplot_term="x11 enhanced")
