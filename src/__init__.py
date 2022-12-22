import subprocess

__version__ = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).decode('ascii').strip()
