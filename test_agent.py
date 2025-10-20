import pytest
from AIBot import run_agent

def test_basic_query():
    response = run_agent("What is the nitrate level in California?")
    assert isinstance(response, str)
    assert len(response) > 0

def test_tool_trigger():
    response = run_agent("Use USGS Water API to get nitrate data for CA")
    assert "nitrate" in response.lower() or "No data found" in response