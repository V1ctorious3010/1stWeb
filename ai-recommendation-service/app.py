from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import httpx
import redis
import json
import os
from dotenv import load_dotenv

from services.ai_service import AIRecommendationService
from services.cache_service import CacheService
from models.recommendation import RecommendationRequest, RecommendationResponse, InvestmentRecommendation

load_dotenv()

app = FastAPI(
    title="AI Recommendation Service",
    description="AI-powered investment recommendations based on customer assets and risk profile",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
ai_service = AIRecommendationService()
cache_service = CacheService()

# Health check
@app.get("/health")
async def health_check():
    return {
        "status": "OK",
        "service": "AI Recommendation Service",
        "timestamp": "2024-01-01T00:00:00Z"
    }

# Get investment recommendations
@app.post("/recommendations", response_model=RecommendationResponse)
async def get_recommendations(request: RecommendationRequest):
    try:
        # Check cache first
        cache_key = f"recommendations:{request.customer_id}"
        cached_result = await cache_service.get(cache_key)
        
        if cached_result:
            return RecommendationResponse(**cached_result)
        
        # Get customer data
        customer_data = await get_customer_data(request.customer_id)
        if not customer_data:
            raise HTTPException(status_code=404, detail="Customer not found")
        
        # Get asset data
        asset_data = await get_asset_data(request.customer_id)
        
        # Get market data
        market_data = await get_market_data()
        
        # Generate recommendations using AI
        recommendations = await ai_service.generate_recommendations(
            customer_data=customer_data,
            asset_data=asset_data,
            market_data=market_data,
            investment_amount=request.investment_amount
        )
        
        # Create response
        response = RecommendationResponse(
            customer_id=request.customer_id,
            recommendations=recommendations,
            risk_profile=customer_data.get("riskProfile", "MEDIUM"),
            total_current_assets=sum(asset.get("currentValue", 0) for asset in asset_data),
            generated_at="2024-01-01T00:00:00Z"
        )
        
        # Cache the result
        await cache_service.set(cache_key, response.dict(), ttl=3600)  # 1 hour
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Get portfolio analysis
@app.get("/analysis/{customer_id}")
async def get_portfolio_analysis(customer_id: str):
    try:
        # Check cache
        cache_key = f"analysis:{customer_id}"
        cached_result = await cache_service.get(cache_key)
        
        if cached_result:
            return cached_result
        
        # Get data
        customer_data = await get_customer_data(customer_id)
        asset_data = await get_asset_data(customer_id)
        market_data = await get_market_data()
        
        # Analyze portfolio
        analysis = await ai_service.analyze_portfolio(
            customer_data=customer_data,
            asset_data=asset_data,
            market_data=market_data
        )
        
        # Cache result
        await cache_service.set(cache_key, analysis, ttl=1800)  # 30 minutes
        
        return analysis
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Get risk assessment
@app.get("/risk-assessment/{customer_id}")
async def get_risk_assessment(customer_id: str):
    try:
        # Check cache
        cache_key = f"risk:{customer_id}"
        cached_result = await cache_service.get(cache_key)
        
        if cached_result:
            return cached_result
        
        # Get data
        customer_data = await get_customer_data(customer_id)
        asset_data = await get_asset_data(customer_id)
        
        # Assess risk
        risk_assessment = await ai_service.assess_risk(
            customer_data=customer_data,
            asset_data=asset_data
        )
        
        # Cache result
        await cache_service.set(cache_key, risk_assessment, ttl=7200)  # 2 hours
        
        return risk_assessment
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Helper functions to fetch data from other services
async def get_customer_data(customer_id: str) -> Dict[str, Any]:
    """Fetch customer data from Customer Service"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{os.getenv('CUSTOMER_SERVICE_URL', 'http://customer-service:8001')}/api/customers/{customer_id}"
            )
            if response.status_code == 200:
                return response.json()
            return None
    except Exception as e:
        print(f"Error fetching customer data: {e}")
        return None

async def get_asset_data(customer_id: str) -> List[Dict[str, Any]]:
    """Fetch asset data from Asset Service"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{os.getenv('ASSET_SERVICE_URL', 'http://asset-service:8002')}/api/assets/customer/{customer_id}"
            )
            if response.status_code == 200:
                data = response.json()
                return data.get("assets", [])
            return []
    except Exception as e:
        print(f"Error fetching asset data: {e}")
        return []

async def get_market_data() -> Dict[str, Any]:
    """Fetch market data from Market Data Service"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{os.getenv('MARKET_DATA_SERVICE_URL', 'http://market-data-service:8003')}/api/market/current"
            )
            if response.status_code == 200:
                return response.json()
            return {}
    except Exception as e:
        print(f"Error fetching market data: {e}")
        return {}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004) 