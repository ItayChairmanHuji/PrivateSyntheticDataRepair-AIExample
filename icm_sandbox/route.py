import argparse
import os
import shutil
import json

def get_stage_path(stage_num_or_name):
    base_dir = "icm_sandbox"
    for item in os.listdir(base_dir):
        if item.startswith(f"{stage_num_or_name:02}") or item.endswith(stage_num_or_name):
            return os.path.join(base_dir, item)
    return None

def main():
    parser = argparse.ArgumentParser(description="ICM Stage Handoff Router")
    parser.add_argument("--from_stage", required=True, help="Source stage (e.g., 02 or synthesizing)")
    parser.add_argument("--to_stage", required=True, help="Target stage (e.g., 03 or marginals_obtaining)")
    parser.add_argument("--clean", action="store_true", help="Clean target input folder before copying")
    
    args = parser.parse_args()
    
    src_path = get_stage_path(args.from_stage)
    dst_path = get_stage_path(args.to_stage)
    
    if not src_path or not dst_path:
        print(f"Error: Could not find stages {args.from_stage} or {args.to_stage}")
        return

    src_out = os.path.join(src_path, "output")
    dst_in = os.path.join(dst_path, "input")
    
    if not os.path.exists(src_out):
        print(f"Error: Source output folder {src_out} does not exist.")
        return

    if args.clean and os.path.exists(dst_in):
        shutil.rmtree(dst_in)
    
    os.makedirs(dst_in, exist_ok=True)
    
    print(f"Routing artifacts from {src_out} -> {dst_in}...")
    
    count = 0
    for item in os.listdir(src_out):
        s = os.path.join(src_out, item)
        d = os.path.join(dst_in, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, dirs_exist_ok=True)
        else:
            shutil.copy2(s, d)
        count += 1
        print(f"  [+] {item}")
        
    print(f"Success: Routed {count} artifacts.")

if __name__ == "__main__":
    main()
