import pytest

from junglebook.sections.sensor_metadata import MetadataSection

from test.utils import load_section


@pytest.fixture
def section():
    return load_section(MetadataSection)


class TestMetadataSection:

    pass