#!/bin/bash

# Exit on error
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

echo -e "${GREEN}Starting AstroDistro build process...${NC}"

# Create necessary directories
mkdir -p src/{kernel,ui,voice,ai}
mkdir -p build
mkdir -p tools

# Install build dependencies
echo -e "${GREEN}Installing build dependencies...${NC}"
sudo apt-get update
sudo apt-get install -y \
    build-essential \
    git \
    wget \
    curl \
    python3 \
    python3-pip \
    cmake \
    ninja-build \
    libssl-dev \
    libncurses5-dev \
    libx11-dev \
    libxext-dev \
    libxrender-dev \
    libxtst-dev \
    libxi-dev \
    libxrandr-dev \
    libxinerama-dev \
    libxcursor-dev \
    libxcomposite-dev \
    libxdamage-dev \
    libxfixes-dev \
    libxrender-dev \
    libxtst-dev \
    libxi-dev \
    libxrandr-dev \
    libxinerama-dev \
    libxcursor-dev \
    libxcomposite-dev \
    libxdamage-dev \
    libxfixes-dev \
    portaudio19-dev \
    python3-dev \
    python3-pyaudio \
    python3-numpy \
    python3-scipy \
    python3-pandas \
    python3-matplotlib \
    python3-seaborn \
    python3-sklearn \
    python3-tensorflow \
    python3-torch \
    python3-transformers \
    python3-sounddevice \
    python3-soundfile \
    python3-webrtcvad \
    python3-speechrecognition \
    python3-pocketsphinx \
    python3-vosk \
    python3-whisper \
    python3-openai \
    python3-ollama

# Download Linux kernel
echo -e "${GREEN}Downloading Linux kernel...${NC}"
KERNEL_VERSION="6.8.0"
wget https://cdn.kernel.org/pub/linux/kernel/v6.x/linux-${KERNEL_VERSION}.tar.xz -P build/
tar xf build/linux-${KERNEL_VERSION}.tar.xz -C build/

# Create Python virtual environment
echo -e "${GREEN}Setting up Python virtual environment...${NC}"
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

echo -e "${GREEN}Build environment setup complete!${NC}"
echo -e "${GREEN}Next steps:${NC}"
echo "1. Configure kernel: cd build/linux-${KERNEL_VERSION} && make menuconfig"
echo "2. Build kernel: make -j$(nproc)"
echo "3. Install kernel: sudo make modules_install && sudo make install" 