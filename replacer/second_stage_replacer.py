# -*- coding: utf-8 -*-
"""
Replacer logic for second and third phase enrichment.
Handles the replacements of oblique references and legislation provisions.
"""


import re
from itertools import groupby
from typing import Dict, List, Tuple, Union

from bs4 import BeautifulSoup

LegislationReference = Tuple[Tuple[int, int], str]
LegislationReferenceReplacements = List[Dict[str, Union[str, int]]]


def split_string(text: str, split_points: List[int]) -> List:
    """
    Splits a string at given points in the text
    :param text: some string of text
    :param split_points: list of positions to split between
    :return: list of split strings
    """
    return list(
        map(lambda x: text[slice(*x)], zip(split_points, split_points[1:] + [None]))
    )


def replace_references(
    text: str, reference_replacements: LegislationReferenceReplacements
) -> str:
    """
    Replaces references in text according to the reference_replacements list
    :param text: original text string
    :param reference_replacements: list of dict of references and replacement information
    :return: string with replaced references
    """
    split_points: List[int] = [
        split_point
        for reference_replacement in reference_replacements
        if isinstance((split_point := reference_replacement.get("ref_position")), int)
    ]
    split_text = split_string(text, split_points)
    enriched_text = text[: split_points[0]]
    for sub_text, reference_replacement in zip(split_text, reference_replacements):
        detected_ref = reference_replacement["detected_ref"]
        if not isinstance(detected_ref, str):
            continue
        ref_tag = reference_replacement["ref_tag"]
        if not isinstance(ref_tag, str):
            continue
        enriched_text += re.sub(
            re.escape(detected_ref),
            ref_tag,
            sub_text,
        )

    return enriched_text


def replace_references_by_paragraph(
    file_data: BeautifulSoup, reference_replacements: LegislationReferenceReplacements
) -> str:
    """
    Replaces references in the file_data xml by paragraph
    :param file_data: XML file
    :param reference_replacements: list of dict of detected references
    :return: enriched XML file data string
    """

    def key_func(k):
        return k["ref_para"]

    paragraphs = file_data.find_all("p")
    ordered_reference_replacements = sorted(reference_replacements, key=key_func)

    for paragraph_number, paragraph_reference_replacements in groupby(
        ordered_reference_replacements, key=key_func
    ):
        paragraph_string = str(paragraphs[paragraph_number])
        replacement_paragraph_string = replace_references(
            paragraph_string, list(paragraph_reference_replacements)
        )
        replacement_paragraph = BeautifulSoup(replacement_paragraph_string, "lxml").p
        paragraphs[paragraph_number].replace_with(replacement_paragraph)
    return str(file_data)


def oblique_replacement(
    file_data: str, reference_replacements: LegislationReferenceReplacements
) -> str:
    """
    Replaces references in the file_data xml
    :param file_data: XML file
    :param replacements: list of dict of resolved oblique refs
    :return: enriched XML file data
    """
    enriched_text = replace_references(file_data, reference_replacements)
    return enriched_text
