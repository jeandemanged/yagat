# YAGAT

**Y**et **A**nother **G**rid **A**nalysis **T**ool

[![Actions Status](https://github.com/jeandemanged/yagat/workflows/CI/badge.svg)](https://github.com/jeandemanged/yagat/actions)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=jeandemanged_yagat&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=jeandemanged_yagat)

[![Release](https://img.shields.io/github/v/release/jeandemanged/yagat)](https://github.com/jeandemanged/yagat/releases/latest)

## Overview

YAGAT provides a graphical user interface built on top of the fantastic [PowSyBl](https://www.powsybl.org) open source
grid analysis libraries.

With YAGAT, no programming skills are required: just download, unzip, and run – you're all set!

Today with YAGAT you can:

- Load grid models from the various formats supported by [PowSyBl](https://www.powsybl.org):
    - PowSyBl native iIDM format
    - CIM/CGMES
    - UCTE-DEF
    - IEEE-CDF
    - MATPOWER
    - Siemens PSS®E
- Display and navigate the grid model:
    - with electrical buses represented in tabular form
    - with per-equipment lists
- Modify generator, load, etc. active power
- Run a Load Flow, visualize solved bus voltages and branch flows

### Rationale

YAGAT was created to address key limitations found in existing open-source grid analysis tools, making it more
accessible for users without programming expertise or advanced technical setups. Here's why YAGAT stands out:

1. **Graphical User Interfaces (GUIs):**  
   Many existing grid analysis tools are command-line-based or require custom scripting. This can be intimidating for
   users unfamiliar with programming. YAGAT fills this gap by offering a user-friendly GUI, allowing users to interact
   with grid models visually and intuitively, without writing a single line of code.

2. **Technical Barriers:**  
   Some tools require extensive programming knowledge or familiarity with complex APIs to perform basic operations like
   running load flow calculations or modifying grid parameters. YAGAT eliminates this barrier, enabling users to perform
   these tasks with just a few clicks.

3. **Complicated Installation Processes:**  
   Installations for many tools often involve dependency management, environment setup, or specific system
   requirements, making it difficult for non-technical users. YAGAT simplifies this process with pre-packaged binaries
   for Windows, Linux, and macOS. Installation is as simple as downloading, unzipping, and running the application.

By addressing these pain points, YAGAT empowers engineers, analysts, and researchers to focus on their work rather than
wrestling with software setup or programming challenges. It democratizes grid analysis, making it accessible to a
broader audience with diverse technical backgrounds.

## Installation

Binary releases are provided for Windows, Linux and macOS on
the [releases page](https://github.com/jeandemanged/yagat/releases).  
No additional software is required for installation.  
Download and extract the zip archive for your platform, then run YAGAT.

Note that YAGAT's author does not own a Mac, please report any issue found running YAGAT on macOS.

## Quick Start

- **Open a sample network**: Go to `File` | `Open Sample network` | `IEEE 9 Bus` to load a sample grid model.
- **Navigate the grid**: Use the tree view on the left to browse through the network model and its elements.
- **Run the Load Flow**: Select `Run` | `Load Flow` to execute the analysis.
    - Once completed, review the solved bus voltages and branch flows.

![yagat quickstart](https://github.com/user-attachments/assets/a5ef2a20-13a8-44f5-b927-8d090d173d73)

## Building from source

With Python 3.12 and e.g. using a Virtual Environment and `pip`.

```bash
# clone the git repository
git clone https://github.com/jeandemanged/yagat.git
cd yagat
```

```bash
# create a virtual environment and install requirements
python -m venv venv
. venv/bin/activate
pip install -r requirements.txt
```

```bash
# build the application
pyinstaller -y yagat.spec
```

YAGAT is then available for your platform in the `dist` directory.

## Roadmap

YAGAT today lacks many features, but you may already find it useful. What is planned for the future is:

### Short-Term to Mid-Term Plans:

- **Grid Import**:
    - modify format-specific import options
- **Grid Export**:
    - modify format-specific export options
- **Grid views**:
    - overall cleanup
    - add tables for grid element parameters (e.g. lines R, X, etc.) display and update
    - add navigation between the different views
- **Grid Topology Updates**:
    - modify switches open/close status, modify equipment connected status
- **Load Flow**:
    - Add ability to save/load the Load Flow parameters
- **Reports**:
    - View Grid import and Load Flow reports in order to troubleshoot e.g. non-convergence

### Future Plans:

- **Security Analysis**:
    - Configure a list of contingencies to simulate
    - Run contingency analysis
    - View contingency violations

## Under the Hood

YAGAT is:

- **Written in Python**: a high-level, general-purpose programming language.
- **Using [PyPowSyBl](https://pypowsybl.readthedocs.io/en/latest/index.html)**: Provides the core grid analysis
  functionalities.
- **Using [Tkinter](https://wiki.python.org/moin/TkInter)**: Supplies the graphical user interface.
- **Using [Tksheet](https://github.com/ragardner/tksheet)**: An amazing tkinter table widget.
- **Using [PyInstaller](https://pyinstaller.org/en/stable/)**: Packages the application.

## Data Confidentiality

We take data confidentiality seriously.
All data processed by the application remains on the user's local machine and is not transmitted to any external
servers.
This ensures complete data privacy for users working with sensitive grid models.

## Contributing and Support

Should you encounter any issues with YAGAT, please let us know.  
We welcome contributions, ideas, and feedback. Please open an [issue](https://github.com/jeandemanged/yagat/issues)
or [pull request](https://github.com/jeandemanged/yagat/pulls) to get involved.
