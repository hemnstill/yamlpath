import pytest

import ruamel.yaml as ry

from yamlpath.enums import PathSearchKeywords
from yamlpath.path import SearchKeywordTerms
from yamlpath.common import KeywordSearches
from yamlpath.exceptions import YAMLPathException
from yamlpath import YAMLPath

class Test_common_keywordsearches():
    """Tests for the KeywordSearches helper class."""

    ###
    # search_matches
    ###
    def test_unknown_search_keyword(self):
        with pytest.raises(YAMLPathException) as ex:
            nodes = list(KeywordSearches.search_matches(
                SearchKeywordTerms(False, None, ""),
                {},
                YAMLPath("/")
            ))


    ###
    # has_child
    ###
    def test_has_child_invalid_param_count(self):
        with pytest.raises(YAMLPathException) as ex:
            nodes = list(KeywordSearches.search_matches(
                SearchKeywordTerms(False, PathSearchKeywords.HAS_CHILD, ""),
                {},
                YAMLPath("/")
            ))
