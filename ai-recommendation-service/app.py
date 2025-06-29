from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import httpx
import redis
import json
import os
from dotenv import load_dotenv
from datetime import datetime

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

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    try:
        # Initialize investment products with market data
        await ai_service.initialize_products()
        print("AI Recommendation Service started successfully with Alpha Vantage integration")
    except Exception as e:
        print(f"Warning: Could not initialize products with market data: {e}")
        print("Service will initialize products on first request")

# Health check
@app.get("/health")
async def health_check():
    return {
        "status": "OK",
        "service": "AI Recommendation Service",
        "features": {
            "ml_models": ai_service.risk_model is not None and ai_service.return_model is not None,
            "market_data_integration": len(ai_service.investment_products) > 0 and any(
                product.get("market_data_integrated", False) for product in ai_service.investment_products
            ),
            "alpha_vantage_connected": ai_service.market_data_service is not None
        },
        "products_loaded": len(ai_service.investment_products),
        "timestamp": datetime.now().isoformat()
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
        ai_response = await ai_service.generate_recommendations(
            customer_data=customer_data,
            asset_data=asset_data,
            market_data=market_data,
            investment_amount=request.investment_amount
        )
        
        # Extract recommendations from AI response
        recommendations_data = ai_response["data"]["recommendations"]
        
        # Create response
        response = RecommendationResponse(
            customer_id=request.customer_id,
            recommendations=recommendations_data,
            risk_profile=customer_data.get("riskProfile", "MEDIUM"),
            total_current_assets=sum(asset.get("currentValue", 0) for asset in asset_data),
            generated_at=ai_response["data"]["generated_at"],
            portfolio_analysis=ai_response["data"].get("analysis_summary"),
            market_insights=ai_response["data"].get("market_context")
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
        analysis_response = await ai_service.analyze_portfolio(
            customer_data=customer_data,
            asset_data=asset_data,
            market_data=market_data
        )
        
        # Cache result
        await cache_service.set(cache_key, analysis_response, ttl=1800)  # 30 minutes
        
        return analysis_response
        
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
        risk_response = await ai_service.assess_risk(
            customer_data=customer_data,
            asset_data=asset_data
        )
        
        # Cache result
        await cache_service.set(cache_key, risk_response, ttl=7200)  # 2 hours
        
        return risk_response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Get market overview
@app.get("/market-overview")
async def get_market_overview():
    """Get real-time market overview from Alpha Vantage"""
    try:
        market_data = await ai_service.market_data_service.get_market_overview()
        return market_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Get investment products
@app.get("/products")
async def get_investment_products():
    """Get all available investment products"""
    try:
        # Initialize products if not already done
        if not ai_service.investment_products:
            await ai_service.initialize_products()
        
        products = ai_service.investment_products
        
        return {
            "status": "success",
            "data": {
                "products": products,
                "total_count": len(products),
                "asset_types": list(set(product["asset_type"] for product in products)),
                "risk_levels": list(set(product["risk_level"] for product in products)),
                "market_data_integrated": any(product.get("market_data_integrated", False) for product in products),
                "retrieved_at": datetime.now().isoformat()
            },
            "message": f"Retrieved {len(products)} investment products with Alpha Vantage integration"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Test ML predictions
@app.post("/test-ml")
async def test_ml_predictions(customer_data: Dict[str, Any]):
    """Test ML predictions with customer data"""
    try:
        # Get predictions
        predicted_risk = ai_service.predict_risk_score(customer_data)
        predicted_return = ai_service.predict_expected_return(customer_data)
        confidence = ai_service._calculate_model_confidence(customer_data)
        
        return {
            "status": "success",
            "data": {
                "predictions": {
                    "risk_score": predicted_risk,
                    "expected_return": predicted_return,
                    "model_confidence": confidence
                },
                "input_features": {
                    "age": customer_data.get("age"),
                    "income": customer_data.get("income"),
                    "currentAssets": customer_data.get("currentAssets"),
                    "investmentHorizon": customer_data.get("investmentHorizon"),
                    "riskTolerance": customer_data.get("riskTolerance")
                },
                "model_info": {
                    "risk_model_loaded": ai_service.risk_model is not None,
                    "return_model_loaded": ai_service.return_model is not None,
                    "scaler_loaded": ai_service.scaler is not None
                },
                "predicted_at": datetime.now().isoformat()
            },
            "message": "ML predictions completed successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Test product generation with market data
@app.get("/test-products")
async def test_product_generation():
    """Test investment product generation with Alpha Vantage market data"""
    try:
        # Force re-initialization of products
        ai_service.investment_products = []
        await ai_service.initialize_products()
        
        products = ai_service.investment_products
        
        # Analyze market data integration
        market_integrated_count = sum(1 for p in products if p.get("market_data_integrated", False))
        
        # Get market data for comparison
        market_data = await ai_service.market_data_service.get_market_overview()
        
        return {
            "status": "success",
            "data": {
                "total_products": len(products),
                "market_integrated_products": market_integrated_count,
                "integration_percentage": (market_integrated_count / len(products)) * 100 if products else 0,
                "market_sentiment": market_data["data"].get("market_sentiment", "UNKNOWN") if market_data else "UNKNOWN",
                "sample_products": products[:3] if products else [],
                "market_data_available": market_data is not None,
                "generated_at": datetime.now().isoformat()
            },
            "message": f"Generated {len(products)} products with {market_integrated_count} market-integrated"
        }
        
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
    """Fetch market data from Alpha Vantage API"""
    try:
        # Use Alpha Vantage service instead of mock market data service
        market_data = await ai_service.market_data_service.get_market_overview()
        return market_data.get("data", {})
    except Exception as e:
        print(f"Error fetching market data from Alpha Vantage: {e}")
        return {}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004) 