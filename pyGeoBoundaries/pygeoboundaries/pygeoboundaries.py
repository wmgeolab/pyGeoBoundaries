import os
import zipfile
import requests
import datetime
import pandas as pd
import geopandas as gpd
from io import StringIO
from shapely.validation import explain_validity

admTypes = ["ADM0", "ADM1", "ADM2", "ADM3", "ADM4", "ADM5"]
productTypes = ["gbOpen", "gbAuthoritative", "gbHumanitarian"]

# Define the URLs
countries_url = (
    "https://github.com/wmgeolab/geoBoundaryBot/raw/main/dta/iso_3166_1_alpha_3.csv"
)
licenses_url = "https://github.com/wmgeolab/geoBoundaryBot/raw/main/dta/gbLicenses.csv"

# Fetch CSV data from URLs
countries_csv = requests.get(countries_url).text
licenses_csv = requests.get(licenses_url).text

# Read CSV data into DataFrames
countries = pd.read_csv(StringIO(countries_csv))
licenses = pd.read_csv(StringIO(licenses_csv))

# Extract values from DataFrames
isoList1 = countries["Alpha-3code"].tolist()
licenseList1 = licenses["license_name"].tolist()


def loadFile(path):
    """
    Load File: Read GeoJSON or Shapefile, or extract and read from a zip file.

    Parameters:
    -----------
    path : str : The file path to the GeoJSON, Shapefile, or a zip file containing them.

    Returns:
    --------
    GeoDataFrame
        A GeoDataFrame containing the loaded geometry data.

    Usage:
    ------
    >>> from pygeoboundaries import loadFile
    >>> geom_data = loadFile(path='/path/to/your/file.geojson')
    """
    # Check if the path is a zip file
    if path.endswith(".zip"):
        extracted_folder = "temp_extraction_folder"
        # Create the extraction folder if it doesn't exist
        os.makedirs(extracted_folder)
        # Extract all files from the zip
        with zipfile.ZipFile(path, "r") as zip_ref:
            zip_ref.extractall(extracted_folder)
        # List all extracted files
        extracted_files = os.listdir(extracted_folder)
        # Find the first .geojson or .shp file
        selected_file = next(
            (
                file
                for file in extracted_files
                if file.endswith(".geojson") or file.endswith(".shp")
            ),
            None,
        )
        if selected_file:
            # Construct the path to the selected file
            selected_file_path = os.path.join(extracted_folder, selected_file)
            geom_data = gpd.read_file(selected_file_path)
            return geom_data

    elif path.endswith(".geojson") or path.endswith(".shp"):
        # If the path directly points to a .geojson or .shp file, read it using GeoPandas
        return gpd.read_file(path)
    else:
        raise ValueError(
            "Error: Please give a valid path with either .geojson, .shp extension, or a zip file containing them."
        )


def metaLoad(path):
    """
    Meta Load: Read metadata from a text file or extract from a zip file.

    Parameters:
    -----------
    path : str : The file path to the metadata text file or a zip file containing it.

    Returns:
    --------
    str
        A string containing the loaded metadata.

    Usage:
    ------
    >>> from pygeoboundaries import metaLoad
    >>> metadata = metaLoad(path='/path/to/your/file.txt')
    """
    # Check if the path is a zip file
    if path.endswith(".zip"):
        with zipfile.ZipFile(path, "r") as zip_ref:
            # Get a list of file names in the zip file
            file_names = zip_ref.namelist()

            # Check if there is at least one .geojson or .shp file
            valid_file = any(name.endswith(".txt") for name in file_names)

            if valid_file:
                # Extract the first .geojson or .shp file from the zip
                for name in file_names:
                    if name.endswith(".txt"):
                        zip_ref.extract(name, path="temp_extraction_folder")
                        extracted_path = os.path.join("temp_extraction_folder", name)
                        with open(extracted_path, "r", encoding="utf-8") as file:
                            metaData = file.read()
                            testData = "get on with it"
                            print(testData)
                        return testData

    elif path.endswith(".txt"):
        with open(path, "r", encoding="utf-8") as file:
            metaData = file.read()
        return metaData
    else:
        raise ValueError("Error: Please give a valid path with .txt extension.")


def nameCheck(path):
    """
    Name Check: Check for the presence of a column containing names in the provided GeoDataFrame.

    Parameters:
    -----------
    path : str : The file path to the GeoJSON or Shapefile or zipfile.

    Usage:
    ------
    >>> from pygeoboundaries import nameCheck
    >>> nameCheck(path='/path/to/your/file.geojson')
    """
    geomData = loadFile(path)
    nameC = set(
        ["Name", "name", "NAME", "shapeName", "shapename", "SHAPENAME", "MAX_Name"]
    )
    nameCol = list(nameC & set(geomData.columns))
    if len(nameCol) == 1:
        print("INFO", "Column for name detected: " + str(nameCol[0]))
        try:
            nameExample = geomData[str(nameCol[0])][0]
            nameValues = (
                geomData[geomData[str(nameCol[0])].str.contains(".*", regex=True)][
                    str(nameCol[0])
                ]
            ).count()
            print(
                "INFO", "Names: " + str(nameValues) + " | Example: " + str(nameExample)
            )
        except Exception as e:
            print(
                "WARN", "No name values were found, even though a column was present."
            )


def isoCheck(path):
    """
    ISO Check: Check for the presence of a column containing ISO codes in the provided GeoDataFrame.

    Parameters:
    -----------
    path : str : The file path to the GeoJSON or Shapefile or zipfile.

    Usage:
    ------
    >>> from pygeoboundaries import isoCheck
    >>> isoCheck(path='/path/to/your/file.geojson')
    """
    geomData = loadFile(path)
    nameC = set(
        [
            "ISO",
            "ISO_code",
            "ISO_Code",
            "iso",
            "shapeISO",
            "shapeiso",
            "shape_iso",
            "MAX_ISO_Co",
        ]
    )
    nameCol = list(nameC & set(geomData.columns))
    if len(nameCol) == 1:
        print("INFO", "Column for ISO detected: " + str(nameCol[0]))
        try:
            nameExample = geomData[str(nameCol[0])][0]
            nameValues = (
                geomData[geomData[str(nameCol[0])].str.contains(".*", regex=True)][
                    str(nameCol[0])
                ]
            ).count()
            print(
                "INFO", "ISOs: " + str(nameValues) + " | Example: " + str(nameExample)
            )
        except Exception as e:
            print(
                "WARN", "No ISOs values were found, even though a column was present."
            )


def boundaryCheck(path):
    """
    Boundary Check: Check for valid geometries and whether they extend past the boundaries of the Earth.

    Parameters:
    -----------
    path : str : The file path to the GeoJSON or Shapefile or zipfile.

    Usage:
    ------
    >>> from pygeoboundaries import boundaryCheck
    >>> boundaryCheck(path='/path/to/your/file.geojson')
    """
    geomData = loadFile(path)
    for index, row in geomData.iterrows():
        xmin = row["geometry"].bounds[0]
        ymin = row["geometry"].bounds[1]
        xmax = row["geometry"].bounds[2]
        ymax = row["geometry"].bounds[3]
        tol = 1e-5
        valid = (
            (xmin >= -180 - tol)
            and (xmax <= 180 + tol)
            and (ymin >= -90 - tol)
            and (ymax <= 90 + tol)
        )
        if not valid:
            print(
                "CRITICAL",
                "ERROR: This geometry seems to extend past the boundaries of the earth: "
                + str(explain_validity(row["geometry"])),
            )

        if not row["geometry"].is_valid:
            print(
                "WARN",
                "Something is wrong with this geometry, but we might be able to fix it with a buffer: "
                + str(explain_validity(row["geometry"])),
            )
            if not row["geometry"].buffer(0).is_valid:
                print(
                    "CRITICAL",
                    "ERROR: Something is wrong with this geometry, and we can't fix it: "
                    + str(explain_validity(row["geometry"])),
                )
            else:
                print(
                    "WARN", "A geometry error was corrected with buffer=0 in shapely."
                )


def projectionCheck(path):
    """
    Projection Check: Check if the geometry data has the required EPSG 4326 projection.

    Parameters:
    -----------
    path : str : The file path to the GeoJSON or Shapefile or zipfile.

    Usage:
    ------
    >>> from pygeoboundaries import projectionCheck
    >>> projectionCheck(path='/path/to/your/file.geojson')
    """
    geomData = loadFile(path)
    if geomData.crs == "epsg:4326":
        print("INFO", "Projection confirmed as " + str(geomData.crs))
    else:
        print(
            "CRITICAL",
            "The projection must be EPSG 4326.  The file proposed has a projection of: "
            + str(geomData.crs),
        )


def metaCheck(path):
    """
    Meta Check: Validate metadata information from a text file.

    Parameters:
    -----------
    path : str : The file path to the metadata text file or zipfile that contains meta file.

    Returns:
    --------
    None

    Usage:
    ------
    >>> from pygeoboundaries import metaCheck
    >>> metaCheck(path='/path/to/your/meta.txt')
    """
    metaData = metaLoad(path)
    print("INFO", "Beginning meta.txt validity checks.")

    for m in metaData.splitlines():
        try:
            e = m.split(":")
            if len(e) > 2:
                e[1] = e[1] + e[2]
            key = e[0].strip()
            val = e[1].strip()
        except Exception as e:
            print(
                "WARN",
                "At least one line of meta.txt failed to be read correctly: "
                + str(m)
                + " | "
                + str(e),
            )
            key = "readError"
            val = "readError"

        if ("Year" in key) or ("year" in key):
            # pre 4.0 legacy cleanup
            if ".0" in str(val):
                val = str(val)[:-2]
            try:
                if "to" in val:
                    date1, date2 = val.split(" to ")
                    date1 = datetime.datetime.strptime(date1, "%d-%m-%Y")
                    date2 = datetime.datetime.strptime(date2, "%d-%m-%Y")
                    print("INFO", "Valid date range " + str(val) + " detected.")
                else:
                    year = int(float(val))
                    if (year > 1950) and (year <= datetime.datetime.now().year):
                        print("INFO", "Valid year " + str(year) + " detected.")
                    else:
                        print(
                            "CRITICAL",
                            "The year in the meta.txt file is invalid (expected value is between 1950 and present): "
                            + str(year),
                        )
            except Exception as e:
                print(
                    "CRITICAL",
                    "The year provided in the metadata "
                    + str(val)
                    + " was invalid. This is what I know:"
                    + str(e),
                )

        if "boundary type" in key.lower() and "name" not in key.lower():
            try:
                validTypes = ["ADM0", "ADM1", "ADM2", "ADM3", "ADM4", "ADM5"]
                if val.upper().replace(" ", "") in validTypes:
                    print("INFO", "Valid Boundary Type detected: " + str(val) + ".")
                else:
                    print(
                        "CRITICAL",
                        "The boundary type in the meta.txt file is invalid: "
                        + str(val),
                    )
            except Exception as e:
                print(
                    "CRITICAL",
                    "The boundary type in the meta.txt file was invalid. This is what I know:"
                    + str(e),
                )

        if "iso" in key.lower().strip():
            if len(val) != 3:
                print(
                    "CRITICAL",
                    "ISO is invalid - we expect a 3-character ISO code following ISO-3166-1 (Alpha 3).",
                )
            elif val not in isoList1:
                print(
                    "CRITICAL",
                    "ISO is not on our list of valid ISO-3 codes.  See https://github.com/wmgeolab/geoBoundaryBot/blob/main/dta/iso_3166_1_alpha_3.csv for all valid codes this script checks against.",
                )
            else:
                print("INFO", "Valid ISO detected: " + str(val))

        if "canonical" in key.lower():
            if len(val.replace(" ", "")) > 0:
                if val.lower() not in ["na", "nan", "null"]:
                    print("INFO", "Canonical name detected: " + str(val))
            else:
                print("WARN", "No canonical name detected.")

        if (
            "source" in key.lower()
            and "license" not in key.lower()
            and "data" not in key.lower()
        ):
            if len(val.replace(" ", "")) > 0:
                if val.lower() not in ["na", "nan", "null"]:
                    print("INFO", "Source detected: " + str(val))

        if "release type" in key.lower():
            if val.lower() not in [
                "geoboundaries",
                "gbauthoritative",
                "gbhumanitarian",
                "gbopen",
                "un_salb",
                "un_ocha",
            ]:
                print("CRITICAL", "Invalid release type detected: " + str(val))

            else:
                print("INFO", "Valid Release Type detected: " + str(val))

        if "license" == key.lower():
            # Clean up shorthand license names to long form (i.e., CC-BY --> CC Attribution)
            # Only implementing for very common mass-import issues (i.e., Intergovernmental from HDX)
            if (
                val
                == "Creative Commons Attribution for Intergovernmental Organisations"
            ):
                val = "Creative Commons Attribution 3.0 Intergovernmental Organisations (CC BY 3.0 IGO)"
            if val.lower().strip() not in licenseList1:
                print("CRITICAL", "Invalid license detected: " + str(val))
            else:
                print("INFO", "Valid license type detected: " + str(val))

        if "license notes" in key.lower():
            if len(val.replace(" ", "")) > 0:
                if val.lower() not in ["na", "nan", "null"]:
                    print("INFO", "License notes detected: " + str(val))
            else:
                print("INFO", "No license notes detected.")

        # if("license source" in key.lower()):
        #     if(len(val.replace(" ","")) > 0):
        #         if(val.lower() not in ["na", "nan", "null"]):
        #             print("INFO", "License source detected: " + str(val))

        #             #Check for a png image of the license source.
        #             #Any png or jpg with the name "license" is accepted.
        #             licPic = 0
        #             try:
        #                 with zipfile.ZipFile(wself.sourcePath) as zFb:
        #                     licPic = zFb.read('license.png')
        #             except:
        #                 pass

        #             try:
        #                 with zipfile.ZipFile(self.sourcePath) as zFb:
        #                     licPic = zFb.read('license.jpg')
        #             except:
        #                 pass

        #             if(licPic != 0):
        #                     print("INFO", "License image found.")
        #                     self.metaReq["licenseImage"] = "Image Available"
        #             else:
        #                 print("WARN", "No license image found. We check for license.png and license.jpg.")
        #                 self.metaReq["licenseImage"] = "None Available"
        #         else:
        #             print("CRITICAL", "No license source detected.")
        #             self.metaReq["licenseImage"] = "ERROR: No license source detected."
        #     else:
        #         print("CRITICAL", "No license source detected.")
        #         self.metaReq["licenseImage"] = "ERROR: No license source detected."

        if "link to source data" in key.lower():
            if len(val.replace(" ", "")) > 0:
                if val.lower() not in ["na", "nan", "null"]:
                    print("INFO", "Data Source Found: " + str(val))

                else:
                    print("CRITICAL", "ERROR: No link to source data found.")

            else:
                print("CRITICAL", "ERROR: No link to source data found.")

        if "other notes" in key.lower():
            if len(val.replace(" ", "")) > 0:
                if val.lower() not in ["na", "nan", "null"]:
                    print("INFO", "Other notes detected: " + val)
            else:
                print("WARN", "No other notes detected.  This field is optional.")


def allChecks(path):
    """
    Perform all checks on the given file path.

    Parameters:
    -----------
    path : str : The file path to the data file.

    Returns:
    --------
    None

    Usage:
    ------
    >>> from pygeoboundaries import allChecks
    >>> allChecks(path='/path/to/your/datafile')
    """
    nameCheck(path)
    isoCheck(path)
    boundaryCheck(path)
    projectionCheck(path)
    metaCheck(path)
    print("All checks are passes")


# nameCheck("/home/rohith/work/trial/IND_ADM3.zip")
# metaCheck("/home/rohith/work/trial/AFG_ADM0/meta.txt")
metaLoad("/home/rohith/work/trial/IND_ADM3.zip")
