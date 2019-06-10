# -*- coding: utf-8 -*-
#
#
#  TheVirtualBrain-Scientific Package. This package holds all simulators, and 
# analysers necessary to run brain-simulations. You can use it stand alone or
# in conjunction with TheVirtualBrain-Framework Package. See content of the
# documentation-folder for more details. See also http://www.thevirtualbrain.org
#
# (c) 2012-2017, Baycrest Centre for Geriatric Care ("Baycrest") and others
#
# This program is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.
# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with this
# program.  If not, see <http://www.gnu.org/licenses/>.
#
#
#   CITATION:
# When using The Virtual Brain for scientific publications, please cite it as follows:
#
#   Paula Sanz Leon, Stuart A. Knock, M. Marmaduke Woodman, Lia Domide,
#   Jochen Mersmann, Anthony R. McIntosh, Viktor Jirsa (2013)
#       The Virtual Brain: a simulator of primate brain network dynamics.
#   Frontiers in Neuroinformatics (7:10. doi: 10.3389/fninf.2013.00010)
#
#

"""
.. moduleauthor:: Lia Domide <lia.domide@codemart.ro>
"""

import numpy
from tvb.tests.library.base_testcase import BaseTestCase
from tvb.datatypes.cortex import Cortex
from tvb.datatypes.local_connectivity import LocalConnectivity


class TestConsoleTraited(BaseTestCase):
    """
    Test using traited classes from console.
    """

    def test_assign_complex_attr(self):
        """
        Test scientific methods are executed
        """
        default_cortex = Cortex.from_file()
        default_cortex.coupling_strength = numpy.array([0.0121])
        assert default_cortex.local_connectivity is None

        # default_cortex.local_connectivity = surfaces.LocalConnectivity(cutoff=2, surface=default_cortex)
        # default_cortex.compute_local_connectivity()
        # self.assertTrue(default_cortex.local_connectivity is not None)

        default_lc = LocalConnectivity.from_file()
        default_lc.cutoff = 2
        other_cortex = Cortex(local_connectivity=default_lc)
        assert other_cortex.local_connectivity is not None
