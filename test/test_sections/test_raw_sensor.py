from unittest.mock import Mock

import pytest

from junglebook.sections.sensor import SensorSection

from test.utils import load_section


@pytest.fixture
def section():
    # return load_section(SensorSection)
    pass

class TestRawSensorSection:

    def test_decrement_index(self, section: SensorSection):
        pass
        # section._sd.sensor_state.fsensor_index = 1
        # section._update_isensor_index = Mock()
        # section._decrement_index()
        #
        # actual_result = section._sd.sensor_state.fsensor_index
        # expected_result = 0
        #
        # assert actual_result == expected_result

    def test_increment_index(self, section: SensorSection):
        pass
        # section._sd.sensor_state.fsensor_index = 0
        # section._update_isensor_index = Mock()
        # section._sd.config_state.foreign_sensors = [1, 2]
        # section._increment_index()
        #
        # actual_result = section._sd.sensor_state.fsensor_index
        # expected_result = 1
        #
        # assert actual_result == expected_result

    def test_update_index(self, section: SensorSection):
        pass
        # section._sd.sensor_state.fsensor_index = 0
        # section._update_isensor_index = Mock()
        # section._sd.sensor_state.fsensors_list = ['A', 'B', 'C']
        # section._sd.sensor_state.sb__fsensor = 'C'
        # section._on_fsensor_change()
        #
        # actual_result = section._sd.sensor_state.fsensor_index
        # expected_result = 2
        #
        # assert actual_result == expected_result
