"""
Replacer logic for first phase enrichment.
Handles the replacements of abbreviations, legislation, and case law.
"""

import re


def fixed_year(year):
    """For some reason, years can be returned as "No Year", despite not being present in the code (outside tests) or the database
    (as far as I can see."""
    if not year:
        return None
    match = re.search(r"\d+", year)
    if match:
        return match.group()
    else:
        return None


def replacer_caselaw(file_data, replacement):
    """
    String replacement in the XML
    :param file_data: XML file
    :param replacement: tuple of citation match and corrected citation
    :return: enriched XML file data
    """

    year = fixed_year(replacement[2])
    year_xml = f'uk:year="{year}" ' if year else ""
    replacement_string = f'<ref uk:type="case" href="{replacement[3]}" uk:isNeutral="{str(replacement[4]).lower()}" uk:canonical="{replacement[1]}" {year_xml}uk:origin="TNA">{replacement[0]}</ref>'
    file_data = str(file_data).replace(replacement[0], replacement_string)
    return file_data


def replacer_leg(file_data, replacement):
    """
    String replacement in the XML
    :param file_data: XML file
    :param replacement: tuple of citation match and corrected citation
    :return: enriched XML file data
    """
    replacement_string = f'<ref uk:type="legislation" href="{replacement[1]}" uk:canonical="{replacement[2]}" uk:origin="TNA">{replacement[0]}</ref>'
    file_data = str(file_data).replace(replacement[0], replacement_string)
    return file_data


def replacer_abbr(file_data, replacement):
    """
    String replacement in the XML
    :param file_data: XML file
    :param replacement: tuple of citation match and corrected citation
    :return: enriched XML file data
    """
    replacement_string = (
        f'<abbr title="{replacement[1]}" uk:origin="TNA">{replacement[0]}</abbr>'
    )
    file_data = str(file_data).replace(str(replacement[0]), replacement_string)
    return file_data


def replacer_pipeline(
    file_data, REPLACEMENTS_CASELAW, REPLACEMENTS_LEG, REPLACEMENTS_ABBR
):
    """
    Pipeline to run replacer_caselaw, replacer_leg, replacer_abbr
    :param file_data: XML file
    :param REPLACEMENTS_CASELAW: list of unique tuples of citation match and corrected citation
    :param REPLACEMENTS_LEG: list of unique tuples of citation match and corrected citation
    :param REPLACEMENTS_ABBR: list of unique tuples of citation match and corrected citation
    :return: enriched XML file data
    """
    for replacement in list(set(REPLACEMENTS_CASELAW)):
        file_data = replacer_caselaw(file_data, replacement)

    for replacement in list(set(REPLACEMENTS_LEG)):
        file_data = replacer_leg(file_data, replacement)

    for replacement in list(set(REPLACEMENTS_ABBR)):
        file_data = replacer_abbr(file_data, replacement)

    return file_data
