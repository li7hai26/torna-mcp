"""
Torna MCP Server

A MCP (Model Context Protocol) server for interacting with Torna API documentation platform.

This package provides tools to interact with Torna OpenAPI for managing API documentation.

Example:
    from torna_mcp import torna_mcp_server

    # Start the server
    torna_mcp_server.run()
"""

__version__ = "0.1.0"
__author__ = "阿拉丁神灯"
__email__ = "li7hai26@gmail.com"

from .server import torna_mcp_server

__all__ = ["torna_mcp_server"]
