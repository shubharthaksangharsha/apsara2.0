import subprocess

# List of packages to install using apt-get
apt_packages = [
    "libgirepository1.0-dev",
    "libasound-dev",
    "portaudio19-dev",
    "libportaudio2",
    "libportaudiocpp0"
]

# Install each package using apt-get
for package in apt_packages:
    subprocess.run(["sudo", "apt-get", "install", "-y", package], check=True)

# Install Python packages listed in requirements.txt using pip
subprocess.run(["pip", "install", "-r", "requirements.txt"], check=True)
