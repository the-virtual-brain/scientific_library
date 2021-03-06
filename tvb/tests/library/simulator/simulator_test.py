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

Tests all the possible combinations of (available) models and integration 
schemes (region and surface based simulations).

.. moduleauthor:: Paula Sanz Leon <sanzleon.paula@gmail.com@>
.. moduleauthor:: Stuart A. Knock <Stuart@tvb.invalid>

"""

import pytest
import numpy
import itertools
from tvb.datatypes.surfaces import CorticalSurface
from tvb.tests.library.base_testcase import BaseTestCase
from tvb.simulator import simulator, models, coupling, integrators, monitors, noise
from tvb.datatypes.connectivity import Connectivity
from tvb.datatypes.cortex import Cortex
from tvb.datatypes.local_connectivity import LocalConnectivity
from tvb.datatypes.region_mapping import RegionMapping
from tvb.simulator.integrators import HeunDeterministic, IntegratorStochastic

MODEL_CLASSES = models.Model.get_known_subclasses().values()
METHOD_CLASSES = integrators.Integrator.get_known_subclasses().values()


class Simulator(object):
    """
    Simulator test class
    
    """

    def __init__(self):
        """
        Initialise the structural information, coupling function, and monitors.
        
        """

        # Initialise some Monitors with period in physical time
        raw = monitors.Raw()
        gavg = monitors.GlobalAverage(period=2 ** -2)
        subsamp = monitors.SubSample(period=2 ** -2)
        tavg = monitors.TemporalAverage(period=2 ** -2)
        eeg = monitors.EEG.from_file()
        eeg.period = 2 ** -2
        eeg2 = monitors.EEG.from_file()
        eeg2.period = 2 ** -2
        eeg2.reference = 'Fp2'  # EEG with a reference electrode
        meg = monitors.MEG.from_file()
        meg.period = 2 ** -2

        self.monitors = (raw, gavg, subsamp, tavg, eeg, eeg2, meg)

        self.method = None
        self.sim = None

    def run_simulation(self, simulation_length=2 ** 2):
        """
        Test a simulator constructed with one of the <model>_<scheme> methods.
        """

        results = [[] for _ in self.monitors]

        for step in self.sim(simulation_length=simulation_length):
            for i, result in enumerate(step):
                if result is not None:
                    results[i].append(result)

        return results

    def configure(self, dt=2 ** -3, model=models.Generic2dOscillator, speed=4.0,
                  coupling_strength=0.00042, method=HeunDeterministic,
                  surface_sim=False,
                  default_connectivity=True):
        """
        Create an instance of the Simulator class, by default use the
        generic plane oscillator local dynamic model and the deterministic 
        version of Heun's method for the numerical integration.
        
        """
        self.method = method

        if default_connectivity:
            white_matter = Connectivity.from_file()
            region_mapping = RegionMapping.from_file(source_file="regionMapping_16k_76.txt")
        else:
            white_matter = Connectivity.from_file(source_file="connectivity_192.zip")
            region_mapping = RegionMapping.from_file(source_file="regionMapping_16k_192.txt")
        region_mapping.surface = CorticalSurface.from_file()

        white_matter_coupling = coupling.Linear(a=numpy.array([coupling_strength]))
        white_matter.speed = numpy.array([speed])  # no longer allow scalars to numpy array promotion

        dynamics = model()

        if issubclass(method, IntegratorStochastic):
            hisss = noise.Additive(nsig=numpy.array([2 ** -11]))
            integrator = method(dt=dt, noise=hisss)
        else:
            integrator = method(dt=dt)

        if surface_sim:
            local_coupling_strength = numpy.array([2 ** -10])
            default_cortex = Cortex.from_file()
            default_cortex.region_mapping_data = region_mapping
            default_cortex.coupling_strength = local_coupling_strength
            if default_connectivity:
                default_cortex.local_connectivity = LocalConnectivity.from_file()
            else:
                default_cortex.local_connectivity = LocalConnectivity()
            default_cortex.local_connectivity.surface = default_cortex.region_mapping_data.surface
        else:
            default_cortex = None

        # Order of monitors determines order of returned values.
        self.sim = simulator.Simulator()
        self.sim.surface = default_cortex
        self.sim.model = dynamics
        self.sim.integrator = integrator
        self.sim.connectivity = white_matter
        self.sim.coupling = white_matter_coupling
        self.sim.monitors = self.monitors
        self.sim.configure()


class TestSimulator(BaseTestCase):
    @pytest.mark.slow
    @pytest.mark.parametrize('model_class,method_class', itertools.product(MODEL_CLASSES, METHOD_CLASSES))
    def test_simulator_region(self, model_class, method_class):
        test_simulator = Simulator()
        test_simulator.configure(model=model_class, method=method_class, surface_sim=False)
        result = test_simulator.run_simulation()

        self.assert_equal(len(test_simulator.monitors), len(result))
        for ts in result:
            assert ts is not None
            assert len(ts) > 0

    @pytest.mark.slow
    @pytest.mark.parametrize('default_connectivity', [True, False])
    def test_simulator_surface(self, default_connectivity):
        """
        This test evaluates if surface simulations run as basic flow.
        """
        test_simulator = Simulator()

        test_simulator.configure(surface_sim=True, default_connectivity=default_connectivity)
        result = test_simulator.run_simulation(simulation_length=2)

        assert len(test_simulator.monitors) == len(result)
