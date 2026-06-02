import zulip
import subprocess
import os
import sys
import argparse
import time
from pathlib import Path

class ZulipGeminiBridge:
    def __init__(self, zuliprc_path: str, owner_email: str):
        self.client = zulip.Client(config_file=zuliprc_path)
        self.owner_email = owner_email
        self.bot_email = self.client.get_profile()['email']
        
        # Paths
        self.node_path = "/tmp/node_gemini"
        self.bundle_path = "/u4/ichairman/.npm-global/lib/node_modules/@google/gemini-cli/bundle/gemini.js"
        self.workspace_root = "/u4/ichairman/final_research"

        print(f"Bot started: {self.bot_email}")
        print(f"Owner: {self.owner_email}")
        print("Mode: Unlimited Gemini CLI (OAuth) + Image Support")

    def find_recent_images(self, since_timestamp):
        """Finds images in the workspace modified since the command started."""
        images = []
        extensions = {'.png', '.jpg', '.jpeg', '.svg', '.pdf'}
        
        # Broaden search paths based on observed cluster structure
        search_dirs = [
            os.path.join(self.workspace_root, "outputs"),
            os.path.join(self.workspace_root, "s06_analysis/output"),
            os.path.join(self.workspace_root, "s06_analysis/notebooks/plots"),
            self.workspace_root
        ]

        for sdir in search_dirs:
            if not os.path.exists(sdir): continue
            for root, _, files in os.walk(sdir):
                for f in files:
                    fpath = os.path.join(root, f)
                    try:
                        mtime = os.path.getmtime(fpath)
                        if any(f.lower().endswith(ext) for ext in extensions):
                            if mtime > since_timestamp:
                                images.append(fpath)
                    except:
                        continue
        return list(set(images))

    def upload_and_send_image(self, original_msg, file_path):
        """Uploads a file to Zulip and sends a link/preview."""
        try:
            with open(file_path, 'rb') as f:
                result = self.client.upload_file(f)
                if result['result'] == 'success':
                    url = result['uri']
                    fname = os.path.basename(file_path)
                    self.send_reply(original_msg, f"🖼️ **Generated Image:** [{fname}]({url})")
                else:
                    self.send_reply(original_msg, f"❌ Failed to upload {os.path.basename(file_path)}")
        except Exception as e:
            self.send_reply(original_msg, f"💥 Upload error: {str(e)}")

    def handle_message(self, msg):
        sender_email = msg['sender_email']
        if sender_email == self.bot_email: return
        if msg['type'] == 'stream': return
        if sender_email != self.owner_email: return

        content = msg['content'].strip()
        if not content: return

        print(f"Processing: {content}")
        # Note the time BEFORE execution to catch images created BY the command
        start_time = time.time()

        try:
            # Execute full Gemini CLI
            result = subprocess.run(
                [self.node_path, self.bundle_path, "--yolo", content],
                capture_output=True,
                text=True,
                timeout=600
            )

            stdout = result.stdout.strip()
            stderr = result.stderr.strip()
            
            # 1. First, find any new images
            recent_images = self.find_recent_images(start_time - 5)

            # 2. Prepare the text response
            response = stdout
            if stderr:
                lines = [l for l in stderr.split('\n') if "FutureWarning" not in l and "Ripgrep" not in l]
                if lines: response += f"\n\n--- Logs ---\n" + "\n".join(lines)

            if not response:
                response = "✅ Task completed."

            if recent_images:
                response += f"\n\n🖼️ **Detected {len(recent_images)} image(s). Uploading now...**"

            if len(response) > 8000:
                response = response[:8000] + "\n... [Truncated]"

            # Send text summary first
            self.send_reply(msg, response)

            # 3. Upload images one by one
            for img in recent_images:
                print(f"Uploading: {img}")
                self.upload_and_send_image(msg, img)

        except Exception as e:
            self.send_reply(msg, f"💥 Bridge Error: {str(e)}")

    def send_reply(self, original_msg, content):
        request = {
            "type": "private",
            "to": [original_msg['sender_email']],
            "content": content,
        }
        self.client.send_message(request)

    def run(self):
        self.client.call_on_each_message(self.handle_message)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Zulip to Gemini CLI Bridge")
    parser.add_argument("--zuliprc", default="zuliprc", help="Path to zuliprc file")
    parser.add_argument("--owner", required=True, help="Your Zulip email address")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.zuliprc):
        print(f"Error: {args.zuliprc} not found.")
        sys.exit(1)

    bridge = ZulipGeminiBridge(args.zuliprc, args.owner)
    bridge.run()
