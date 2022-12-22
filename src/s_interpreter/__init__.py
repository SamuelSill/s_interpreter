import subprocess

tag: str = subprocess.check_output(['git', 'describe', '--abbrev=0', '--tags']).decode("ascii").strip()
__version__ = f"{tag}.{subprocess.check_output(['git', 'rev-list', tag + '..HEAD', '--count']).decode('ascii').strip()}"
