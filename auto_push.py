#!/usr/bin/env python3
"""
Automatic GitHub Push Script
This script automatically pushes changes to GitHub when updates are completed.
"""

import subprocess
import sys
import os

def run_command(command):
    """Run a shell command and return the result."""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return -1, "", str(e)

def auto_push():
    """Automatically push changes to GitHub."""
    print("🚀 Starting automatic GitHub push...")
    
    # Check git status
    print("📊 Checking git status...")
    returncode, stdout, stderr = run_command("git status")
    
    if returncode != 0:
        print(f"❌ Error checking git status: {stderr}")
        return False
    
    # Check if there are changes to commit
    if "nothing to commit" in stdout:
        print("✅ No changes to commit. Everything is up to date.")
        return True
    
    # Add all changes
    print("📦 Adding changes to staging area...")
    returncode, stdout, stderr = run_command("git add .")
    
    if returncode != 0:
        print(f"❌ Error adding changes: {stderr}")
        return False
    
    # Commit changes
    print("💾 Committing changes...")
    commit_message = f"Auto-commit: Update at {subprocess.getoutput('date /t')} {subprocess.getoutput('time /t')}"
    returncode, stdout, stderr = run_command(f'git commit -m "{commit_message}"')
    
    if returncode != 0:
        print(f"❌ Error committing changes: {stderr}")
        return False
    
    # Push to GitHub
    print("📤 Pushing to GitHub...")
    returncode, stdout, stderr = run_command("git push origin main")
    
    if returncode != 0:
        print(f"❌ Error pushing to GitHub: {stderr}")
        return False
    
    print("✅ Successfully pushed changes to GitHub!")
    print(f"📝 Commit message: {commit_message}")
    return True

def main():
    """Main function."""
    # Change to project directory
    project_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_dir)
    
    success = auto_push()
    
    if success:
        print("\n🎉 Automatic GitHub push completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Automatic GitHub push failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()