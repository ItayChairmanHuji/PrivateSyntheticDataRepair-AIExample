import subprocess
import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
import sys
import time

def run_experiment(script: str, overrides: list):
    """
    Runs a single experiment using the specified script with provided overrides.
    """
    cmd = [sys.executable, script] + overrides
    print(f"Starting: {' '.join(cmd)}")
    start_time = time.time()
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    duration = time.time() - start_time
    if result.returncode == 0:
        print(f"Finished: {' '.join(overrides)} (took {duration:.2f}s)")
        return True, result.stdout
    else:
        print(f"Error in experiment {' '.join(overrides)}:\n{result.stderr}")
        return False, result.stderr

def main():
    parser = argparse.ArgumentParser(description="Run multiple research experiments in parallel.")
    parser.add_argument("--workers", type=int, default=4, help="Maximum number of parallel workers.")
    parser.add_argument("--overrides_file", type=str, help="Path to a file containing sets of overrides (one set per line).")
    parser.add_argument("--script", type=str, default="main.py", help="Script to run (default: main.py).")
    
    # Optional: allow passing overrides directly via CLI for simple cases
    # Example: python scripts/run_parallel_experiments.py --workers 2 "repairing=ilp" "repairing=weighted_vc"
    parser.add_argument("overrides", nargs="*", help="Sets of overrides to run in parallel.")

    args = parser.parse_args()

    all_experiment_overrides = []
    
    if args.overrides_file:
        with open(args.overrides_file, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    all_experiment_overrides.append(line.split())
    
    if args.overrides:
        # Each override string passed via CLI is treated as a separate experiment set if it's not a single override
        # For simplicity, if they are passed as "key=val key2=val2", we split them.
        for o_set in args.overrides:
            all_experiment_overrides.append(o_set.split())

    if not all_experiment_overrides:
        print("No experiments to run. Provide overrides via CLI or --overrides_file.")
        return

    print(f"Running {len(all_experiment_overrides)} experiments using {args.script} with {args.workers} workers...")
    
    with ProcessPoolExecutor(max_workers=args.workers) as executor:
        futures = {executor.submit(run_experiment, args.script, overrides): overrides for overrides in all_experiment_overrides}
        
        results = []
        for future in as_completed(futures):
            success, output = future.result()
            results.append(success)

    success_count = sum(results)
    print(f"\nParallel execution complete: {success_count}/{len(all_experiment_overrides)} succeeded.")

if __name__ == "__main__":
    main()
