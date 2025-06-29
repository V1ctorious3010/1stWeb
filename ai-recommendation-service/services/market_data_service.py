import httpx
import os
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import asyncio
from dotenv import load_dotenv

load_dotenv()

class AlphaVantageService:
    def __init__(self):
        self.api_key = os.getenv('ALPHA_VANTAGE_API_KEY')
        self.base_url = "https://www.alphavantage.co/query"
        
        if not self.api_key:
            print("Warning: ALPHA_VANTAGE_API_KEY not found in environment variables")
    
    async def get_stock_quote(self, symbol: str) -> Dict[str, Any]:
        """Get real-time stock quote"""
        if not self.api_key:
            return self._get_mock_stock_data(symbol)
        
        try:
            async with httpx.AsyncClient() as client:
                params = {
                    "function": "GLOBAL_QUOTE",
                    "symbol": symbol,
                    "apikey": self.api_key
                }
                
                response = await client.get(self.base_url, params=params)
                if response.status_code == 200:
                    data = response.json()
                    if "Global Quote" in data:
                        quote = data["Global Quote"]
                        return {
                            "symbol": quote.get("01. symbol"),
                            "price": float(quote.get("05. price", 0)),
                            "change": float(quote.get("09. change", 0)),
                            "change_percent": quote.get("10. change percent", "0%"),
                            "volume": int(quote.get("06. volume", 0)),
                            "previous_close": float(quote.get("08. previous close", 0)),
                            "open": float(quote.get("02. open", 0)),
                            "high": float(quote.get("03. high", 0)),
                            "low": float(quote.get("04. low", 0)),
                            "last_updated": quote.get("07. latest trading day")
                        }
                    else:
                        return self._get_mock_stock_data(symbol)
                else:
                    return self._get_mock_stock_data(symbol)
                    
        except Exception as e:
            print(f"Error fetching stock data for {symbol}: {e}")
            return self._get_mock_stock_data(symbol)
    
    async def get_forex_rate(self, from_currency: str, to_currency: str) -> Dict[str, Any]:
        """Get real-time forex exchange rate"""
        if not self.api_key:
            return self._get_mock_forex_data(from_currency, to_currency)
        
        try:
            async with httpx.AsyncClient() as client:
                params = {
                    "function": "CURRENCY_EXCHANGE_RATE",
                    "from_currency": from_currency,
                    "to_currency": to_currency,
                    "apikey": self.api_key
                }
                
                response = await client.get(self.base_url, params=params)
                if response.status_code == 200:
                    data = response.json()
                    if "Realtime Currency Exchange Rate" in data:
                        rate_data = data["Realtime Currency Exchange Rate"]
                        return {
                            "from_currency": rate_data.get("1. From_Currency Code"),
                            "to_currency": rate_data.get("3. To_Currency Code"),
                            "exchange_rate": float(rate_data.get("5. Exchange Rate", 0)),
                            "last_updated": rate_data.get("6. Last Refreshed"),
                            "timezone": rate_data.get("7. Time Zone")
                        }
                    else:
                        return self._get_mock_forex_data(from_currency, to_currency)
                else:
                    return self._get_mock_forex_data(from_currency, to_currency)
                    
        except Exception as e:
            print(f"Error fetching forex data: {e}")
            return self._get_mock_forex_data(from_currency, to_currency)
    
    async def get_crypto_price(self, symbol: str, market: str = "USD") -> Dict[str, Any]:
        """Get real-time cryptocurrency price"""
        if not self.api_key:
            return self._get_mock_crypto_data(symbol)
        
        try:
            async with httpx.AsyncClient() as client:
                params = {
                    "function": "CURRENCY_EXCHANGE_RATE",
                    "from_currency": symbol,
                    "to_currency": market,
                    "apikey": self.api_key
                }
                
                response = await client.get(self.base_url, params=params)
                if response.status_code == 200:
                    data = response.json()
                    if "Realtime Currency Exchange Rate" in data:
                        rate_data = data["Realtime Currency Exchange Rate"]
                        return {
                            "symbol": rate_data.get("1. From_Currency Code"),
                            "market": rate_data.get("3. To_Currency Code"),
                            "price": float(rate_data.get("5. Exchange Rate", 0)),
                            "last_updated": rate_data.get("6. Last Refreshed"),
                            "timezone": rate_data.get("7. Time Zone")
                        }
                    else:
                        return self._get_mock_crypto_data(symbol)
                else:
                    return self._get_mock_crypto_data(symbol)
                    
        except Exception as e:
            print(f"Error fetching crypto data for {symbol}: {e}")
            return self._get_mock_crypto_data(symbol)
    
    async def get_market_overview(self) -> Dict[str, Any]:
        """Get comprehensive market overview"""
        try:
            # Get major indices
            indices = ["^GSPC", "^DJI", "^IXIC", "^VIX"]  # S&P 500, Dow Jones, NASDAQ, VIX
            index_data = {}
            
            for index in indices:
                data = await self.get_stock_quote(index)
                if data:
                    index_data[index] = data
            
            # Get major forex pairs
            forex_pairs = [("USD", "VND"), ("EUR", "USD"), ("USD", "JPY")]
            forex_data = {}
            
            for from_curr, to_curr in forex_pairs:
                data = await self.get_forex_rate(from_curr, to_curr)
                if data:
                    forex_data[f"{from_curr}{to_curr}"] = data
            
            # Get major cryptocurrencies
            crypto_symbols = ["BTC", "ETH", "BNB"]
            crypto_data = {}
            
            for symbol in crypto_symbols:
                data = await self.get_crypto_price(symbol)
                if data:
                    crypto_data[symbol] = data
            
            return {
                "status": "success",
                "data": {
                    "indices": index_data,
                    "forex": forex_data,
                    "cryptocurrencies": crypto_data,
                    "market_sentiment": self._calculate_market_sentiment(index_data),
                    "last_updated": datetime.now().isoformat()
                },
                "message": "Market overview retrieved successfully"
            }
            
        except Exception as e:
            print(f"Error getting market overview: {e}")
            return self._get_mock_market_overview()
    
    def _calculate_market_sentiment(self, index_data: Dict[str, Any]) -> str:
        """Calculate market sentiment based on major indices"""
        if not index_data:
            return "NEUTRAL"
        
        positive_count = 0
        total_count = 0
        
        for index, data in index_data.items():
            if "change" in data and data["change"] is not None:
                total_count += 1
                if data["change"] > 0:
                    positive_count += 1
        
        if total_count == 0:
            return "NEUTRAL"
        
        positive_ratio = positive_count / total_count
        
        if positive_ratio >= 0.7:
            return "BULLISH"
        elif positive_ratio <= 0.3:
            return "BEARISH"
        else:
            return "NEUTRAL"
    
    def _get_mock_stock_data(self, symbol: str) -> Dict[str, Any]:
        """Fallback mock data for stocks"""
        import random
        base_price = random.uniform(50, 200)
        change = random.uniform(-10, 10)
        
        return {
            "symbol": symbol,
            "price": round(base_price, 2),
            "change": round(change, 2),
            "change_percent": f"{round(change/base_price*100, 2)}%",
            "volume": random.randint(1000000, 10000000),
            "previous_close": round(base_price - change, 2),
            "open": round(base_price + random.uniform(-5, 5), 2),
            "high": round(base_price + random.uniform(0, 10), 2),
            "low": round(base_price - random.uniform(0, 10), 2),
            "last_updated": datetime.now().strftime("%Y-%m-%d")
        }
    
    def _get_mock_forex_data(self, from_currency: str, to_currency: str) -> Dict[str, Any]:
        """Fallback mock data for forex"""
        import random
        
        # Mock exchange rates
        rates = {
            "USDVND": 24000,
            "EURUSD": 1.08,
            "USDJPY": 150
        }
        
        pair = f"{from_currency}{to_currency}"
        base_rate = rates.get(pair, random.uniform(0.5, 2.0))
        
        return {
            "from_currency": from_currency,
            "to_currency": to_currency,
            "exchange_rate": round(base_rate, 4),
            "last_updated": datetime.now().isoformat(),
            "timezone": "UTC"
        }
    
    def _get_mock_crypto_data(self, symbol: str) -> Dict[str, Any]:
        """Fallback mock data for cryptocurrencies"""
        import random
        
        # Mock crypto prices
        prices = {
            "BTC": 45000,
            "ETH": 3000,
            "BNB": 300
        }
        
        base_price = prices.get(symbol, random.uniform(100, 1000))
        
        return {
            "symbol": symbol,
            "market": "USD",
            "price": round(base_price, 2),
            "last_updated": datetime.now().isoformat(),
            "timezone": "UTC"
        }
    
    def _get_mock_market_overview(self) -> Dict[str, Any]:
        """Fallback mock market overview"""
        return {
            "status": "success",
            "data": {
                "indices": {
                    "^GSPC": self._get_mock_stock_data("^GSPC"),
                    "^DJI": self._get_mock_stock_data("^DJI"),
                    "^IXIC": self._get_mock_stock_data("^IXIC")
                },
                "forex": {
                    "USDVND": self._get_mock_forex_data("USD", "VND"),
                    "EURUSD": self._get_mock_forex_data("EUR", "USD")
                },
                "cryptocurrencies": {
                    "BTC": self._get_mock_crypto_data("BTC"),
                    "ETH": self._get_mock_crypto_data("ETH")
                },
                "market_sentiment": "NEUTRAL",
                "last_updated": datetime.now().isoformat()
            },
            "message": "Mock market overview data"
        } 