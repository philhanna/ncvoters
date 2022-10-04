import os.path

my_dir = os.path.dirname(__file__)
project_root_dir = os.path.abspath(os.path.join(my_dir, ".."))
testdata = os.path.join(project_root_dir, "testdata")

__all__ = [
    'project_root_dir',
    'testdata',
]
