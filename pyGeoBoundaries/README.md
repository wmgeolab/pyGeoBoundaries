# pyGeoBoundaries

+ pyGeoBoundaries is a Python package designed for performing data checks and file validation on geoboundary files. The primary purpose of this package is to facilitate the review process for pull requests made to the geoBoundaries repository.

### Methods
+ Collection of checks
    - nameCheck
    - isoCheck
    - boundaryCheck
    - projectionCheck
    - metaCheck
    - checkLicensePng
    - allCheck


### Getting Started

You can find the package on PyPI, making it easily installable using pip.

#### Installation
```bash
pip install pygeoboundaries
```

### Usage

Utilize the provided methods for performing various checks on your geoboundary files.

```bash
from pygeoboundaries import nameCheck
nameCheck("path to your file)
```

### Contribution

Contributions to the project are welcomed. If you notice any bugs or have suggestions for improvements, feel free to let us know. Thank you for your contributions!

### Author

+ Dan Miller Runfola
+ Rohith Reddy Mandala