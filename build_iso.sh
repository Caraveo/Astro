#!/bin/bash

# Exit on error
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

echo -e "${GREEN}Starting AstroDistro ISO build process...${NC}"

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}Please run as root${NC}"
    exit 1
fi

# Install required packages
echo -e "${GREEN}Installing build dependencies...${NC}"
apt-get update
apt-get install -y \
    debootstrap \
    squashfs-tools \
    xorriso \
    grub-pc-bin \
    grub-efi-amd64-bin \
    mtools \
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

# Create build directory
BUILD_DIR="build_iso"
mkdir -p $BUILD_DIR
cd $BUILD_DIR

# Create chroot environment
echo -e "${GREEN}Creating chroot environment...${NC}"
debootstrap --arch amd64 --variant=minbase jammy chroot http://archive.ubuntu.com/ubuntu/

# Mount necessary filesystems
mount --bind /dev chroot/dev
mount --bind /run chroot/run
mount -t proc none chroot/proc
mount -t sysfs none chroot/sys

# Create sources.list
cat > chroot/etc/apt/sources.list << EOF
deb http://archive.ubuntu.com/ubuntu/ jammy main restricted universe multiverse
deb http://archive.ubuntu.com/ubuntu/ jammy-updates main restricted universe multiverse
deb http://security.ubuntu.com/ubuntu jammy-security main restricted universe multiverse
EOF

# Copy AstroDistro files
echo -e "${GREEN}Copying AstroDistro files...${NC}"
mkdir -p chroot/opt/astrodistro
cp -r ../src chroot/opt/astrodistro/
cp ../requirements.txt chroot/opt/astrodistro/
cp ../README.md chroot/opt/astrodistro/
cp ../astrodistro.service chroot/etc/systemd/system/

# Create installation script
cat > chroot/opt/astrodistro/install.sh << 'EOF'
#!/bin/bash
cd /opt/astrodistro
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

pip3 install --upgrade pip setuptools wheel
pip3 install -r requirements.txt
systemctl enable astrodistro.service
EOF

chmod +x chroot/opt/astrodistro/install.sh

# Create system configuration
echo -e "${GREEN}Creating system configuration...${NC}"
mkdir -p chroot/etc/systemd/system/getty@tty1.service.d/
cat > chroot/etc/systemd/system/getty@tty1.service.d/override.conf << EOF
[Service]
ExecStart=
ExecStart=-/sbin/agetty --autologin root --noclear %I \$TERM
Type=idle
EOF

# Create startup script
cat > chroot/etc/rc.local << 'EOF'
#!/bin/bash
systemctl start astrodistro.service
exit 0
EOF

chmod +x chroot/etc/rc.local

# Create ISO structure
echo -e "${GREEN}Creating ISO structure...${NC}"
mkdir -p iso/boot/grub
mkdir -p iso/live

# Create grub config
cat > iso/boot/grub/grub.cfg << EOF
set timeout=5
set default=0

menuentry "AstroDistro" {
    linux /live/vmlinuz boot=live quiet splash
    initrd /live/initrd.img
}
EOF

# Copy kernel and initrd
echo -e "${GREEN}Copying kernel and initrd...${NC}"
KERNEL_VERSION=$(ls chroot/boot/vmlinuz-* | sort -V | tail -n1 | xargs basename | sed 's/vmlinuz-//')
cp chroot/boot/vmlinuz-${KERNEL_VERSION} iso/live/vmlinuz
cp chroot/boot/initrd.img-${KERNEL_VERSION} iso/live/initrd.img

# Create filesystem
echo -e "${GREEN}Creating filesystem...${NC}"
mksquashfs chroot iso/live/filesystem.squashfs -comp xz

# Create ISO
echo -e "${GREEN}Creating ISO image...${NC}"
grub-mkrescue -o ../astrodistro.iso iso

# Cleanup
echo -e "${GREEN}Cleaning up...${NC}"
umount chroot/dev
umount chroot/run
umount chroot/proc
umount chroot/sys
rm -rf $BUILD_DIR

echo -e "${GREEN}ISO build complete!${NC}"
echo -e "${GREEN}ISO image created at: $(pwd)/astrodistro.iso${NC}" 