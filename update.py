from aridity.config import ConfigCtrl
from graphviz import Digraph
from pathlib import Path
from pyven.projectinfo import ProjectInfo
from tempfile import TemporaryDirectory
from urllib.request import urlopen
import json, logging, shutil

log = logging.getLogger(__name__)

def main_update():
    logging.basicConfig(level = logging.DEBUG)
    ctrl = ConfigCtrl()
    ctrl.loadsettings()
    config = ctrl.node
    with urlopen(f"https://api.github.com/users/{config.organization}/repos") as f:
        names = [p['name'] for p in json.load(f)]
    projects = Path(config.projectsdir)
    dot = Digraph(format = 'png')
    for name in names:
        path = projects / name
        if not path.exists():
            log.warning("Skip: %s", name)
            continue
        info = ProjectInfo.seekany(path)
        dot.node(name)
        for dep in info.localrequires():
            dot.edge(name, dep)
    with TemporaryDirectory() as tempdir:
        path = Path(tempdir, 'dependencies')
        dot.render(path)
        path = path.with_name(f"{path.name}.png")
        shutil.copy2(path, Path(__file__).parent / path.name)
