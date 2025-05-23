#!/bin/bash

# Exit on error
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

echo -e "${GREEN}Starting AstroDistro installation...${NC}"

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}Please run as root${NC}"
    exit 1
fi

# Install system dependencies
echo -e "${GREEN}Installing system dependencies...${NC}"
apt-get update
apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    build-essential \
    git \
    wget \
    curl \
    portaudio19-dev \
    libssl-dev \
    libffi-dev \
    libxml2-dev \
    libxslt1-dev \
    zlib1g-dev \
    libjpeg-dev \
    libpng-dev \
    libgirepository1.0-dev \
    libcairo2-dev \
    libpango1.0-dev \
    gir1.2-gtk-3.0 \
    gir1.2-gdk-3.0 \
    gir1.2-glib-2.0

# Install Ollama
echo -e "${GREEN}Installing Ollama...${NC}"
curl -fsSL https://ollama.com/install.sh | sh

# Create installation directory
echo -e "${GREEN}Creating installation directory...${NC}"
mkdir -p /opt/astrodistro

# Copy files
echo -e "${GREEN}Copying files...${NC}"
cp -r src /opt/astrodistro/
cp requirements.txt /opt/astrodistro/
cp README.md /opt/astrodistro/

# Install Python dependencies
echo -e "${GREEN}Installing Python dependencies...${NC}"
pip3 install --upgrade pip setuptools wheel
pip3 install -r requirements.txt

# Install systemd service
echo -e "${GREEN}Installing systemd service...${NC}"
cp astrodistro.service /etc/systemd/system/
systemctl daemon-reload

# Set permissions
echo -e "${GREEN}Setting permissions...${NC}"
chown -R $SUDO_USER:$SUDO_USER /opt/astrodistro
chmod +x /opt/astrodistro/src/main.py

# Enable service
echo -e "${GREEN}Enabling service...${NC}"
systemctl enable astrodistro.service

echo -e "${GREEN}Installation complete!${NC}"
echo -e "${GREEN}To start AstroDistro, run:${NC}"
echo "sudo systemctl start astrodistro.service"
echo -e "${GREEN}To check status:${NC}"
echo "sudo systemctl status astrodistro.service" 