# YAGAT

**Y**et **A**nother **G**rid **A**nalysis **T**ool

## Overview

YAGAT provides a graphical user interface built on top of the [PowSyBl](https://www.powsybl.org) open source grid analysis libraries.

With YAGAT no computer science skill is required: just download the application and run it.

Today with YAGAT you can:
- Load grid models from the various formats supported by [PowSyBl](https://www.powsybl.org):
  - CIM/CGMES
  - UCTE-DEF
  - IEEE-CDF
  - MATPOWER
  - Siemens PSS®E
- Display and navigate the grid model with electrical buses represented in tabular form
- Run a Load Flow, visualize solved bus voltages and branch flows

## Installation

### Binary releases

Binary releases are provided for Windows, Linux and macOS on the [releases page](https://github.com/jeandemanged/yagat/releases).  
No additional software is required for installation.  
Download and extract the zip archive for your platform, then run YAGAT.

### Building from source

With Python 3.12 and e.g. using a Virtual Environment and `pip`.

```bash
# clone the git repository
git clone https://github.com/jeandemanged/yagat.git
cd yagat
```

```bash
# install requirements
python -m venv venv
. venv/bin/activate
pip install -r requirements.txt
```

```bash
# build the application
pyinstaller -y yagat.spec
```

YAGAT is then available for your platform in the `dist` directory.

## Quick Start

- **Open a sample network**: Go to `File` | `Open Sample network` | `IEEE 9 Bus` to load a sample grid model.
- **Navigate the grid**: Use the tree view on the left to browse through the network model and its elements.
- **Run the Load Flow**: Select `Run` | `Load Flow` to execute the analysis.
  - Once completed, view the solved bus voltages and branch flows for insights into the grid's state.

## Roadmap

YAGAT today lacks many features, but you may already find it useful. What is planned for the future is:

### Short-Term to Mid-Term Plans:
- **General**: A log view
- **Grid Model Navigation**: Tabular views per equipment type
- **Grid Model Updates**: Adjust grid configurations, such as opening/closing switches, changing generator set points, etc.
- **Load Flow**:
  - Complete Load Flow Parameters view
  - Add ability to save/load the Load Flow parameters
  - View Load Flow reports for troubleshooting non-convergence

### Future Plans:
- **Security Analysis**:
  - Configure a list of contingencies to simulate
  - Run contingency analysis
  - View contingency violations

## Under the Hood

YAGAT is:
- **Written in Python**: A versatile language that allows easy integration with other libraries.
- **Using [PyPowSyBl](https://pypowsybl.readthedocs.io/en/latest/index.html)**: Provides the core grid analysis functionalities.
- **Using [Tkinter](https://wiki.python.org/moin/TkInter)**: Supplies the graphical user interface, enabling an intuitive experience for users.
- **Using [PyInstaller](https://pyinstaller.org/en/stable/)**: Packages the application for cross-platform compatibility.

## Data Confidentiality

We take data confidentiality seriously.
All data processed by the application remains on the user's local machine and is not transmitted to any external servers.
This ensures complete data privacy for users working with sensitive grid models.

## Contributing and Support

Should you encounter any issues with YAGAT, please let us know.  
We welcome contributions, ideas, and feedback. Please open an [issue](https://github.com/jeandemanged/yagat/issues)
or [pull request](https://github.com/jeandemanged/yagat/pulls) to get involved.
