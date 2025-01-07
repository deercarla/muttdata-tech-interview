# data-dev-exam-template
This repository is part of the MuttData challenge, solved by me.

## Getting Started:
**(1)** In your terminal, type:

```
git clone https://github.com/deercarla/muttdata-tech-interview.git
```

Or you can download GitHub desktop and clone the repository using the UI tools.

**(2)** Select the folder where you cloned the repository:
```
cd C:\Users\...\Carla--de-Erausquin
```

### Automatic Installation:

**(3)** Run *install.py*
```
python install.py
```

*install.py* comes with two optional parameters
```
--env_dir: path to the virtual environment
--package_dir: path to the package to install
```

If not present, the environment will be installed within the project folder 
and the *package_dir* is defined as the local path to BertStudents.

**(4)** Activate the environment in terminal:

- On Windows:
```
venv\Scripts\activate.bat
```

- On MacOS/Linux:
```
source venv/bin/activate
```


### Manual Installation

**(3)** Create the "env" environment by typing in the terminal:

```
python -m venv env
```

**(4)** Activate it by typing:

- On Windows:
```
env\Scripts\activate.bat
```

- On MacOS/Linux:
```
source env/bin/activate
```

**(5)** Enter the environment folder:
```
cd env
```

**(6)** Type:
```
pip install -e C:[PROJECT_PATH]\Carla--de-Erausquin
```

Alternatively, you can go up one directory from the environment folder and type:
```
pip install .
```
