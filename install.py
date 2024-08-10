import subprocess

# List of packages to install using apt-get
apt_packages = [
    "gobject-introspection",
    "libgirepository1.0-dev",
    "libasound-dev",
    "portaudio19-dev",
    "libportaudio2",
    "libportaudiocpp0",
    "libgirepository1.0-dev",
    "pulseaudio", 
    "ffmpeg",
    "bluez", 
    "sox"
    #"libdbus-1-dev"
]

# Check if apt is not locked
subprocess.run(['sudo', 'apt', 'install', '--fix-broken', '-y'], check=True)
# Install each package using apt-get
for package in apt_packages:
    print('PACKAGE INSTALLING:', package)
    if package == 'libgirepository1.0-dev':
        break
    subprocess.run(["sudo", "apt-get", "install", "-y", package], check=True)

subprocess.run(["sudo", "apt", "update", "-y"], check=True)
# Install Python packages listed in requirements.txt using pip
subprocess.run(["pip", "install", "-r", "requirements.txt"], check=True)

for package in apt_packages[apt_packages.index('libgirepository1.0-dev'):]:
    subprocess.run(["sudo", "apt-get", "install", "-y", package], check=True)

#Playwright 
subprocess.run(["playwright", "install"], check=True)
subprocess.run(["playwright", "install-deps"], check=True)    
