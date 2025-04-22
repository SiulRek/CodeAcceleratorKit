import importlib.util
import io
import os
import sys
import unittest


def load_unittests_from_file(file_path):
    """
    Load unittests from a file and return them.

    Parameters
    ----------
    file_path (str)
        Path to the file containing the unittests.

    Returns
    -------
    unittest.TestSuite
        The unittests loaded from the file.
    """
    test_file_path = os.path.abspath(file_path)

    module_name = os.path.splitext(os.path.basename(test_file_path))[0]

    spec = importlib.util.spec_from_file_location(module_name, test_file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return unittest.defaultTestLoader.loadTestsFromModule(module)


def execute_unittests_from_file(file_path, cwd, verbosity=1):
    """
    Execute unittests from a file and return the output.

    Parameters
    ----------
    file_path (str)
        Path to the file containing the unittests.
    cwd (str)
        Path to the current working directory.
    verbosity (int)
        Verbosity level of the unittests. Default is 1.

    Returns
    -------
    str
        The output of the unittests.
    """
    sys.path.insert(0, cwd)
    tests = load_unittests_from_file(file_path)
    test_output = io.StringIO()
    runner = unittest.TextTestRunner(stream=test_output, verbosity=verbosity)
    runner.run(tests)
    output = test_output.getvalue()
    test_output.close()
    sys.path.pop(0)
    return output


if __name__ == "__main__":
    if len(sys.argv) < 2:
        path = f"tasks/tests/for_tasks/automatic_prompt_test.py"
        cwd = f"."
        verbosity = 1
    else:
        # Assuming the arguments match
        path = sys.argv[1]
        cwd = sys.argv[2]
        verbosity = int(sys.argv[3]) if len(sys.argv) > 2 else 1
    test_results = execute_unittests_from_file(path, cwd, verbosity)
    print(test_results)

