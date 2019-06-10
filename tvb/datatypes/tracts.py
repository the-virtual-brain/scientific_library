# -*- coding: utf-8 -*-
#
#
# TheVirtualBrain-Framework Package. This package holds all Data Management, and 
# Web-UI helpful to run brain-simulations. To use it, you also need do download
# TheVirtualBrain-Scientific Package (for simulators). See content of the
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
# CITATION:
# When using The Virtual Brain for scientific publications, please cite it as follows:
#
#   Paula Sanz Leon, Stuart A. Knock, M. Marmaduke Woodman, Lia Domide,
#   Jochen Mersmann, Anthony R. McIntosh, Viktor Jirsa (2013)
#       The Virtual Brain: a simulator of primate brain network dynamics.
#   Frontiers in Neuroinformatics (7:10. doi: 10.3389/fninf.2013.00010)
#
#

"""
module docstring
.. moduleauthor:: Mihai Andrei <mihai.andrei@codemart.ro>
"""

from tvb.basic.logger.builder import get_logger
from tvb.datatypes.region_mapping import RegionVolumeMapping
from tvb.basic.neotraits.api import HasTraits, Attr, NArray

LOG = get_logger(__name__)
TRACTS_CHUNK_SIZE = 100


class Tracts(HasTraits):
    """Datatype for results of diffusion imaging tractography."""

    MAX_N_VERTICES = 2 ** 16

    vertices = NArray(
        label="Vertex positions",
        doc="""An array specifying coordinates for the tracts vertices."""
    )

    tract_start_idx = NArray(
        dtype=int,
        label="Tract starting indices",
        doc="""Where is the first vertex of a tract in the vertex array"""
    )

    tract_region = NArray(
        dtype=int,
        label="Tract region index",
        required=False,
        doc="""
            An index used to find quickly all tract emerging from a region
            tract_region[i] is the region of the i'th tract. -1 represents the background
            """
    )

    region_volume_map = Attr(
        field_type=RegionVolumeMapping,
        label="Region volume Mapping used to create the tract_region index",
        required=False
    )

    @property
    def tracts_count(self):
        return len(self.tract_start_idx) - 1

