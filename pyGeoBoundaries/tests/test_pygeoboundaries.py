from pygeoboundaries import __version__
from pygeoboundaries import nameCheck


def test_version():
    assert __version__ == '0.0.1'


def test_nameCheck():
    results = nameCheck("/home/rohith/work/trial/AIA_ADM0.zip","/home/rohith/work/trial/")
    assert results == None
