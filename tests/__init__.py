from pathlib import Path

my_file = Path(__file__)
tests_dir = my_file.parent
project_root = tests_dir.parent
testdata = project_root.joinpath("testdata")
outputs = project_root.joinpath("outputs")

__all__ = [
    'outputs',
    'testdata',
]
