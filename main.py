#!/usr/bin/env python3
"""
AI Test Case Copilot - Main Entry Point

This is the main entry point for the AI Test Case Copilot application.
It provides a simple interface for processing change requests and managing test cases.
"""

import sys
import os
from src.cli import cli

def main():
    """Main entry point for the AI Test Case Copilot."""
    try:
        # Add the src directory to the Python path
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
        
        # Run the CLI
        cli()
        
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"Fatal error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
