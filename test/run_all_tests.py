# Import build-in modules
import math
import sys

# Import third-party modules
import pytest

if __name__ == "__main__":
    result_tests = pytest.main(["-vv"])
    result_coverage = pytest.main(["--cov"])
    sys.exit(max(result_tests, result_coverage))