import os.path as osp
import sys


def add_path(path):
    if path not in sys.path:
        print(path)
        sys.path.insert(0, path)


this_dir = osp.dirname(__file__)

project_path = osp.dirname(this_dir)
model_path = osp.join(project_path, 'libs', 'models')

add_path(project_path)
add_path(model_path)