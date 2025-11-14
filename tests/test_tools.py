"""Tests for torna-mcp tools."""

import os
from unittest.mock import MagicMock, patch

import pytest

from torna_mcp.models import DocGetInput, DocPushInput, HttpMethod, ResponseFormat


class TestDocPushInput:
    """Test cases for DocPushInput model."""

    def test_valid_doc_push_input(self):
        """Test creating valid DocPushInput."""
        data = {"name": "Test API", "url": "/api/test", "http_method": "GET"}
        input_data = DocPushInput(**data)
        assert input_data.name == "Test API"
        assert input_data.url == "/api/test"
        assert input_data.http_method == HttpMethod.GET
        assert input_data.is_folder is False

    def test_folder_creation(self):
        """Test creating a folder/category."""
        data = {
            "name": "API Category",
            "url": "",
            "http_method": "GET",
            "is_folder": True,
        }
        input_data = DocPushInput(**data)
        assert input_data.is_folder is True
        assert input_data.url == ""

    def test_optional_params(self):
        """Test optional parameters."""
        data = {
            "name": "Test API",
            "url": "/api/test",
            "http_method": "POST",
            "description": "A test API",
            "content_type": "application/xml",
            "author": "Test Author",
        }
        input_data = DocPushInput(**data)
        assert input_data.description == "A test API"
        assert input_data.content_type == "application/xml"
        assert input_data.author == "Test Author"


class TestDocGetInput:
    """Test cases for DocGetInput model."""

    def test_valid_doc_get_input(self):
        """Test creating valid DocGetInput."""
        data = {"doc_id": "test-doc-id"}
        input_data = DocGetInput(**data)
        assert input_data.doc_id == "test-doc-id"


class TestTools:
    """Test cases for tool functions."""

    def test_format_doc_push_data(self):
        """Test formatting doc push data."""
        from torna_mcp.server import _format_doc_push_data

        # Test data formatting logic
        data = {"name": "Test API", "url": "/api/test", "http_method": "GET"}
        input_data = DocPushInput(**data)
        formatted = _format_doc_push_data(input_data)

        # Verify basic structure
        assert "apis" in formatted
        assert len(formatted["apis"]) == 1
        assert formatted["apis"][0]["name"] == "Test API"
        assert formatted["apis"][0]["url"] == "/api/test"
        assert formatted["apis"][0]["httpMethod"] == "GET"
        assert formatted["apis"][0]["contentType"] == "application/json"
        assert formatted["apis"][0]["isFolder"] is False
        assert formatted["apis"][0]["isShow"] is True

    def test_format_doc_push_data_with_optional_params(self):
        """Test formatting doc push data with optional parameters."""
        from torna_mcp.server import _format_doc_push_data

        data = {
            "name": "Test API with Params",
            "url": "/api/test",
            "http_method": "POST",
            "description": "API description",
            "content_type": "application/xml",
            "request_params": [
                {"name": "userId", "type": "int", "description": "User ID"}
            ],
            "response_params": [
                {"name": "success", "type": "bool", "description": "Success flag"}
            ],
            "author": "Test Author",
        }
        input_data = DocPushInput(**data)
        formatted = _format_doc_push_data(input_data)

        # Verify all parameters are included
        assert formatted["apis"][0]["name"] == "Test API with Params"
        assert formatted["apis"][0]["description"] == "API description"
        assert formatted["apis"][0]["httpMethod"] == "POST"
        assert formatted["apis"][0]["contentType"] == "application/xml"
        assert formatted["apis"][0]["author"] == "Test Author"
        assert len(formatted["apis"][0]["requestParams"]) == 1
        assert len(formatted["apis"][0]["responseParams"]) == 1
