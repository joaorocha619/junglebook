

import pytest

from junglebook.sections.config import ConfigSection
from test.utils import load_section


@pytest.fixture
def section():
    return load_section(ConfigSection)


class TestConfigSection:

    pass
