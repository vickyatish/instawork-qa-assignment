#!/usr/bin/env python3
"""
Fix script for NumPy compatibility issues with scikit-learn and scipy.
This script will create a clean environment with compatible versions.
"""

import subprocess
import sys
import os

def run_command(cmd, description):
    """Run a command and print the result."""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return False

def main():
    print("🔧 AI Test Copilot Environment Fix")
    print("=" * 50)
    
    # Check if we're in a conda environment
    if 'conda' in sys.executable:
        print("📦 Detected conda environment")
        
        # Create a clean conda environment
        env_name = "ai-test-copilot"
        
        print(f"\n🔄 Creating conda environment '{env_name}'...")
        if not run_command(f"conda create -n {env_name} python=3.11 -y", "Creating conda environment"):
            return False
        
        print(f"\n🔄 Activating environment and installing packages...")
        install_cmd = f"""
        conda activate {env_name} && 
        pip install "numpy>=1.20.0,<2.0.0" "scikit-learn>=1.0.0,<1.4.0" "scipy>=1.5.0,<1.10.0" &&
        pip install openai click colorama jsonschema python-dotenv
        """
        
        if not run_command(install_cmd, "Installing compatible packages"):
            return False
            
        print(f"\n✅ Environment '{env_name}' created successfully!")
        print(f"\n📝 To use the fixed environment, run:")
        print(f"   conda activate {env_name}")
        print(f"   cd /Users/yatishsekaran/Downloads/AI-First-Automation-Engineer-Take-home-project-main")
        print(f"   python -m src.cli status")
        
    else:
        print("📦 Detected pip environment")
        
        # Try to fix the current environment
        print("\n🔄 Fixing current environment...")
        
        # Uninstall problematic packages
        run_command("pip uninstall numpy scikit-learn scipy -y", "Uninstalling problematic packages")
        
        # Install compatible versions
        if not run_command("pip install 'numpy>=1.20.0,<2.0.0' 'scikit-learn>=1.0.0,<1.4.0' 'scipy>=1.5.0,<1.10.0'", "Installing compatible packages"):
            return False
            
        print("\n✅ Environment fixed successfully!")
        print("\n📝 You can now run:")
        print("   python -m src.cli status")
    
    return True

if __name__ == "__main__":
    if main():
        print("\n🎉 Fix completed successfully!")
    else:
        print("\n❌ Fix failed. Please check the error messages above.")
        sys.exit(1)
