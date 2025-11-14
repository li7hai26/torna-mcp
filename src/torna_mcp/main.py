#!/usr/bin/env python3
"""
Torna MCP Server CLI

Command-line interface for the Torna MCP Server.
"""

import os
import sys
from pathlib import Path

# Add current directory to Python path for direct execution
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Import main function from server module
from refactored_server import main

if __name__ == "__main__":
    main()
