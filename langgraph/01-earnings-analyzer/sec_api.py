"""
SEC EDGAR API Client for fetching company filings and financial data.

This module handles all interactions with the SEC EDGAR database.
The SEC provides free, public access to all company filings - no API key needed!

Key concepts:
- CIK: Central Index Key - SEC's unique identifier for each company
- Ticker: Stock symbol (e.g., AAPL, TSLA)
- Filing types: 10-K (annual), 10-Q (quarterly), 8-K (current events)
"""

import os

import requests
import json
from typing import Optional, Dict, List
from datetime import datetime


class SECClient:
    """Client for interacting with SEC EDGAR API."""
    
    BASE_URL = "https://sec.gov"
    
    def __init__(self, user_agent: str = "Educational Project contact@example.com"):
        """
        Initialize SEC client.
        
        Args:
            user_agent: Required by SEC - identifies who is making requests
                       Format: "YourName your@email.com"
        """
        if user_agent is None:
            user_agent = os.getenv(
                "SEC_USER_AGENT",
                "Educational Project"
            )
        self.headers = {
            "User-Agent": user_agent,
            "Accept-Encoding": "gzip, deflate"
        }
    
    def get_company_cik(self, ticker: str) -> Optional[str]:
        """
        Convert stock ticker to CIK number.
        
        Example: AAPL -> 0000320193
        
        Args:
            ticker: Stock symbol (e.g., "AAPL", "TSLA")
            
        Returns:
            CIK number as string, or None if not found
        """
        try:
            # SEC provides a JSON file mapping tickers to CIKs
            url = f"{self.BASE_URL}/files/company_tickers.json"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            data = response.json()
            
            # Search for ticker (case-insensitive)
            ticker_upper = ticker.upper()
            for key, company in data.items():
                if company.get("ticker", "").upper() == ticker_upper:
                    # CIK needs to be 10 digits with leading zeros
                    cik = str(company["cik_str"]).zfill(10)
                    print(f"✓ Found CIK for {ticker}: {cik}")
                    return cik
            
            print(f"✗ Ticker {ticker} not found")
            return None
            
        except Exception as e:
            print(f"Error fetching CIK: {e}")
            return None
    
    def get_company_facts(self, cik: str) -> Optional[Dict]:
        """
        Get all company facts (financial data) from SEC.
        
        This returns structured financial data in XBRL format.
        Contains historical data for all reported metrics.
        
        Args:
            cik: 10-digit CIK number
            
        Returns:
            Dictionary with company facts, or None if error
        """
        try:
            url = f"{self.BASE_URL}/api/xbrl/companyfacts/CIK{cik}.json"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            print(f"Error fetching company facts: {e}")
            return None
    
    def get_company_submissions(self, cik: str) -> Optional[Dict]:
        """
        Get all filings/submissions for a company.
        
        This includes metadata about every filing (dates, form types, etc.)
        but not the actual content.
        
        Args:
            cik: 10-digit CIK number
            
        Returns:
            Dictionary with submission history, or None if error
        """
        try:
            url = f"{self.BASE_URL}/submissions/CIK{cik}.json"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            print(f"Error fetching submissions: {e}")
            return None
    
    def extract_revenue(self, facts: Dict) -> List[Dict]:
        try:
            # Navigate to revenue data
            revenue_data = facts["facts"]["us-gaap"]["Revenues"]["units"]["USD"]
            
            # Filter to quarterly data
            quarterly = [
                item for item in revenue_data 
                if item.get("fp") in ["Q1", "Q2", "Q3", "Q4"]
            ]
            
            # Format nicely
            results = []
            for item in quarterly:
                results.append({
                    "period": f"Q{item['fp'][1]} {item['fy']}",
                    "value": item["val"],
                    "date": item.get("filed", "")
                })
            
            # Sort by date (newest first)
            results.sort(key=lambda x: x["date"], reverse=True)
            
            return results
            
        except KeyError as e:
            print(f"Revenue data not found: {e}")
            return []
        
    def extract_net_income(self, facts: Dict) -> List[Dict]:
        """
        Extract net income data from company facts.
        
        TODO: Implement this function!
        
        Similar to extract_revenue but look for:
        - "NetIncomeLoss" in us-gaap
        
        Args:
            facts: Company facts dictionary
            
        Returns:
            List of net income entries
        """
        # TODO: Implement net income extraction
        pass  # Remove this and add your code
    
    def get_latest_metrics(self, ticker: str) -> Optional[Dict]:
        """
        Get the most recent financial metrics for a company.
        
        This is a convenience function that combines several API calls.
        
        Args:
            ticker: Stock symbol
            
        Returns:
            Dictionary with latest metrics:
            {
                "ticker": "AAPL",
                "company_name": "Apple Inc.",
                "latest_quarter": "Q4 2024",
                "revenue": 85800000000,
                "net_income": 21400000000,
                "filing_date": "2024-11-01"
            }
        """
        try:
            # Step 1: Get CIK
            cik = self.get_company_cik(ticker)
            if not cik:
                return None
            
            # Step 2: Get submissions to find latest filing
            submissions = self.get_company_submissions(cik)
            if not submissions:
                return None
            
            # TODO: Extract company name from submissions
            company_name = submissions.get("name", "Unknown")
            
            # Step 3: Get company facts for financial data
            facts = self.get_company_facts(cik)
            if not facts:
                return None
            
            # TODO: Extract metrics using the functions above
            # revenues = self.extract_revenue(facts)
            # net_incomes = self.extract_net_income(facts)
            
            # TODO: Get the most recent values
            # latest_revenue = revenues[0] if revenues else None
            # latest_net_income = net_incomes[0] if net_incomes else None
            
            # TODO: Return structured data
            return {
                "ticker": ticker.upper(),
                "company_name": company_name,
                "cik": cik,
                # Add more fields here
            }
            
        except Exception as e:
            print(f"Error getting latest metrics: {e}")
            return None


def test_sec_client():
    """Test function to verify SEC API is working."""
    
    print("🧪 Testing SEC API Client\n")
    
    client = SECClient()
    
    # Test 1: Get CIK for Apple
    print("Test 1: Getting CIK for AAPL...")
    cik = client.get_company_cik("AAPL")
    assert cik is not None, "Failed to get CIK"
    print(f"✓ Success: {cik}\n")
    
    # Test 2: Get company submissions
    print("Test 2: Getting submissions...")
    submissions = client.get_company_submissions(cik)
    assert submissions is not None, "Failed to get submissions"
    print(f"✓ Success: Found {len(submissions['filings']['recent']['accessionNumber'])} recent filings\n")
    
    # Test 3: Get company facts
    print("Test 3: Getting company facts...")
    facts = client.get_company_facts(cik)
    assert facts is not None, "Failed to get facts"
    print(f"✓ Success: Retrieved financial data\n")
    
    # TODO: Add tests for your extract_revenue and extract_net_income functions
    
    print("✅ All tests passed!")


if __name__ == "__main__":
    # Run tests when file is executed directly
    test_sec_client()
    
    # Try getting latest metrics for a company
    print("\n" + "="*50)
    print("Example: Getting latest metrics for Tesla")
    print("="*50 + "\n")
    
    client = SECClient()
    metrics = client.get_latest_metrics("TSLA")
    
    if metrics:
        print(json.dumps(metrics, indent=2))
    else:
        print("Failed to retrieve metrics")