#!/usr/bin/env python3
"""
Test script to verify Gemini API connectivity.
This script tests the connection to Google's Gemini 2.0 Flash model.
"""

import os
import sys
from dotenv import load_dotenv
import google.generativeai as genai


def test_gemini_connection():
    """Test the Gemini API connection with a simple prompt."""

    # Load environment variables from .env file
    load_dotenv()

    # Get API key from environment
    api_key = os.getenv('GEMINI_API_KEY')

    # Check if API key is set and valid
    if not api_key:
        print("ERROR: GEMINI_API_KEY not found in environment variables.")
        print("Please set your API key in the .env file.")
        sys.exit(1)

    if api_key == "your_key_here":
        print("WARNING: GEMINI_API_KEY is still set to placeholder value 'your_key_here'")
        print("Please update the .env file with your actual Gemini API key.")
        print("\nTo get a Gemini API key:")
        print("1. Visit https://makersuite.google.com/app/apikey")
        print("2. Create a new API key")
        print("3. Replace 'your_key_here' in .env with your actual key")
        sys.exit(1)

    # Configure the Gemini API
    print("Configuring Gemini API...")
    genai.configure(api_key=api_key)

    try:
        # Initialize the model
        print("Initializing Gemini 2.0 Flash model...")
        model = genai.GenerativeModel('gemini-2.0-flash-exp')

        # Test with a simple prompt
        print("\nSending test prompt to Gemini...")
        test_prompt = "Say 'Hello! Gemini API is connected and working!' in a friendly way."

        response = model.generate_content(test_prompt)

        # Display the response
        print("\n" + "="*60)
        print("SUCCESS! Gemini API Connection Verified")
        print("="*60)
        print("\nModel Response:")
        print(response.text)
        print("\n" + "="*60)
        print("\nAPI Connection Details:")
        print(f"  Model: gemini-2.0-flash-exp")
        print(f"  API Key: {api_key[:8]}...{api_key[-4:] if len(api_key) > 12 else '****'}")
        print("  Status: Connected and Working")
        print("="*60)

        return True

    except Exception as e:
        print("\n" + "="*60)
        print("ERROR: Failed to connect to Gemini API")
        print("="*60)
        print(f"\nError Type: {type(e).__name__}")
        print(f"Error Message: {str(e)}")
        print("\nPossible issues:")
        print("1. Invalid API key")
        print("2. Network connectivity problems")
        print("3. API quota exceeded")
        print("4. Model name might be incorrect")
        print("="*60)
        sys.exit(1)


if __name__ == "__main__":
    print("="*60)
    print("Gemini API Connection Test")
    print("="*60)
    print()

    test_gemini_connection()
