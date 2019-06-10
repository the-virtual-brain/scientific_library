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
Calculate temporal cross correlation coefficients (Pearson's
coefficient) on a TimeSeries datatype and return a
graph.CorrelationCoefficients dataype. The correlation matrix is
widely used to represent functional connectivity (FC).

.. moduleauthor:: Paula Sanz Leon <paula.sanz-leon@univ-amu.fr>

"""

import numpy
#TODO: Currently built around the Simulator's 4D timeseries -- generalise...
import tvb.datatypes.time_series as time_series
import tvb.datatypes.graph as graph
from tvb.basic.neotraits.api import HasTraits, Attr, Float, narray_describe
from tvb.basic.logger.builder import get_logger

LOG = get_logger(__name__)




class CorrelationCoefficient(HasTraits):
    """
    Compute the node-pairwise pearson correlation coefficient of the
    given input 4D TimeSeries  datatype.
    
    Return a CrossCorrelation datatype, whose values of are between -1
    and 1, inclusive.
    
    See: http://docs.scipy.org/doc/numpy/reference/generated/numpy.corrcoef.html
    """

    time_series = Attr(
        field_type=time_series.TimeSeries,
        label="Time Series",
        required=True,
        doc="""The time-series for which the cross correlation matrices are
        calculated.""")

    t_start = Float(
        label=":math:`t_{start}`",
        default=0.9765625,
        required=True,
        doc="""Time start point (ms). By default it uses the default Monitor sample period.
        The starting time point of a time series is not zero, but the monitor's sample period. """)

    t_end = Float(
        label=":math:`t_{end}`",
        default=1000.,
        required=True,
        doc=""" End time point (ms) """)


    def evaluate(self):
        """
        Compute the correlation coefficients of a 2D array (tpts x nodes).
        Yields an array of size nodes x nodes x state-variables x modes.

        The time interval over which the correlation coefficients are computed 
        is defined by t_start, t_end

        """
        #(nodes, nodes, state-variables, modes)
        input_shape = self.time_series.data.shape
        result_shape = self.result_shape(input_shape)
        LOG.info("result shape will be: %s" % str(result_shape))

        result = numpy.zeros(result_shape)


        t_lo = int((1. / self.time_series.sample_period) * (self.t_start - self.time_series.sample_period))
        t_hi = int((1. / self.time_series.sample_period) * (self.t_end - self.time_series.sample_period))
        t_lo = max(t_lo, 0)
        t_hi = max(t_hi, input_shape[0])

        #One correlation coeff matrix, for each state-var & mode.
        for mode in xrange(result_shape[3]):
            for var in xrange(result_shape[2]):
                current_slice = tuple([slice(t_lo, t_hi + 1), slice(var, var + 1),
                                       slice(input_shape[2]), slice(mode, mode + 1)])
                # TODO: Double check whether this should read from H5 and move to framework
                data = self.time_series.data[current_slice].squeeze()
                result[:, :, var, mode] = numpy.corrcoef(data.T)

        LOG.debug("result")
        LOG.debug(narray_describe(result))

        corr_coeff = graph.CorrelationCoefficients(source=self.time_series,
                                                   array_data=result)
        return corr_coeff


    def result_shape(self, input_shape):
        """Returns the shape of the main result of ...."""
        result_shape = (input_shape[2], input_shape[2],
                        input_shape[1], input_shape[3])
        return result_shape


    def result_size(self, input_shape):
        """
        Returns the storage size in Bytes of the main result of .
        """
        result_size = numpy.sum(map(numpy.prod, self.result_shape(input_shape))) * 8.0  # Bytes
        return result_size


    def extended_result_size(self, input_shape):
        """
        Returns the storage size in Bytes of the extended result of the ....
        That is, it includes storage of the evaluated ... attributes
        such as ..., etc.
        """
        extend_size = self.result_size(input_shape)  # Currently no derived attributes.
        return extend_size



