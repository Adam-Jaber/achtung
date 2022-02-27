import subprocess
import sys

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

module_list = ['requests', 'pygame']

if __name__ == '__main__':
    for package in module_list:
        install(package)