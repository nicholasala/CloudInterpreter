////////ENGLISH////////

User's Guide

Requirements:

-Ubuntu 16.04 or higher
-GCC 4.9 or higher
-Python 3.6

Procedure:

-Install the dependencies by running the dependencies/install-deps-ubuntu.sh file
-Create a virtualenv through python 3.6
-Activate the previously created venv "source name-venv/bin/activate"
-Install in the following venv the packages numpy and json: "pip install name-package"
-Install the .whl file corresponding to the modified version of open3D required "pip install open3d-0.7.0.0-cp36-cp36m-linux_x86_64.whl".

Start it up:
Inside venv previusly created virtual environment run:

-python3 INPUT STRUCTURE
(INPUT: file to convert or directory of already converted cloud)
(STRUCTURE: structure of file to convert, for example "xyzrgb")

////////ITALIAN////////

Guida all'utilizzo

Requisiti:

-Ubuntu 16.04 o superiore
-GCC 4.9 o superiore
-Python 3.6

Procedura:

-Installare le dipendenze eseguendo il file dependencies/install-deps-ubuntu.sh
-Creare un virtualenv attraverso python 3.6
-Attivare il venv precedentemente creato "source nome-venv/bin/activate"
-Installare nel seguente venv i pacchetti numpy e json: "pip install nome-pacchetto"
-Installare il file .whl corrispondente alla versione modificata di open3D necessaria "pip install open3d-0.7.0.0-cp36-cp36m-linux_x86_64.whl"

Avvio:
All'interno del virtual environment appena costruito, eseguire:

-python3 INPUT STRUCTURE
(INPUT: file da convertire o cartella nuvola convertita)
(STRUCTURE: struttura del file da convertire, per esempio "xyzrgb")

