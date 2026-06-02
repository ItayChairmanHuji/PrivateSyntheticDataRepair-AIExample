#!/bin/bash
#SBATCH --job-name=relocate-gemini
#SBATCH --output=relocate_%j.log
#SBATCH --error=relocate_%j.err
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=2G
#SBATCH --time=00:30:00
#SBATCH --partition=ALL

# Create a permanent-ish folder in /var/tmp or similar if possible
# Since we need it to survive reboots, we'll use a local scratch if available
# But on many clusters, /tmp or /var/tmp is local to the node.

# Let's check for a shared scratch space first
echo "Checking for scratch space..."
df -h | grep -i scratch || echo "No scratch found"

# If no scratch, we have to copy node to /tmp on EVERY job start.
# This is actually fine for the Zulip bridge job.

echo "Updating Zulip Bridge to handle noexec home..."
