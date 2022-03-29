# -*- coding: utf-8 -*-
"""
Created on Mon Mar 3 10:48:33 2022

@author: Imane.Hafnaoui


Detects legislation references by searching through a lookup table of existing acts.
    - Exact matcher: searches the judgement for exact matches to the legislation title in lookup table.
    - Fuzzy matcher: detects well-formed and malformed citations (parameter: cutoff - confidence ratio to filter the search (min -> 90))
    - Hybrid matcher: narrows down the fuzzy matching to candidate segments in the judgement that contain the pattern [Act YYYY] and 
    performs exact matching otherwise.
    
"""
import pandas as pd
import bs4 as BeautifulSoup
import spacy
from spacy.matcher import PhraseMatcher, Matcher
from spaczz.matcher import FuzzyMatcher
import sys
from time import time
from spacy.lang.en import English
import json

from db_connection import get_hrefs

keys = ['detected_ref', 'start', 'end', 'confidence', 'ref']

# EXACT MATCHING

def search_for_act(title, doc_obj, nlp, cutoff=None, candidates=None):
    # print(title)
    phrase_matcher = PhraseMatcher(nlp.vocab)
    phrase_list = [nlp(title)]
    phrase_matcher.add("Text Extractor", None, *phrase_list)

    matched_items = phrase_matcher(doc_obj)

    matched_text = []
    for match_id, start, end in matched_items:
        span = doc_obj[start: end]
        matched_text.append((span.text, start, end, 100))
        print(matched_text)
    return matched_text

# FUZZY MATCHING

def search_for_act_fuzzy(title, doc_obj, nlp, cutoff=95, candidates=None):
    fuzzy_matcher = FuzzyMatcher(nlp.vocab)
    phrase_list = [nlp(title)]
    options = {"fuzzy_func": "token_sort", "min_r1": 90, "min_r2": cutoff}
    fuzzy_matcher.add("Text Extractor",  phrase_list, kwargs=[options])
    matched_items = fuzzy_matcher(doc_obj)
    matched_text = []
    for match_id, start, end, ratio in matched_items:
        span = doc_obj[start: end]
        matched_text.append((span.text, start, end, ratio))
        print(matched_text)
    return matched_text

# HYBRID MATCHING

def detectCandidate(nlp, docobj):
    # detect possible legislation refs with pattern [Act YYYY]
    pattern = [{"ORTH": "Act"}, {"SHAPE": "dddd"}]
    matcher = Matcher(nlp.vocab)
    matcher.add('Act Matcher', [pattern])
    matches = matcher(docobj)
    return [(start, end) for match_id, start, end in matches]


def hybrid(title, docobj, nlp, cutoff=95, candidates=None):
    act, year = title[:-4], title[-4:]
    act_span = len(nlp(title))
    all_matches = []
    for _, end in candidates:
        # get segment in judgment that contains candidate ref
        segment = nlp(docobj[end-act_span:end-1].text)
        dyear = docobj[end-1:end].text
        # fuzzy match act with segment
        matches = search_for_act_fuzzy(act, segment, nlp, cutoff=cutoff)
        if (len(matches) > 0) & (dyear == year):
            all_matches.extend(
                [(docobj[end-1-e+s:end].text, end-1-e+s, end, ratio) for text, s, e, ratio in matches])
    return all_matches

######

def mergedict(x,b):
    a = {}
    for k,v in b.items(): a[k] = a.get(k, []) + b[k]
    for k,v in x.items(): a[k] = a.get(k, []) + x[k]
    return a

def detect_year_span(docobj, nlp):
    pattern = [{"SHAPE": "dddd"}]
    dmatcher = Matcher(nlp.vocab)
    dmatcher.add('date matcher', [pattern])
    dm = dmatcher(docobj)
    dates = [docobj[start:end].text for match_id, start, end in dm]
    dates = set([int(d) for d in dates if (len(d) == 4) & (d.isdigit())])
    return dates

def lookup_pipe(titles, docobj, nlp, method, conn, cutoff=95):
    results = {}
    candidates = detectCandidate(
        nlp, docobj) if method.__name__ == 'hybrid' else None
    for title in nlp.pipe(titles, batch_size=100):
        matches = method(title.text, docobj, nlp, cutoff, candidates)
        if matches:
            href = get_hrefs(conn, title.text)
            matches_with_refs = []
            for match in matches:
                match_list = list(match)
                match_list.append(href)
                match = tuple(match_list)
                matches_with_refs.append(match)
            results[title.text] = results.get(title.text, []) + matches_with_refs
    return results

######

methods = {
    'exact': search_for_act,
    'hybrid': hybrid
}

def leg_pipeline(leg_titles, docobj, nlp, conn):
    results = []
    dates = detect_year_span(docobj, nlp)
    shorttitles = leg_titles[leg_titles.year.isin(dates)]

    for fuzzy, method in zip([True, False], ('hybrid','exact')):
        titles = shorttitles[shorttitles.for_fuzzy==fuzzy].candidate_titles.drop_duplicates().tolist()
        res = lookup_pipe(titles, docobj, nlp, methods[method], conn)
        results.append(res)

    results = mergedict(results[0], results[1])

    results = dict([(k, [dict(zip(keys, j)) for j in v])
                    for k, v in results.items()])    
    refs = [i for j in results.values() for i in j]

    keys_to_extract = {'ref', 'detected_ref'}
    replacements = []
    for ref in refs:
        replacement = tuple([ref[key] for key in ref.keys() & keys_to_extract])
        replacements.append(replacement)

    return replacements