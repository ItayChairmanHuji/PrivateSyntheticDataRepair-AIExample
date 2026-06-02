#!/bin/bash
#SBATCH --job-name=install-gemini-cli
#SBATCH --output=install_cli_%j.log
#SBATCH --error=install_cli_%j.err
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=4G
#SBATCH --time=01:00:00
#SBATCH --partition=ALL

set -e

INSTALL_DIR="$HOME/node_portable"
mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"

echo "Downloading Node.js..."
# Download Node.js 20 (LTS) for Linux x64
wget -q https://nodejs.org/dist/v20.11.1/node-v20.11.1-linux-x64.tar.xz
tar -xJf node-v20.11.1-linux-x64.tar.xz --strip-components=1
rm node-v20.11.1-linux-x64.tar.xz

export PATH="$INSTALL_DIR/bin:$PATH"
echo "Node version: $(node -v)"
echo "NPM version: $(npm -v)"

echo "Installing Gemini CLI..."
# Use a local folder for global-style installation to avoid permission issues
mkdir -p "$HOME/.npm-global"
npm config set prefix "$HOME/.npm-global"
export PATH="$HOME/.npm-global/bin:$PATH"

npm install -g @google/gemini-cli

echo "Gemini CLI installed successfully."
echo "Path to gemini: $(which gemini)"
echo "--------------------------------------------------"
echo "INSTALLATION COMPLETE"
echo "To use it, you will need to add these to your .bashrc:"
echo "export PATH=\$HOME/node_portable/bin:\$HOME/.npm-global/bin:\$PATH"
