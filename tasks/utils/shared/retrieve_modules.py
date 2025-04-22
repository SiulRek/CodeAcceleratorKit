import json
import os
import sys

import pkg_resources
import stdlib_list

package_to_import_name = {
    "Pillow": "PIL",
    "scikit-learn": "sklearn",
    "_warnings": "warnings",
    "PyYAML": "yaml",
    "python-dateutil": "dateutil",
    "opencv-python": "cv2",
    # Add other package names here
}


def retrieve_modules(cwd):
    """
    Retrieves names of standard library modules and third-party modules in the
    current Python environment. Stores them in a JSON file under
    'standard_library' and 'third_party' keys.

    Parameters
    ----------
    cwd (str)
        The current working directory. Used to find local modules.
    """

    standard_libs = stdlib_list.stdlib_list()
    standard_libs = [lib for lib in standard_libs if "." not in lib]
    for i, lib in enumerate(standard_libs):
        if lib in package_to_import_name:
            standard_libs[i] = package_to_import_name[lib]

    third_party_libs = [dist.project_name for dist in pkg_resources.working_set]
    third_party_libs = [lib for lib in third_party_libs if "." not in lib]
    for i, lib in enumerate(third_party_libs):
        if lib in package_to_import_name:
            third_party_libs[i] = package_to_import_name[lib]

    local_libs = os.listdir(cwd)
    local_libs = [lib.replace(".py", "") for lib in local_libs]
    local_libs = [lib for lib in local_libs if "." not in lib]
    modules_dict = {
        "standard_library": standard_libs,
        "third_party": third_party_libs,
        "local": local_libs,
    }

    modules_info = {"modules_info": modules_dict}
    return modules_info


if __name__ == "__main__":
    cwd = os.getcwd()
    json_path = None

    if len(sys.argv) > 2:
        cwd = sys.argv[1]
        json_path = sys.argv[2]

    modules_info = retrieve_modules(cwd)

    if json_path:
        print(f"Writing modules info to {json_path}")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(modules_info, f, indent=4)
