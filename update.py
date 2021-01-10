from aridity.config import ConfigCtrl
from graphviz import Digraph
from pathlib import Path
from pyven.projectinfo import ProjectInfo
from tempfile import TemporaryDirectory
from urllib.request import urlopen
import json, logging, shutil

log = logging.getLogger(__name__)
format = 'svg'

def main_update():
    logging.basicConfig(level = logging.DEBUG)
    ctrl = ConfigCtrl()
    ctrl.loadsettings()
    config = ctrl.node
    projects = Path(config.projectsdir)
    org = config.organization
    with urlopen(f"https://api.github.com/users/{org}/repos") as f:
        names = [p['name'] for p in json.load(f)]
    dot = Digraph(format = format)
    for name in names:
        if org == name:
            continue
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
        path = path.with_name(f"{path.name}.{format}")
        shutil.copy2(path, Path(__file__).parent / path.name)
