import subprocess
import os
import sys
from datetime import datetime

def run_command(command, description):
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] {description}")
    print(f"Running: {' '.join(command)}")
    try:
        subprocess.run(command, check=True)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Success: {description}")
    except subprocess.CalledProcessError as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ERROR during {description}")
        print(f"Command failed with exit code {e.returncode}")
        sys.exit(1)

def main():
    print("="*60)
    print("CineMatch AI - Full Model Retraining Pipeline")
    print("="*60)
    print("This workflow will sequentially execute preprocessing, model training, and evaluation.")
    
    # Paths are relative to the project root
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    
    env = os.environ.copy()
    env["PYTHONPATH"] = project_root

    def run_script(script_path, desc):
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] {desc}")
        print(f"Running: python {script_path}")
        try:
            subprocess.run([sys.executable, script_path], check=True, cwd=project_root, env=env)
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Success: {desc}")
        except subprocess.CalledProcessError as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ERROR during {desc}")
            print(f"Command failed with exit code {e.returncode}")
            sys.exit(1)

    # 1. Preprocess
    run_script("backend/scripts/preprocess.py", "Step 1/3: Data Preprocessing")
    
    # 2. Train
    run_script("backend/scripts/train.py", "Step 2/3: Model Training")
    
    # 3. Evaluate
    run_script("backend/scripts/evaluate.py", "Step 3/3: Model Evaluation")
    
    print("\n" + "="*60)
    print("Retraining Pipeline Completed Successfully")
    print("New model artifacts have been saved and will be loaded when the backend is restarted.")
    print("="*60)

if __name__ == "__main__":
    main()
