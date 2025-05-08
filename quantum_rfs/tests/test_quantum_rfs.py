"""
Unit and regression test for the quantum_rfs package.
"""

# Import package, test suite, and other packages as needed
import sys

import pytest

import quantum_rfs


def test_quantum_rfs_imported():
    """Sample test, will always pass so long as import statement worked."""
    assert "quantum_rfs" in sys.modules
