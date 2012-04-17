# nhlib: A New Hazard Library
# Copyright (C) 2012 GEM Foundation
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
import unittest

from nhlib import const
from nhlib.geo import Point
from nhlib.geo.surface.planar import PlanarSurface
from nhlib.tom import PoissonTOM
from nhlib.source.rupture import Rupture, ProbabilisticRupture


def make_rupture(rupture_class, **kwargs):
    default_arguments = {
        'mag': 5.5,
        'rake': 123.45,
        'tectonic_region_type': const.TRT.STABLE_CONTINENTAL,
        'hypocenter': Point(5, 6, 7),
        'surface': PlanarSurface(10, 11, 12,
            Point(0, 0, 1), Point(1, 0, 1),
            Point(1, 0, 2), Point(0, 0, 2)
        )
    }
    default_arguments.update(kwargs)
    kwargs = default_arguments
    rupture = rupture_class(**kwargs)
    for key in kwargs:
        assert getattr(rupture, key) is kwargs[key]
    return rupture


class RuptureCreationTestCase(unittest.TestCase):
    def assert_failed_creation(self, rupture_class, exc, msg, **kwargs):
        with self.assertRaises(exc) as ae:
            make_rupture(rupture_class, **kwargs)
        self.assertEqual(ae.exception.message, msg)

    def test_wrong_trt(self):
        self.assert_failed_creation(Rupture, ValueError,
            "unknown tectonic region type 'Swamp'",
            tectonic_region_type='Swamp'
        )

    def test_negative_magnitude(self):
        self.assert_failed_creation(Rupture, ValueError,
            'magnitude must be positive',
            mag=-1
        )

    def test_zero_magnitude(self):
        self.assert_failed_creation(Rupture, ValueError,
            'magnitude must be positive',
            mag=0
        )

    def test_hypocenter_in_the_air(self):
        self.assert_failed_creation(Rupture, ValueError,
            'rupture hypocenter must have positive depth',
            hypocenter=Point(0, 1, -0.1)
        )

    def test_probabilistic_rupture_negative_occurrence_rate(self):
        self.assert_failed_creation(ProbabilisticRupture, ValueError,
            'occurrence rate must be positive',
            occurrence_rate=-1, temporal_occurrence_model=PoissonTOM(10)
        )

    def test_probabilistic_rupture_zero_occurrence_rate(self):
        self.assert_failed_creation(ProbabilisticRupture, ValueError,
            'occurrence rate must be positive',
            occurrence_rate=0, temporal_occurrence_model=PoissonTOM(10)
        )


class ProbabilisticRuptureTestCase(unittest.TestCase):
    def test_get_probability(self):
        rupture = make_rupture(ProbabilisticRupture,
                               occurrence_rate=1e-2,
                               temporal_occurrence_model=PoissonTOM(10))
        self.assertAlmostEqual(rupture.get_probability(), 0.0951626)
