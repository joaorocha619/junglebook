from typing import Type

from junglebook.sections import Section


def load_section(section_type: Type[Section]) -> Section:
    states = Section.load_states((section_type,), mock=True)
    section = section_type.load(states)
    return section
