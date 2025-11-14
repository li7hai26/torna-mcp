from setuptools import setup, find_packages
import os

# 读取README文件
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "Torna MCP Server - A MCP server for interacting with Torna API documentation platform"

setup(
    name="torna-mcp",
    version="0.1.2",
    description="A MCP (Model Context Protocol) server for interacting with Torna API documentation platform",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    author="阿拉丁神灯",
    author_email="li7hai26@gmail.com",
    url="https://github.com/li7hai26/torna-mcp",
    license="MIT",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "httpx>=0.25.0",
        "pydantic>=2.0.0",
        "fastmcp>=0.3.0",
    ],
    python_requires=">=3.11",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    keywords=["mcp", "torna", "api-documentation", "claude", "llm", "protocol"],
    entry_points={
        "console_scripts": [
            "torna-mcp=torna_mcp.main:main",
        ],
    },
    include_package_data=True,
)