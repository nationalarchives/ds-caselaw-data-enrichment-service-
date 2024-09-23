import unittest

from replacer.replacer_pipeline import (
    fixed_year,
    replacer_abbr,
    replacer_caselaw,
    replacer_leg,
)


class TestCitationReplacer(unittest.TestCase):
    """
    This class tests the replacement of the citations within the text itself. This comes from shared.replacer.py
    """

    def test_citation_replacer_1(self):
        citation_match = "[2025] 1 All E.R. 123"  # incorrect citation
        corrected_citation = "[2025] 1 All ER 123"  # in practice, returned via the citation matcher
        year = "2025"
        URI = "#"
        is_neutral = "true"
        text = "In the judgment the incorrect citation is [2025] 1 All E.R. 123."
        replacement_entry = (citation_match, corrected_citation, year, URI, is_neutral)
        replaced_entry = replacer_caselaw(text, replacement_entry)
        assert corrected_citation in replaced_entry
        replacement_string = f'<ref xmlns:uk="https://caselaw.nationalarchives.gov.uk/akn" xmlns="http://docs.oasis-open.org/legaldocml/ns/akn/3.0" uk:type="case" href="{URI}" uk:isNeutral="{is_neutral}" uk:canonical="{corrected_citation}" uk:year="{year}" uk:origin="TNA">{citation_match}</ref>'
        assert replacement_string in replaced_entry

    def test_citation_replacer_2(self):
        citation_match = "[2022] UKET 789123_2012"
        corrected_citation = "[2022] UKET 789123/2012"
        year = "2022"
        URI = "#"
        is_neutral = "true"
        text = "This citation that needs to be changed is [2022] UKET 789123_2012 which discussed..."
        replacement_entry = (citation_match, corrected_citation, year, URI, is_neutral)
        replaced_entry = replacer_caselaw(text, replacement_entry)
        assert corrected_citation in replaced_entry
        replacement_string = f'<ref xmlns:uk="https://caselaw.nationalarchives.gov.uk/akn" xmlns="http://docs.oasis-open.org/legaldocml/ns/akn/3.0" uk:type="case" href="{URI}" uk:isNeutral="{is_neutral}" uk:canonical="{corrected_citation}" uk:year="{year}" uk:origin="TNA">{citation_match}</ref>'
        assert replacement_string in replaced_entry

    def test_citation_replacer_3_no_year(self):
        """Note that this test does not have a year, so there is no uk:year attribute, unlike the others"""
        citation_match = "LR 1 A&E 123"
        corrected_citation = "LR 1 AE 123"
        year = "No Year"
        text = "LR 1 A&E 123 refers to..."
        URI = "#"
        is_neutral = "true"
        replacement_entry = (citation_match, corrected_citation, year, URI, is_neutral)
        replaced_entry = replacer_caselaw(text, replacement_entry)
        assert corrected_citation in replaced_entry
        replacement_string = f'<ref xmlns:uk="https://caselaw.nationalarchives.gov.uk/akn" xmlns="http://docs.oasis-open.org/legaldocml/ns/akn/3.0" uk:type="case" href="{URI}" uk:isNeutral="{is_neutral}" uk:canonical="{corrected_citation}" uk:origin="TNA">LR 1 A&amp;E 123</ref>'
        assert replacement_string in replaced_entry

    def test_citation_replacer_4(self):
        citation_match = "(2022) EWHC 123 (Mercantile)"
        corrected_citation = "[2022] EWHC 123 (Mercantile)"
        year = "2022"
        URI = "#"
        is_neutral = "true"
        text = "I defer to the judgment in (2022) EWHC 123 (Mercantile)."
        replacement_entry = (citation_match, corrected_citation, year, URI, is_neutral)
        replaced_entry = replacer_caselaw(text, replacement_entry)
        assert corrected_citation in replaced_entry
        replacement_string = f'<ref xmlns:uk="https://caselaw.nationalarchives.gov.uk/akn" xmlns="http://docs.oasis-open.org/legaldocml/ns/akn/3.0" uk:type="case" href="{URI}" uk:isNeutral="{is_neutral}" uk:canonical="{corrected_citation}" uk:year="{year}" uk:origin="TNA">{citation_match}</ref>'
        assert replacement_string in replaced_entry

    def test_citation_replacer_5(self):
        citation_match = "[2022] ewca civ 123"
        corrected_citation = "[2022] EWCA Civ 123"
        year = "2022"
        URI = "#"
        is_neutral = "true"
        text = "[2022] ewca civ 123."
        replacement_entry = (citation_match, corrected_citation, year, URI, is_neutral)
        replaced_entry = replacer_caselaw(text, replacement_entry)
        assert corrected_citation in replaced_entry
        replacement_string = f'<ref xmlns:uk="https://caselaw.nationalarchives.gov.uk/akn" xmlns="http://docs.oasis-open.org/legaldocml/ns/akn/3.0" uk:type="case" href="{URI}" uk:isNeutral="{is_neutral}" uk:canonical="{corrected_citation}" uk:year="{year}" uk:origin="TNA">{citation_match}</ref>'
        assert replacement_string in replaced_entry


class TestLegislationReplacer(unittest.TestCase):
    """
    This class tests the replacement of the citations within the text itself. This comes from shared.replacer.py
    """

    def test_citation_replacer_1(self):
        legislation_match = "Adoption and Children Act 2002"  # matched legislation
        href = "http://www.legislation.gov.uk/ukpga/2002/38"
        text = "In their skeleton argument in support of the first ground, Mr Goodwin and Mr Redmond remind the court that the welfare checklist in s.1(4) of the Adoption and Children Act 2002 requires the court, inter alia"
        canonical = "foo"
        replacement_entry = (legislation_match, href, canonical)
        replaced_entry = replacer_leg(text, replacement_entry)
        assert legislation_match in replaced_entry
        replacement_string = '<ref xmlns:uk="https://caselaw.nationalarchives.gov.uk/akn" xmlns="http://docs.oasis-open.org/legaldocml/ns/akn/3.0" uk:type="legislation" href="http://www.legislation.gov.uk/ukpga/2002/38" uk:canonical="foo" uk:origin="TNA">Adoption and Children Act 2002</ref>'
        assert replacement_string in replaced_entry

    def test_citation_replacer_2(self):
        legislation_match = "Children and Families Act 2014"  # matched legislation
        href = "http://www.legislation.gov.uk/ukpga/2014/6/enacted"
        text = "In her first judgment on 31 January, the judge correctly directed herself as to the law, reminding herself that any application for expert evidence in children’s proceedings is governed by s.13 of the Children and Families Act 2014."
        canonical = "bar"
        replacement_entry = (legislation_match, href, canonical)
        replaced_entry = replacer_leg(text, replacement_entry)
        assert legislation_match in replaced_entry
        replacement_string = '<ref xmlns:uk="https://caselaw.nationalarchives.gov.uk/akn" xmlns="http://docs.oasis-open.org/legaldocml/ns/akn/3.0" uk:type="legislation" href="http://www.legislation.gov.uk/ukpga/2014/6/enacted" uk:canonical="bar" uk:origin="TNA">Children and Families Act 2014</ref>'
        assert replacement_string in replaced_entry

    def test_citation_replacer_2_no_enacted(self):
        legislation_match = "Children and Families Act 2014"  # matched legislation
        href = "http://www.legislation.gov.uk/ukpga/2014/6"
        text = "In her first judgment on 31 January, the judge correctly directed herself as to the law, reminding herself that any application for expert evidence in children’s proceedings is governed by s.13 of the Children and Families Act 2014."
        canonical = "bar"
        replacement_entry = (legislation_match, href, canonical)
        replaced_entry = replacer_leg(text, replacement_entry)
        assert legislation_match in replaced_entry
        replacement_string = '<ref xmlns:uk="https://caselaw.nationalarchives.gov.uk/akn" xmlns="http://docs.oasis-open.org/legaldocml/ns/akn/3.0" uk:type="legislation" href="http://www.legislation.gov.uk/ukpga/2014/6" uk:canonical="bar" uk:origin="TNA">Children and Families Act 2014</ref>'
        assert replacement_string in replaced_entry


class TestReplacerAbbr(unittest.TestCase):
    """Unit Tests for `replacer_abbr`"""

    def test_replacer_abbr(self):
        """
        Given a text string and a tuple of original string and abbreviation
            where the original string is contained in the text string
        When replacer_abbr is called with these
        Then a string is returned that looks like the original text string
            with the matching string enclosed by an <abbr> tag with the replacement
            string as the title attribute and TNA as the uk:origin attribute
        """
        text = "This game requires 12 GB of Random Access Memory"
        replacement_entry = ("Random Access Memory", "RAM")

        expected = "This game requires 12 GB of " '<abbr title="RAM" uk:origin="TNA">' "Random Access Memory" "</abbr>"
        assert replacer_abbr(text, replacement_entry) == expected


class TestFixedYear(unittest.TestCase):
    def test_no_year(self):
        assert fixed_year(None) is None

    def test_empty_year(self):
        assert fixed_year("") is None

    def test_gibberish_year(self):
        assert fixed_year("xxx") is None

    def test_real_year(self):
        assert fixed_year("1969") == "1969"

    def test_mixed_year(self):
        """This shouldn't be used anywhere, it's merely documenting the behaviour added whilst fixing the No Year issue"""
        assert fixed_year("In the summer of '69") == "69"
