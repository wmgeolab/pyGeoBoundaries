from pygeoboundaries import __version__
from pygeoboundaries import metaLoad


def test_version():
    assert __version__ == '0.0.1'


def test_metaLoad():
    results = metaLoad("/home/rohith/work/trial/IND_ADM3.zip")
    assert results == "get on with it"
