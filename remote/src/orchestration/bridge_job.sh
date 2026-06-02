#!/bin/bash
#SBATCH --job-name=gemini-zulip-bridge
#SBATCH --output=zulip_bridge_%j.log
#SBATCH --error=zulip_bridge_%j.err
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=2G
#SBATCH --time=7-00:00:00
#SBATCH --partition=ALL

# Load your python environment if needed
# source /path/to/your/venv/bin/activate

# Stage node binary to bypass noexec home
cp $HOME/node_portable/bin/node /tmp/node_gemini
chmod +x /tmp/node_gemini

# Trust current workspace for headless mode
export GEMINI_CLI_TRUST_WORKSPACE=true
export PYTHONUNBUFFERED=1

echo "Starting Unlimited Zulip Bridge on $(hostname)"
python remote/src/orchestration/zulip_bridge.py --zuliprc zuliprc --owner "itay.chairman@mail.huji.ac.il"
