import subprocess

# List of packages to install using apt-get
apt_packages = [
    "libasound-dev",
    "portaudio19-dev",
    "libportaudio2",
    "libportaudiocpp0",
    "gobject-introspection",
    "libgirepository1.0-dev",
    "pulseaudio", 
    "ffmpeg",
    "bluez", 
    "sox"
    #"libdbus-1-dev"
]

# Check if apt is not locked
print('Checking if any apt is not locked')
subprocess.run(['sudo', 'apt', 'install', '--fix-broken', '-y'], check=True)
# Install each package using apt-get
for package in apt_packages:
    if package == 'gobject-introspection':
        print('Breaking...')
        break
    print('PACKAGE INSTALLING:', package)
    subprocess.run(["sudo", "apt-get", "install", "-y", package], check=True)

print('Updating packages...')
subprocess.run(["sudo", "apt", "update", "-y"], check=True)
print('Installing pyaudio')
subprocess.run(["pip", "install", "pyaudio"])
print('Continue installing other packages...')
for package in apt_packages[apt_packages.index('gobject-introspection'):]:
    subprocess.run(["sudo", "apt-get", "install", "-y", package], check=True)

print('INSTALLING PACKAGES FROM requirements.txt')
# Install Python packages listed in requirements.txt using pip
subprocess.run(["pip", "install", "-r", "requirements.txt"], check=True)

print('INSTALLING PLAYWRIGHT DEPENDENCIES')
#Playwright 
subprocess.run(["playwright", "install"], check=True)
subprocess.run(["playwright", "install-deps"], check=True)    

