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
#   The Virtual Brain: a simulator of primate brain network dynamics.
#   Frontiers in Neuroinformatics (7:10. doi: 10.3389/fninf.2013.00010)
#
#

"""
Filler analyzer: Takes a TimeSeries object and returns two Floats.


These metrics are described and used in:

Hellyer et al. The Control of Global Brain Dynamics: Opposing Actions
of Frontoparietal Control and Default Mode Networks on Attention. 
The Journal of Neuroscience, January 8, 2014,  34(2):451– 461

Proxy of spatial coherence (V): 

Proxy metastability (M): the variability in spatial coherence of the signal
globally or locally (within a network) over time.

Proxy synchrony (S) : the reciprocal of mean spatial variance across time.

.. moduleauthor:: Paula Sanz Leon <paula.sanz-leon@univ-amu.fr>

"""
import numpy

import tvb.analyzers.metrics_base as metrics_base
from tvb.basic.logger.builder import get_logger


LOG = get_logger(__name__)


def remove_mean(x, axis):
    """
    Remove mean from numpy array along axis
    """
    # Example for demean(x, 2) with x.shape == 2,3,4,5
    # m = x.mean(axis=2) collapses the 2'nd dimension making m and x incompatible
    # so we add it back m[:,:, np.newaxis, :]
    # Since the shape and axis are known only at runtime
    # Calculate the slicing dynamically
    idx = [slice(None)] * x.ndim
    idx[axis] = numpy.newaxis
    return x - x.mean(axis=axis)[idx]


class ProxyMetastabilitySynchrony(metrics_base.BaseTimeseriesMetricAlgorithm):
    r"""
    Subtract the mean time-series and compute. 

    Input:
    TimeSeries DataType
    
    Output: 
    Float, Float
    
    The two metrics given by this analyzers are a proxy for metastability and synchrony. 
    The underlying dynamical model used in the article was the Kuramoto model.

    .. math::
            V(t) &= \frac{1}{N} \sum_{i=1}^{N} |S_i(t) - <S(t)>| \\
            M(t) &= \sqrt{E[V(t)^{2}]-(E[V(t)])^{2}} \\
            S(t) &= \frac{1}{\bar{V(t)}}

    """

    def evaluate(self):
        """
        Compute the zero centered variance of node variances for the time_series.
        """
        cls_attr_name = self.__class__.__name__ + ".time_series"
        # self.time_series.trait["data"].log_debug(owner=cls_attr_name)
        
        shape = self.time_series.data.shape
        tpts = shape[0]

        if self.start_point != 0.0:
            start_tpt = self.start_point / self.time_series.sample_period
            LOG.debug("Will discard: %s time points" % start_tpt)
        else: 
            start_tpt = 0

        if start_tpt > tpts:
            LOG.warning("The time-series is shorter than the starting point")
            LOG.debug("Will divide the time-series into %d segments." % self.segment)
            # Lazy strategy
            start_tpt = int((self.segment - 1) * (tpts // self.segment))

        start_tpt = int(start_tpt)
        time_series_diffs = remove_mean(self.time_series.data[start_tpt:, :], axis=2)
        v_data = abs(time_series_diffs).mean(axis=2)

        #handle state-variables & modes
        cat_tpts = v_data.shape[0] * shape[1] * shape[3]
        v_data = v_data.reshape((cat_tpts, ), order="F")
        #std across time-points
        metastability = v_data.std(axis=0)
        synchrony = 1. / v_data.mean(axis=0)
        return {"Metastability": metastability,
                "Synchrony": synchrony}

