import unittest

from codehighlighter.fuzzy_finder_dialog import (
    filter_and_sort_options,
    is_subsequence,
    score_match,
)


class FuzzyFinderDialogTestCase(unittest.TestCase):

    def test_is_subsequence_matches(self):
        # Exact match
        self.assertTrue(is_subsequence("python", "python"))
        # Case insensitive
        self.assertTrue(is_subsequence("PyThOn", "pYtHoN"))
        # Subsequence matches
        self.assertTrue(is_subsequence("py", "python"))
        self.assertTrue(is_subsequence("ptn", "python"))
        self.assertTrue(is_subsequence("yhn", "python"))
        self.assertTrue(is_subsequence("on", "python"))
        # Empty query matches anything
        self.assertTrue(is_subsequence("", "python"))
        self.assertTrue(is_subsequence("", ""))

    def test_is_subsequence_no_matches(self):
        # Wrong order
        self.assertFalse(is_subsequence("yp", "python"))
        # Character not in target
        self.assertFalse(is_subsequence("px", "python"))
        # Query longer than target
        self.assertFalse(is_subsequence("pythons", "python"))

    def test_score_match(self):
        # No match
        self.assertEqual(score_match("yp", "python"), 0)
        # Subsequence match (Score 1)
        self.assertEqual(score_match("ptn", "python"), 1)
        # Substring match (Score 2)
        self.assertEqual(score_match("thon", "python"), 2)
        # Prefix match (Score 3)
        self.assertEqual(score_match("pyt", "python"), 3)
        # Exact match (Score 4)
        self.assertEqual(score_match("python", "python"), 4)
        # Case insensitive exact match (Score 4)
        self.assertEqual(score_match("PyThOn", "pYtHoN"), 4)

    def test_filter_and_sort_options(self):
        options = ["Python", "pydeps", "copy", "C++", "Java"]

        # Searching "py":
        # - "Python" -> prefix match (score 3)
        # - "pydeps" -> prefix match (score 3)
        # - "copy" -> subsequence match (score 1)
        # Expected sorted order:
        # "pydeps" and "Python" have score 3, so sorted alphabetically: "pydeps", then "Python".
        # Then "copy" with score 1.
        self.assertEqual(
            filter_and_sort_options("py", options), ["pydeps", "Python", "copy"]
        )

        # Searching "a":
        # - "Java" -> substring match (score 2)
        # Expected sorted order:
        # "Java"
        self.assertEqual(filter_and_sort_options("a", options), ["Java"])
