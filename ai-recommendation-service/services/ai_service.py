import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from typing import List, Dict, Any, Optional
import joblib
import os
from datetime import datetime, timedelta
import random

from .market_data_service import AlphaVantageService

class AIRecommendationService:
    def __init__(self):
        self.risk_model = None
        self.return_model = None
        self.scaler = StandardScaler()
        self.load_or_train_models()
        
        # Initialize market data service
        self.market_data_service = AlphaVantageService()
        
        # Initialize investment products as empty, will be loaded when needed
        self.investment_products = []
    
    def load_or_train_models(self):
        """Load pre-trained models or train new ones"""
        try:
            # Try to load existing models
            self.risk_model = joblib.load('models/risk_model.pkl')
            self.return_model = joblib.load('models/return_model.pkl')
            self.scaler = joblib.load('models/scaler.pkl')
            print("Loaded pre-trained models")
        except:
            # Train new models if not found
            print("Training new models...")
            self._train_models()
    
    def _train_models(self):
        """Train machine learning models with mock data"""
        # Generate mock training data
        np.random.seed(42)
        n_samples = 1000
        
        # Features: age, income, current_assets, investment_horizon, risk_tolerance
        age = np.random.normal(45, 15, n_samples)
        income = np.random.lognormal(10, 0.5, n_samples)
        current_assets = np.random.lognormal(12, 0.8, n_samples)
        investment_horizon = np.random.choice([1, 3, 5, 10, 20], n_samples)
        risk_tolerance = np.random.choice([1, 2, 3, 4, 5], n_samples)
        
        # Create feature matrix
        X = np.column_stack([age, income, current_assets, investment_horizon, risk_tolerance])
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Generate target variables
        # Risk score (1-10)
        risk_scores = np.clip(
            (age * 0.1 + income * 0.2 + current_assets * 0.3 + 
             investment_horizon * 0.2 + risk_tolerance * 0.2 + 
             np.random.normal(0, 1, n_samples)), 1, 10
        )
        
        # Expected return (%)
        expected_returns = np.clip(
            (risk_tolerance * 2 + investment_horizon * 0.5 + 
             np.random.normal(5, 3, n_samples)), 0, 20
        )
        
        # Train models
        self.risk_model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.return_model = RandomForestRegressor(n_estimators=100, random_state=42)
        
        self.risk_model.fit(X_scaled, risk_scores)
        self.return_model.fit(X_scaled, expected_returns)
        
        # Save models
        os.makedirs('models', exist_ok=True)
        joblib.dump(self.risk_model, 'models/risk_model.pkl')
        joblib.dump(self.return_model, 'models/return_model.pkl')
        joblib.dump(self.scaler, 'models/scaler.pkl')
        
        print("Models trained and saved")
    
    def predict_risk_score(self, customer_data: Dict[str, Any], market_data: Optional[Dict[str, Any]] = None) -> float:
        """Predict risk score using trained RandomForest model with market data integration"""
        if not self.risk_model:
            return customer_data.get("riskScore", 5.0)
        
        try:
            # Extract customer features
            age = customer_data.get("age", 45)
            income = customer_data.get("income", 50000000)
            current_assets = customer_data.get("currentAssets", 100000000)
            investment_horizon = customer_data.get("investmentHorizon", 5)
            risk_tolerance = customer_data.get("riskTolerance", 3)
            
            # Extract market features if available
            market_volatility = 0.15  # Default volatility
            market_sentiment_score = 0.5  # Neutral sentiment
            vix_level = 20  # Default VIX level
            
            if market_data and "data" in market_data:
                market_info = market_data["data"]
                
                # Get VIX level for market volatility
                if "indices" in market_info and "^VIX" in market_info["indices"]:
                    vix_data = market_info["indices"]["^VIX"]
                    vix_level = vix_data.get("price", 20)
                    market_volatility = min(0.5, vix_level / 100)  # Normalize VIX to 0-0.5
                
                # Get market sentiment score
                sentiment = market_info.get("market_sentiment", "NEUTRAL")
                sentiment_mapping = {"BULLISH": 0.8, "NEUTRAL": 0.5, "BEARISH": 0.2}
                market_sentiment_score = sentiment_mapping.get(sentiment, 0.5)
            
            # Create enhanced feature vector with market data
            features = np.array([[
                age, income, current_assets, investment_horizon, risk_tolerance,
                market_volatility, market_sentiment_score, vix_level
            ]])
            
            # Scale features (assuming scaler was trained with 8 features)
            try:
                features_scaled = self.scaler.transform(features)
            except ValueError:
                # If scaler was trained with 5 features, use only customer features
                features_scaled = self.scaler.transform(features[:, :5])
            
            # Predict risk score
            predicted_risk = self.risk_model.predict(features_scaled)[0]
            
            # Adjust prediction based on market conditions
            if market_data and "data" in market_data:
                market_info = market_data["data"]
                sentiment = market_info.get("market_sentiment", "NEUTRAL")
                
                # Market-based adjustments
                if sentiment == "BEARISH":
                    predicted_risk = min(10, predicted_risk + 1)  # Increase risk in bear market
                elif sentiment == "BULLISH":
                    predicted_risk = max(1, predicted_risk - 0.5)  # Slightly decrease risk in bull market
            
            return round(max(1, min(10, predicted_risk)), 2)
            
        except Exception as e:
            print(f"Error predicting risk score: {e}")
            return customer_data.get("riskScore", 5.0)
    
    def predict_expected_return(self, customer_data: Dict[str, Any], market_data: Optional[Dict[str, Any]] = None) -> float:
        """Predict expected return using trained RandomForest model with market data integration"""
        if not self.return_model:
            return 8.0  # Default return
        
        try:
            # Extract customer features
            age = customer_data.get("age", 45)
            income = customer_data.get("income", 50000000)
            current_assets = customer_data.get("currentAssets", 100000000)
            investment_horizon = customer_data.get("investmentHorizon", 5)
            risk_tolerance = customer_data.get("riskTolerance", 3)
            
            # Extract market features if available
            market_volatility = 0.15  # Default volatility
            market_sentiment_score = 0.5  # Neutral sentiment
            sp500_return = 0.08  # Default S&P 500 return
            
            if market_data and "data" in market_data:
                market_info = market_data["data"]
                
                # Get S&P 500 performance
                if "indices" in market_info and "^GSPC" in market_info["indices"]:
                    sp500_data = market_info["indices"]["^GSPC"]
                    if "change_percent" in sp500_data:
                        change_str = sp500_data["change_percent"].replace("%", "")
                        try:
                            sp500_return = float(change_str) / 100
                        except:
                            sp500_return = 0.08
                
                # Get market sentiment score
                sentiment = market_info.get("market_sentiment", "NEUTRAL")
                sentiment_mapping = {"BULLISH": 0.8, "NEUTRAL": 0.5, "BEARISH": 0.2}
                market_sentiment_score = sentiment_mapping.get(sentiment, 0.5)
                
                # Calculate market volatility from multiple indices
                volatility_indicators = []
                for index_key in ["^GSPC", "^DJI", "^IXIC"]:
                    if index_key in market_info.get("indices", {}):
                        index_data = market_info["indices"][index_key]
                        if "change_percent" in index_data:
                            change_str = index_data["change_percent"].replace("%", "")
                            try:
                                volatility_indicators.append(abs(float(change_str)))
                            except:
                                pass
                
                if volatility_indicators:
                    market_volatility = min(0.5, np.mean(volatility_indicators) / 100)
            
            # Create enhanced feature vector with market data
            features = np.array([[
                age, income, current_assets, investment_horizon, risk_tolerance,
                market_volatility, market_sentiment_score, sp500_return
            ]])
            
            # Scale features
            try:
                features_scaled = self.scaler.transform(features)
            except ValueError:
                # If scaler was trained with 5 features, use only customer features
                features_scaled = self.scaler.transform(features[:, :5])
            
            # Predict expected return
            predicted_return = self.return_model.predict(features_scaled)[0]
            
            # Adjust prediction based on market conditions
            if market_data and "data" in market_data:
                market_info = market_data["data"]
                sentiment = market_info.get("market_sentiment", "NEUTRAL")
                
                # Market-based adjustments
                if sentiment == "BULLISH":
                    predicted_return = min(25, predicted_return + 2)  # Increase return in bull market
                elif sentiment == "BEARISH":
                    predicted_return = max(0, predicted_return - 1)  # Decrease return in bear market
                
                # Adjust based on S&P 500 performance
                predicted_return = predicted_return * (1 + sp500_return * 0.3)
            
            return round(max(0, min(25, predicted_return)), 2)
            
        except Exception as e:
            print(f"Error predicting expected return: {e}")
            return 8.0
    
    async def _load_investment_products(self) -> List[Dict[str, Any]]:
        """Load dynamic investment products database with Alpha Vantage integration"""
        import random
        
        # Get real market data from Alpha Vantage
        try:
            market_data = await self.market_data_service.get_market_overview()
            has_market_data = market_data and "data" in market_data
        except:
            has_market_data = False
            market_data = None
        
        # Base product templates with market-aware adjustments
        product_templates = [
            {
                "asset_type": "SAVINGS",
                "base_return": 6.0,
                "risk_level": "LOW",
                "min_horizon": 1,
                "max_horizon": 12,
                "min_investment": 1000000,
                "description_template": "Sản phẩm tiết kiệm {period} với lãi suất {rate}%",
                "advantages": ["An toàn", "Lãi suất ổn định", "Thanh khoản tốt"],
                "disadvantages": ["Lợi nhuận thấp", "Không bảo vệ lạm phát"],
                "institutions": ["Ngân hàng TMCP", "Vietcombank", "BIDV", "Agribank"],
                "market_adjustment": self._get_savings_market_adjustment(market_data) if has_market_data else 0
            },
            {
                "asset_type": "FUND",
                "base_return": 12.0,
                "risk_level": "MEDIUM",
                "min_horizon": 3,
                "max_horizon": 10,
                "min_investment": 500000,
                "description_template": "Quỹ đầu tư {type} với danh mục đa dạng",
                "advantages": ["Đa dạng hóa", "Quản lý chuyên nghiệp", "Lợi nhuận tiềm năng cao"],
                "disadvantages": ["Rủi ro thị trường", "Phí quản lý"],
                "institutions": ["VFM", "SSI", "Dragon Capital", "Mirae Asset"],
                "fund_types": ["cổ phiếu", "trái phiếu", "cân bằng", "tăng trưởng"],
                "market_adjustment": self._get_fund_market_adjustment(market_data) if has_market_data else 0
            },
            {
                "asset_type": "BOND",
                "base_return": 8.5,
                "risk_level": "LOW",
                "min_horizon": 3,
                "max_horizon": 10,
                "min_investment": 100000,
                "description_template": "Trái phiếu {issuer} kỳ hạn {term} năm",
                "advantages": ["An toàn", "Lãi suất ổn định", "Được bảo lãnh"],
                "disadvantages": ["Kỳ hạn dài", "Thanh khoản hạn chế"],
                "institutions": ["Bộ Tài chính", "TPBank", "VietinBank", "Sacombank"],
                "issuers": ["Chính phủ", "Doanh nghiệp", "Ngân hàng", "Tổ chức tài chính"],
                "market_adjustment": self._get_bond_market_adjustment(market_data) if has_market_data else 0
            },
            {
                "asset_type": "STOCK",
                "base_return": 15.0,
                "risk_level": "HIGH",
                "min_horizon": 5,
                "max_horizon": 20,
                "min_investment": 1000000,
                "description_template": "Cổ phiếu {company} - {sector}",
                "advantages": ["Tiềm năng tăng trưởng cao", "Cổ tức ổn định"],
                "disadvantages": ["Rủi ro cao", "Biến động giá lớn"],
                "institutions": ["Vinamilk", "FPT", "Vingroup", "Bamboo Airways"],
                "companies": ["VNM", "FPT", "VIC", "HVN", "TCB", "VCB", "HPG", "MSN"],
                "sectors": ["Thực phẩm", "Công nghệ", "Bất động sản", "Hàng không", "Ngân hàng", "Thép"],
                "market_adjustment": self._get_stock_market_adjustment(market_data) if has_market_data else 0
            },
            {
                "asset_type": "GOLD",
                "base_return": 6.0,
                "risk_level": "MEDIUM",
                "min_horizon": 3,
                "max_horizon": 10,
                "min_investment": 500000,
                "description_template": "Đầu tư vàng {type}",
                "advantages": ["Bảo vệ lạm phát", "Tài sản thực"],
                "disadvantages": ["Không sinh lời", "Chi phí lưu trữ"],
                "institutions": ["SJC", "PNJ", "DOJI", "Phú Quý"],
                "gold_types": ["SJC", "PNJ", "DOJI", "vật chất", "ETF"],
                "market_adjustment": self._get_gold_market_adjustment(market_data) if has_market_data else 0
            }
        ]
        
        products = []
        random.seed(datetime.now().timestamp())  # Use current time as seed
        
        for template in product_templates:
            # Generate multiple products for each template
            num_products = random.randint(2, 4)
            
            for i in range(num_products):
                # Generate dynamic values with market adjustment
                return_variation = random.uniform(-2.0, 2.0)
                market_adjustment = template.get("market_adjustment", 0)
                expected_return = max(0, template["base_return"] + return_variation + market_adjustment)
                
                investment_horizon = random.randint(template["min_horizon"], template["max_horizon"])
                if investment_horizon == 1:
                    horizon_text = "1 năm"
                else:
                    horizon_text = f"{investment_horizon} năm"
                
                min_investment = template["min_investment"] * random.uniform(0.8, 1.5)
                
                # Generate product name and description
                if template["asset_type"] == "SAVINGS":
                    period = f"{investment_horizon} tháng" if investment_horizon < 12 else f"{investment_horizon//12} năm"
                    product_name = f"Tiết kiệm có kỳ hạn {period}"
                    description = template["description_template"].format(
                        period=period, 
                        rate=f"{expected_return:.1f}"
                    )
                    product_code = f"TK{investment_horizon}M"
                    
                elif template["asset_type"] == "FUND":
                    fund_type = random.choice(template["fund_types"])
                    product_name = f"Quỹ mở {random.choice(template['institutions'])} - {fund_type.title()}"
                    description = template["description_template"].format(type=fund_type)
                    product_code = f"FUND{random.randint(1000, 9999)}"
                    
                elif template["asset_type"] == "BOND":
                    issuer = random.choice(template["issuers"])
                    product_name = f"Trái phiếu {issuer} {investment_horizon} năm"
                    description = template["description_template"].format(
                        issuer=issuer, 
                        term=investment_horizon
                    )
                    product_code = f"TP{issuer[:2].upper()}{investment_horizon}Y"
                    
                elif template["asset_type"] == "STOCK":
                    company = random.choice(template["companies"])
                    sector = random.choice(template["sectors"])
                    product_name = f"Cổ phiếu {company}"
                    description = template["description_template"].format(
                        company=company, 
                        sector=sector
                    )
                    product_code = company
                    
                elif template["asset_type"] == "GOLD":
                    gold_type = random.choice(template["gold_types"])
                    product_name = f"Vàng {gold_type}"
                    description = template["description_template"].format(type=gold_type)
                    product_code = f"GOLD{gold_type[:3].upper()}"
                
                # Add some randomness to advantages/disadvantages
                advantages = template["advantages"].copy()
                disadvantages = template["disadvantages"].copy()
                
                # Add market-based advantages/disadvantages
                if has_market_data:
                    market_advantages = self._get_market_based_advantages(template["asset_type"], market_data)
                    market_disadvantages = self._get_market_based_disadvantages(template["asset_type"], market_data)
                    advantages.extend(market_advantages)
                    disadvantages.extend(market_disadvantages)
                
                # Randomly add or remove some items
                if random.random() > 0.7:
                    advantages.append("Phù hợp với người mới bắt đầu")
                if random.random() > 0.7:
                    disadvantages.append("Cần kiến thức chuyên môn")
                
                product = {
                    "product_name": product_name,
                    "asset_type": template["asset_type"],
                    "expected_return": round(expected_return, 1),
                    "risk_level": template["risk_level"],
                    "investment_horizon": horizon_text,
                    "min_investment": round(min_investment),
                    "max_investment": None,
                    "description": description,
                    "advantages": advantages,
                    "disadvantages": disadvantages,
                    "institution": random.choice(template["institutions"]),
                    "product_code": product_code,
                    "last_updated": datetime.now().isoformat(),
                    "market_data_integrated": has_market_data
                }
                
                products.append(product)
        
        return products
    
    async def generate_recommendations(
        self,
        customer_data: Dict[str, Any],
        asset_data: List[Dict[str, Any]],
        market_data: Dict[str, Any],
        investment_amount: Optional[float] = None
    ) -> Dict[str, Any]:
        """Generate investment recommendations based on customer profile and current assets"""
        
        # Initialize products if not already done
        if not self.investment_products:
            await self.initialize_products()
        
        # Get real market data from Alpha Vantage
        real_market_data = await self.market_data_service.get_market_overview()
        
        # Use RandomForest to predict risk score and expected return with market data
        predicted_risk_score = self.predict_risk_score(customer_data, real_market_data)
        predicted_expected_return = self.predict_expected_return(customer_data, real_market_data)
        
        # Analyze customer profile
        risk_profile = customer_data.get("riskProfile", "MEDIUM")
        risk_score = customer_data.get("riskScore", predicted_risk_score)
        current_assets_value = sum(asset.get("currentValue", 0) for asset in asset_data)
        
        # Filter products based on risk profile and market conditions
        suitable_products = []
        for product in self.investment_products:
            if self._is_product_suitable(product, risk_profile, risk_score):
                # Additional market-based filtering
                if self._is_product_suitable_for_market_conditions(product, real_market_data):
                    suitable_products.append(product)
        
        # Score and rank products with real market data and ML insights
        scored_products = []
        for product in suitable_products:
            score = self._calculate_product_score_with_market_data(
                product, customer_data, asset_data, real_market_data, investment_amount
            )
            
            # Add ML-based scoring adjustments
            ml_adjustment = self._calculate_ml_based_adjustment(
                product, predicted_risk_score, predicted_expected_return, real_market_data
            )
            score += ml_adjustment
            
            scored_products.append((product, score))
        
        # Sort by score and return top recommendations
        scored_products.sort(key=lambda x: x[1], reverse=True)
        
        recommendations = []
        for product, score in scored_products[:5]:  # Top 5 recommendations
            recommendation = product.copy()
            recommendation["confidence_score"] = min(score / 100, 1.0)
            
            # Adjust recommendation based on investment amount
            if investment_amount:
                if investment_amount < product["min_investment"]:
                    recommendation["min_investment"] = investment_amount
                if product.get("max_investment"):
                    recommendation["max_investment"] = min(
                        product["max_investment"], investment_amount
                    )
            
            # Add enhanced market context to recommendation
            recommendation["market_context"] = self._get_enhanced_market_context_for_product(
                product, real_market_data, predicted_risk_score, predicted_expected_return
            )
            
            recommendations.append(recommendation)
        
        # Return structured JSON response with real market data and ML predictions
        return {
            "status": "success",
            "data": {
                "recommendations": recommendations,
                "customer_profile": {
                    "risk_profile": risk_profile,
                    "risk_score": risk_score,
                    "predicted_risk_score": predicted_risk_score,
                    "predicted_expected_return": predicted_expected_return,
                    "current_assets_value": current_assets_value,
                    "total_assets_count": len(asset_data)
                },
                "market_overview": real_market_data["data"],
                "analysis_summary": {
                    "total_recommendations": len(recommendations),
                    "average_expected_return": sum(r["expected_return"] for r in recommendations) / len(recommendations) if recommendations else 0,
                    "risk_distribution": self._get_risk_distribution(recommendations),
                    "market_sentiment": real_market_data["data"]["market_sentiment"],
                    "ml_predictions": {
                        "risk_score": predicted_risk_score,
                        "expected_return": predicted_expected_return,
                        "model_confidence": self._calculate_model_confidence(customer_data),
                        "market_integration": True
                    }
                },
                "generated_at": datetime.now().isoformat()
            },
            "message": f"Generated {len(recommendations)} recommendations using ML predictions and real market data from Alpha Vantage"
        }
    
    def _is_product_suitable(self, product: Dict[str, Any], risk_profile: str, risk_score: float) -> bool:
        """Check if a product is suitable for the customer's risk profile"""
        risk_mapping = {
            "LOW": ["LOW"],
            "MEDIUM": ["LOW", "MEDIUM"],
            "HIGH": ["LOW", "MEDIUM", "HIGH"]
        }
        
        return product["risk_level"] in risk_mapping.get(risk_profile, ["MEDIUM"])
    
    def _calculate_product_score_with_market_data(
        self,
        product: Dict[str, Any],
        customer_data: Dict[str, Any],
        asset_data: List[Dict[str, Any]],
        market_data: Dict[str, Any],
        investment_amount: Optional[float]
    ) -> float:
        """Calculate a score for a product based on various factors with real market data"""
        score = 0
        
        # Base score from expected return
        score += product["expected_return"] * 2
        
        # Risk alignment bonus
        risk_profile = customer_data.get("riskProfile", "MEDIUM")
        if product["risk_level"] == risk_profile:
            score += 20
        elif (risk_profile == "HIGH" and product["risk_level"] == "MEDIUM") or \
             (risk_profile == "LOW" and product["risk_level"] == "MEDIUM"):
            score += 10
        
        # Diversification bonus
        current_asset_types = set(asset.get("assetType") for asset in asset_data)
        if product["asset_type"] not in current_asset_types:
            score += 15
        
        # Real market condition adjustment
        if market_data and "data" in market_data:
            market_info = market_data["data"]
            market_sentiment = market_info.get("market_sentiment", "NEUTRAL")
            
            # Adjust score based on market sentiment and product type
            if product["asset_type"] == "STOCK":
                if market_sentiment == "BULLISH":
                    score += 15
                elif market_sentiment == "BEARISH":
                    score -= 10
                    
            elif product["asset_type"] == "BOND":
                if market_sentiment == "BEARISH":
                    score += 10  # Bonds are safer in bear markets
                elif market_sentiment == "BULLISH":
                    score -= 5
                    
            elif product["asset_type"] == "GOLD":
                if market_sentiment == "BEARISH":
                    score += 10  # Gold is a safe haven
                    
            elif product["asset_type"] == "SAVINGS":
                # Savings are always good for stability
                score += 5
        
        # Investment amount compatibility
        if investment_amount:
            if product["min_investment"] <= investment_amount:
                score += 10
            else:
                score -= 20  # Penalty if minimum not met
        
        return score
    
    async def analyze_portfolio(
        self,
        customer_data: Dict[str, Any],
        asset_data: List[Dict[str, Any]],
        market_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze customer's current portfolio"""
        
        if not asset_data:
            return {
                "status": "success",
                "data": {
                    "portfolio_summary": {
                        "total_value": 0,
                        "asset_count": 0,
                        "has_portfolio": False
                    },
                    "asset_allocation": {},
                    "risk_analysis": {
                        "risk_score": 5,
                        "risk_level": "MEDIUM",
                        "diversification_score": 0,
                        "performance_score": 0
                    },
                    "recommendations": ["Bắt đầu xây dựng danh mục đầu tư"],
                    "market_context": market_data or {},
                    "analyzed_at": datetime.now().isoformat()
                },
                "message": "Portfolio analysis completed for new customer"
            }
        
        # Calculate total value
        total_value = sum(asset.get("currentValue", 0) for asset in asset_data)
        
        # Calculate asset allocation
        asset_allocation = {}
        for asset in asset_data:
            asset_type = asset.get("assetType", "OTHER")
            value = asset.get("currentValue", 0)
            asset_allocation[asset_type] = asset_allocation.get(asset_type, 0) + value
        
        # Convert to percentages
        if total_value > 0:
            asset_allocation = {k: (v / total_value) * 100 for k, v in asset_allocation.items()}
        
        # Calculate risk score
        risk_score = self._calculate_portfolio_risk_score(asset_data, customer_data)
        
        # Calculate diversification score
        diversification_score = self._calculate_diversification_score(asset_allocation)
        
        # Calculate performance score
        performance_score = self._calculate_performance_score(asset_data)
        
        # Generate recommendations
        recommendations = self._generate_portfolio_recommendations(
            asset_allocation, risk_score, diversification_score, customer_data
        )
        
        # Determine risk level
        if risk_score <= 3:
            risk_level = "LOW"
        elif risk_score <= 7:
            risk_level = "MEDIUM"
        else:
            risk_level = "HIGH"
        
        # Calculate performance metrics
        performance_metrics = self._calculate_performance_metrics(asset_data)
        
        return {
            "status": "success",
            "data": {
                "portfolio_summary": {
                    "total_value": total_value,
                    "asset_count": len(asset_data),
                    "has_portfolio": True,
                    "largest_asset": max(asset_data, key=lambda x: x.get("currentValue", 0)) if asset_data else None
                },
                "asset_allocation": asset_allocation,
                "risk_analysis": {
                    "risk_score": risk_score,
                    "risk_level": risk_level,
                    "diversification_score": diversification_score,
                    "performance_score": performance_score,
                    "risk_factors": self._identify_risk_factors(asset_allocation, customer_data)
                },
                "performance_metrics": performance_metrics,
                "recommendations": recommendations,
                "market_context": market_data or {},
                "analyzed_at": datetime.now().isoformat()
            },
            "message": f"Portfolio analysis completed for {len(asset_data)} assets"
        }
    
    def _calculate_portfolio_risk_score(self, asset_data: List[Dict[str, Any]], customer_data: Dict[str, Any]) -> float:
        """Calculate overall portfolio risk score"""
        if not asset_data:
            return 5.0
        
        # Weighted average risk score based on asset values
        total_value = sum(asset.get("currentValue", 0) for asset in asset_data)
        if total_value == 0:
            return 5.0
        
        risk_weights = {"LOW": 3, "MEDIUM": 6, "HIGH": 9}
        weighted_risk = 0
        
        for asset in asset_data:
            value = asset.get("currentValue", 0)
            risk_level = asset.get("riskLevel", "MEDIUM")
            weighted_risk += (value / total_value) * risk_weights.get(risk_level, 6)
        
        return round(weighted_risk, 2)
    
    def _calculate_diversification_score(self, asset_allocation: Dict[str, float]) -> float:
        """Calculate portfolio diversification score"""
        if not asset_allocation:
            return 0.0
        
        # More asset types = higher diversification
        num_asset_types = len(asset_allocation)
        max_score = min(num_asset_types / 5, 1.0)  # Cap at 5 asset types
        
        # Penalty for over-concentration
        concentration_penalty = 0
        for percentage in asset_allocation.values():
            if percentage > 50:  # Over 50% in one asset type
                concentration_penalty += (percentage - 50) / 100
        
        return max(0, max_score - concentration_penalty)
    
    def _calculate_performance_score(self, asset_data: List[Dict[str, Any]]) -> float:
        """Calculate portfolio performance score"""
        if not asset_data:
            return 0.0
        
        total_profit_loss = 0
        total_initial_value = 0
        
        for asset in asset_data:
            current_value = asset.get("currentValue", 0)
            initial_value = asset.get("initialValue", 0)
            
            if initial_value > 0:
                total_profit_loss += (current_value - initial_value)
                total_initial_value += initial_value
        
        if total_initial_value == 0:
            return 0.5  # Neutral score
        
        # Calculate return percentage
        return_percentage = (total_profit_loss / total_initial_value) * 100
        
        # Convert to 0-1 score
        if return_percentage >= 10:
            return 1.0
        elif return_percentage >= 5:
            return 0.8
        elif return_percentage >= 0:
            return 0.6
        elif return_percentage >= -5:
            return 0.4
        else:
            return 0.2
    
    def _generate_portfolio_recommendations(
        self,
        asset_allocation: Dict[str, float],
        risk_score: float,
        diversification_score: float,
        customer_data: Dict[str, Any]
    ) -> List[str]:
        """Generate portfolio improvement recommendations"""
        recommendations = []
        
        # Diversification recommendations
        if diversification_score < 0.5:
            recommendations.append("Tăng cường đa dạng hóa danh mục đầu tư")
        
        # Risk management recommendations
        risk_profile = customer_data.get("riskProfile", "MEDIUM")
        if risk_profile == "LOW" and risk_score > 6:
            recommendations.append("Giảm thiểu rủi ro bằng cách chuyển sang tài sản an toàn hơn")
        elif risk_profile == "HIGH" and risk_score < 4:
            recommendations.append("Có thể tăng rủi ro để đạt lợi nhuận cao hơn")
        
        # Asset allocation recommendations
        if asset_allocation.get("SAVINGS", 0) > 80:
            recommendations.append("Cân nhắc đầu tư vào các sản phẩm có lợi nhuận cao hơn")
        
        if asset_allocation.get("STOCK", 0) > 60:
            recommendations.append("Cân nhắc giảm tỷ trọng cổ phiếu để giảm rủi ro")
        
        if not recommendations:
            recommendations.append("Danh mục đầu tư hiện tại khá cân bằng")
        
        return recommendations
    
    async def assess_risk(
        self,
        customer_data: Dict[str, Any],
        asset_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Assess overall risk profile of the customer using ML predictions with market data"""
        
        # Get real market data from Alpha Vantage
        real_market_data = await self.market_data_service.get_market_overview()
        
        # Use RandomForest to predict risk score and expected return with market data
        predicted_risk_score = self.predict_risk_score(customer_data, real_market_data)
        predicted_expected_return = self.predict_expected_return(customer_data, real_market_data)
        
        # Calculate overall risk level
        portfolio_risk_score = self._calculate_portfolio_risk_score(asset_data, customer_data)
        customer_risk_score = customer_data.get("riskScore", predicted_risk_score)
        
        # Combine customer and portfolio risk with ML prediction
        overall_risk_score = (portfolio_risk_score + customer_risk_score + predicted_risk_score) / 3
        
        # Determine risk level
        if overall_risk_score <= 3:
            overall_risk_level = "LOW"
        elif overall_risk_score <= 7:
            overall_risk_level = "MEDIUM"
        else:
            overall_risk_level = "HIGH"
        
        # Identify risk factors
        risk_factors = []
        
        # Concentration risk
        total_value = sum(asset.get("currentValue", 0) for asset in asset_data)
        if total_value > 0:
            for asset in asset_data:
                percentage = (asset.get("currentValue", 0) / total_value) * 100
                if percentage > 30:
                    risk_factors.append({
                        "type": "concentration",
                        "asset": asset.get("assetName", "Unknown"),
                        "percentage": round(percentage, 2),
                        "severity": "HIGH" if percentage > 50 else "MEDIUM",
                        "description": f"Tài sản {asset.get('assetName')} chiếm {round(percentage, 2)}% danh mục"
                    })
        
        # High-risk assets for low-risk customers
        risk_profile = customer_data.get("riskProfile", "MEDIUM")
        if risk_profile == "LOW":
            high_risk_assets = [asset for asset in asset_data if asset.get("riskLevel") == "HIGH"]
            if high_risk_assets:
                risk_factors.append({
                    "type": "risk_mismatch",
                    "severity": "MEDIUM",
                    "description": "Khách hàng có hồ sơ rủi ro thấp nhưng sở hữu tài sản rủi ro cao",
                    "affected_assets": [asset.get("assetName") for asset in high_risk_assets]
                })
        
        # ML-based risk insights with market context
        ml_risk_insights = []
        if predicted_risk_score > 7:
            ml_risk_insights.append("Mô hình ML dự đoán mức rủi ro cao dựa trên hồ sơ khách hàng")
        elif predicted_risk_score < 3:
            ml_risk_insights.append("Mô hình ML dự đoán mức rủi ro thấp, phù hợp với tài sản an toàn")
        
        if predicted_expected_return > 15:
            ml_risk_insights.append("Mô hình ML dự đoán lợi nhuận cao, cần cân nhắc rủi ro tương ứng")
        
        # Market-based risk insights
        if real_market_data and "data" in real_market_data:
            market_info = real_market_data["data"]
            sentiment = market_info.get("market_sentiment", "NEUTRAL")
            
            if sentiment == "BEARISH":
                ml_risk_insights.append("Thị trường đang trong xu hướng giảm, cần thận trọng với tài sản rủi ro")
            elif sentiment == "BULLISH":
                ml_risk_insights.append("Thị trường đang tăng trưởng, có thể cân nhắc tăng tỷ trọng tài sản tăng trưởng")
            
            # VIX-based insights
            if "indices" in market_info and "^VIX" in market_info["indices"]:
                vix_level = market_info["indices"]["^VIX"].get("price", 20)
                if vix_level > 30:
                    ml_risk_insights.append(f"Chỉ số VIX cao ({vix_level}), thị trường biến động mạnh")
                elif vix_level < 15:
                    ml_risk_insights.append(f"Chỉ số VIX thấp ({vix_level}), thị trường ổn định")
        
        # Generate risk mitigation strategies
        risk_mitigation = []
        if overall_risk_level == "HIGH":
            risk_mitigation.extend([
                "Tăng tỷ trọng tài sản an toàn (tiết kiệm, trái phiếu)",
                "Đa dạng hóa danh mục đầu tư",
                "Thiết lập stop-loss cho các khoản đầu tư rủi ro"
            ])
        elif overall_risk_level == "MEDIUM":
            risk_mitigation.extend([
                "Duy trì cân bằng giữa tài sản an toàn và tài sản tăng trưởng",
                "Theo dõi định kỳ hiệu suất danh mục"
            ])
        else:
            risk_mitigation.extend([
                "Có thể cân nhắc tăng tỷ trọng tài sản tăng trưởng để đạt lợi nhuận cao hơn"
            ])
        
        # Stress test results (dynamic based on portfolio)
        stress_test_results = self._calculate_stress_test_results(asset_data, total_value)
        
        # Calculate risk metrics with ML insights
        risk_metrics = {
            "portfolio_risk_score": portfolio_risk_score,
            "customer_risk_score": customer_risk_score,
            "ml_predicted_risk_score": predicted_risk_score,
            "overall_risk_score": overall_risk_score,
            "risk_tolerance_gap": abs(portfolio_risk_score - customer_risk_score),
            "concentration_risk": self._calculate_concentration_risk(asset_data),
            "volatility_estimate": self._estimate_portfolio_volatility(asset_data),
            "ml_confidence": self._calculate_model_confidence(customer_data),
            "market_integration": True
        }
        
        return {
            "status": "success",
            "data": {
                "risk_assessment": {
                    "overall_risk_level": overall_risk_level,
                    "risk_score": round(overall_risk_score, 2),
                    "risk_metrics": risk_metrics
                },
                "ml_insights": {
                    "predicted_risk_score": predicted_risk_score,
                    "predicted_expected_return": predicted_expected_return,
                    "risk_insights": ml_risk_insights,
                    "model_confidence": self._calculate_model_confidence(customer_data),
                    "market_integration": True
                },
                "market_context": real_market_data["data"] if real_market_data else {},
                "risk_factors": risk_factors,
                "risk_mitigation": risk_mitigation,
                "stress_test_results": stress_test_results,
                "portfolio_summary": {
                    "total_assets": len(asset_data),
                    "total_value": total_value,
                    "average_asset_value": total_value / len(asset_data) if asset_data else 0
                },
                "assessed_at": datetime.now().isoformat()
            },
            "message": f"Risk assessment completed using ML predictions and Alpha Vantage market data. Overall risk level: {overall_risk_level}"
        }

    def _get_risk_distribution(self, recommendations: List[Dict[str, Any]]) -> Dict[str, int]:
        """Get distribution of risk levels in recommendations"""
        distribution = {"LOW": 0, "MEDIUM": 0, "HIGH": 0}
        for rec in recommendations:
            risk_level = rec.get("risk_level", "MEDIUM")
            distribution[risk_level] = distribution.get(risk_level, 0) + 1
        return distribution

    def _calculate_performance_metrics(self, asset_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate detailed performance metrics"""
        if not asset_data:
            return {
                "total_return": 0,
                "total_return_percentage": 0,
                "best_performing_asset": None,
                "worst_performing_asset": None,
                "profit_loss_distribution": {"profit": 0, "loss": 0, "neutral": 0}
            }
        
        total_profit_loss = 0
        total_initial_value = 0
        asset_performance = []
        
        for asset in asset_data:
            current_value = asset.get("currentValue", 0)
            initial_value = asset.get("initialValue", 0)
            
            if initial_value > 0:
                profit_loss = current_value - initial_value
                return_percentage = (profit_loss / initial_value) * 100
                
                total_profit_loss += profit_loss
                total_initial_value += initial_value
                
                asset_performance.append({
                    "asset_name": asset.get("assetName", "Unknown"),
                    "profit_loss": profit_loss,
                    "return_percentage": return_percentage,
                    "current_value": current_value,
                    "initial_value": initial_value
                })
        
        # Find best and worst performing assets
        if asset_performance:
            best_asset = max(asset_performance, key=lambda x: x["return_percentage"])
            worst_asset = min(asset_performance, key=lambda x: x["return_percentage"])
        else:
            best_asset = worst_asset = None
        
        # Calculate profit/loss distribution
        profit_count = sum(1 for ap in asset_performance if ap["profit_loss"] > 0)
        loss_count = sum(1 for ap in asset_performance if ap["profit_loss"] < 0)
        neutral_count = len(asset_performance) - profit_count - loss_count
        
        return {
            "total_return": total_profit_loss,
            "total_return_percentage": (total_profit_loss / total_initial_value) * 100 if total_initial_value > 0 else 0,
            "best_performing_asset": best_asset,
            "worst_performing_asset": worst_asset,
            "profit_loss_distribution": {
                "profit": profit_count,
                "loss": loss_count,
                "neutral": neutral_count
            }
        }
    
    def _identify_risk_factors(self, asset_allocation: Dict[str, float], customer_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify specific risk factors in the portfolio"""
        risk_factors = []
        
        # Concentration risk
        for asset_type, percentage in asset_allocation.items():
            if percentage > 50:
                risk_factors.append({
                    "type": "concentration",
                    "asset_type": asset_type,
                    "percentage": percentage,
                    "severity": "HIGH" if percentage > 70 else "MEDIUM",
                    "description": f"Tài sản {asset_type} chiếm {percentage:.1f}% danh mục"
                })
        
        # Risk profile mismatch
        risk_profile = customer_data.get("riskProfile", "MEDIUM")
        if risk_profile == "LOW" and any(asset_type in ["STOCK", "CRYPTO"] for asset_type in asset_allocation.keys()):
            risk_factors.append({
                "type": "risk_mismatch",
                "severity": "MEDIUM",
                "description": "Khách hàng có hồ sơ rủi ro thấp nhưng sở hữu tài sản rủi ro cao"
            })
        
        return risk_factors
    
    def _calculate_stress_test_results(self, asset_data: List[Dict[str, Any]], total_value: float) -> Dict[str, Any]:
        """Calculate dynamic stress test results based on portfolio composition"""
        if not asset_data:
            return {
                "market_crash_scenario": {
                    "description": "Kịch bản thị trường sụp đổ 20%",
                    "estimated_loss": 0,
                    "recovery_time": "N/A"
                },
                "interest_rate_increase": {
                    "description": "Kịch bản lãi suất tăng 2%",
                    "impact": "Không ảnh hưởng",
                    "estimated_impact": 0
                }
            }
        
        # Calculate portfolio composition
        asset_types = {}
        for asset in asset_data:
            asset_type = asset.get("assetType", "OTHER")
            value = asset.get("currentValue", 0)
            asset_types[asset_type] = asset_types.get(asset_type, 0) + value
        
        # Calculate weighted impact
        market_crash_impact = 0
        interest_rate_impact = 0
        
        for asset_type, value in asset_types.items():
            percentage = (value / total_value) * 100
            
            if asset_type in ["STOCK", "FUND"]:
                market_crash_impact += percentage * 0.15  # 15% loss for stocks/funds
            elif asset_type == "BOND":
                interest_rate_impact += percentage * 0.08  # 8% loss for bonds
            elif asset_type == "GOLD":
                market_crash_impact += percentage * 0.05  # 5% loss for gold
            elif asset_type == "SAVINGS":
                interest_rate_impact += percentage * 0.02  # 2% gain for savings
        
        # Determine recovery time based on portfolio composition
        high_risk_percentage = sum(percentage for asset_type, percentage in asset_types.items() 
                                  if asset_type in ["STOCK", "FUND"]) / total_value * 100
        
        if high_risk_percentage > 50:
            recovery_time = "3-5 năm"
        elif high_risk_percentage > 20:
            recovery_time = "2-3 năm"
        else:
            recovery_time = "1-2 năm"
        
        return {
            "market_crash_scenario": {
                "description": "Kịch bản thị trường sụp đổ 20%",
                "estimated_loss": round(total_value * (market_crash_impact / 100), 2),
                "recovery_time": recovery_time,
                "affected_assets": [asset_type for asset_type in asset_types.keys() 
                                  if asset_type in ["STOCK", "FUND", "GOLD"]]
            },
            "interest_rate_increase": {
                "description": "Kịch bản lãi suất tăng 2%",
                "impact": "Giảm giá trị trái phiếu, tăng lãi tiết kiệm",
                "estimated_impact": round(total_value * (interest_rate_impact / 100), 2),
                "affected_assets": [asset_type for asset_type in asset_types.keys() 
                                  if asset_type in ["BOND", "SAVINGS"]]
            }
        }
    
    def _calculate_concentration_risk(self, asset_data: List[Dict[str, Any]]) -> float:
        """Calculate concentration risk score"""
        if not asset_data:
            return 0.0
        
        total_value = sum(asset.get("currentValue", 0) for asset in asset_data)
        if total_value == 0:
            return 0.0
        
        # Calculate Herfindahl-Hirschman Index (HHI)
        hhi = 0
        for asset in asset_data:
            percentage = (asset.get("currentValue", 0) / total_value) * 100
            hhi += (percentage / 100) ** 2
        
        # Convert to 0-1 scale (0 = no concentration, 1 = maximum concentration)
        return min(hhi, 1.0)
    
    def _estimate_portfolio_volatility(self, asset_data: List[Dict[str, Any]]) -> float:
        """Estimate portfolio volatility based on asset composition"""
        if not asset_data:
            return 0.0
        
        # Volatility estimates for different asset types
        volatility_estimates = {
            "SAVINGS": 0.02,  # 2% volatility
            "BOND": 0.05,     # 5% volatility
            "GOLD": 0.15,     # 15% volatility
            "FUND": 0.20,     # 20% volatility
            "STOCK": 0.25,    # 25% volatility
            "OTHER": 0.10     # 10% volatility
        }
        
        total_value = sum(asset.get("currentValue", 0) for asset in asset_data)
        if total_value == 0:
            return 0.0
        
        # Calculate weighted average volatility
        weighted_volatility = 0
        for asset in asset_data:
            asset_type = asset.get("assetType", "OTHER")
            value = asset.get("currentValue", 0)
            volatility = volatility_estimates.get(asset_type, 0.10)
            weighted_volatility += (value / total_value) * volatility
        
        return round(weighted_volatility, 3)
    def _get_market_context_for_product(self, product: Dict[str, Any], market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get market context for a specific product"""
        context = {}
        
        # Add market sentiment
        if market_data:
            context["market_sentiment"] = market_data["data"]["market_sentiment"]
        
        return context 

    def _calculate_model_confidence(self, customer_data: Dict[str, Any]) -> float:
        """Calculate confidence level of ML predictions based on data quality"""
        confidence = 0.8  # Base confidence
        
        # Check if we have all required features
        required_features = ["age", "income", "currentAssets", "investmentHorizon", "riskTolerance"]
        available_features = sum(1 for feature in required_features if customer_data.get(feature) is not None)
        
        # Adjust confidence based on feature availability
        feature_ratio = available_features / len(required_features)
        confidence *= feature_ratio
        
        # Adjust confidence based on data quality
        if customer_data.get("age") and 18 <= customer_data["age"] <= 80:
            confidence += 0.1
        if customer_data.get("income") and customer_data["income"] > 0:
            confidence += 0.1
        if customer_data.get("currentAssets") and customer_data["currentAssets"] >= 0:
            confidence += 0.1
        
        return min(1.0, max(0.0, confidence))

    def _is_product_suitable_for_market_conditions(self, product: Dict[str, Any], market_data: Dict[str, Any]) -> bool:
        """Check if a product is suitable for current market conditions"""
        if not market_data or "data" not in market_data:
            return True
        
        market_info = market_data["data"]
        sentiment = market_info.get("market_sentiment", "NEUTRAL")
        
        # Market condition filtering
        if product["asset_type"] == "STOCK":
            if sentiment == "BEARISH":
                return False  # Avoid stocks in bear market
        elif product["asset_type"] == "BOND":
            if sentiment == "BULLISH":
                return False  # Avoid bonds in bull market
        elif product["asset_type"] == "GOLD":
            if sentiment == "BULLISH":
                return False  # Avoid gold in bull market
        
        return True
    
    def _calculate_ml_based_adjustment(
        self,
        product: Dict[str, Any],
        predicted_risk_score: float,
        predicted_expected_return: float,
        market_data: Dict[str, Any]
    ) -> float:
        """Calculate ML-based adjustment to product score"""
        adjustment = 0
        
        # Risk alignment with ML prediction
        product_risk_mapping = {"LOW": 3, "MEDIUM": 6, "HIGH": 9}
        product_risk = product_risk_mapping.get(product["risk_level"], 6)
        
        risk_diff = abs(predicted_risk_score - product_risk)
        if risk_diff <= 2:
            adjustment += 10  # Good risk alignment
        elif risk_diff <= 4:
            adjustment += 5   # Moderate risk alignment
        else:
            adjustment -= 5   # Poor risk alignment
        
        # Expected return alignment
        return_diff = abs(predicted_expected_return - product["expected_return"])
        if return_diff <= 3:
            adjustment += 8   # Good return alignment
        elif return_diff <= 6:
            adjustment += 4   # Moderate return alignment
        else:
            adjustment -= 3   # Poor return alignment
        
        # Market volatility consideration
        if market_data and "data" in market_data:
            market_info = market_data["data"]
            if "indices" in market_info and "^VIX" in market_info["indices"]:
                vix_level = market_info["indices"]["^VIX"].get("price", 20)
                
                if vix_level > 30:  # High volatility
                    if product["asset_type"] in ["SAVINGS", "BOND"]:
                        adjustment += 5  # Prefer safe assets
                    elif product["asset_type"] == "STOCK":
                        adjustment -= 5  # Avoid risky assets
                elif vix_level < 15:  # Low volatility
                    if product["asset_type"] == "STOCK":
                        adjustment += 5  # Prefer growth assets
        
        return adjustment
    
    def _get_enhanced_market_context_for_product(
        self,
        product: Dict[str, Any],
        market_data: Dict[str, Any],
        predicted_risk_score: float,
        predicted_expected_return: float
    ) -> Dict[str, Any]:
        """Get enhanced market context for a specific product with ML insights"""
        context = {
            "market_sentiment": "NEUTRAL",
            "ml_insights": {},
            "market_indicators": {},
            "recommendation_reason": ""
        }
        
        if market_data and "data" in market_data:
            market_info = market_data["data"]
            context["market_sentiment"] = market_info.get("market_sentiment", "NEUTRAL")
            
            # Add ML insights
            context["ml_insights"] = {
                "predicted_risk_score": predicted_risk_score,
                "predicted_expected_return": predicted_expected_return,
                "risk_alignment": self._calculate_risk_alignment(product, predicted_risk_score),
                "return_alignment": self._calculate_return_alignment(product, predicted_expected_return)
            }
            
            # Add market indicators
            if "indices" in market_info:
                context["market_indicators"] = {
                    "s&p_500": market_info["indices"].get("^GSPC", {}),
                    "dow_jones": market_info["indices"].get("^DJI", {}),
                    "nasdaq": market_info["indices"].get("^IXIC", {}),
                    "vix": market_info["indices"].get("^VIX", {})
                }
            
            # Generate recommendation reason
            context["recommendation_reason"] = self._generate_ml_based_recommendation_reason(
                product, context["ml_insights"], context["market_sentiment"]
            )
        
        return context
    
    def _calculate_risk_alignment(self, product: Dict[str, Any], predicted_risk: float) -> str:
        """Calculate risk alignment between product and ML prediction"""
        product_risk_mapping = {"LOW": 3, "MEDIUM": 6, "HIGH": 9}
        product_risk = product_risk_mapping.get(product["risk_level"], 6)
        
        diff = abs(predicted_risk - product_risk)
        if diff <= 2:
            return "EXCELLENT"
        elif diff <= 4:
            return "GOOD"
        else:
            return "POOR"
    
    def _calculate_return_alignment(self, product: Dict[str, Any], predicted_return: float) -> str:
        """Calculate return alignment between product and ML prediction"""
        diff = abs(predicted_return - product["expected_return"])
        if diff <= 3:
            return "EXCELLENT"
        elif diff <= 6:
            return "GOOD"
        else:
            return "POOR"
    
    def _generate_ml_based_recommendation_reason(
        self,
        product: Dict[str, Any],
        ml_insights: Dict[str, Any],
        market_sentiment: str
    ) -> str:
        """Generate recommendation reason based on ML insights and market sentiment"""
        risk_alignment = ml_insights.get("risk_alignment", "GOOD")
        return_alignment = ml_insights.get("return_alignment", "GOOD")
        
        reasons = []
        
        if risk_alignment == "EXCELLENT":
            reasons.append("Phù hợp hoàn hảo với hồ sơ rủi ro dự đoán")
        elif risk_alignment == "GOOD":
            reasons.append("Phù hợp với hồ sơ rủi ro")
        
        if return_alignment == "EXCELLENT":
            reasons.append("Lợi nhuận kỳ vọng phù hợp với dự đoán ML")
        elif return_alignment == "GOOD":
            reasons.append("Lợi nhuận kỳ vọng hợp lý")
        
        if market_sentiment == "BULLISH" and product["asset_type"] == "STOCK":
            reasons.append("Thị trường tăng trưởng, phù hợp đầu tư cổ phiếu")
        elif market_sentiment == "BEARISH" and product["asset_type"] in ["BOND", "SAVINGS"]:
            reasons.append("Thị trường biến động, tài sản an toàn được ưu tiên")
        
        if not reasons:
            reasons.append("Sản phẩm phù hợp với danh mục đầu tư")
        
        return ". ".join(reasons)

    def _get_savings_market_adjustment(self, market_data: Dict[str, Any]) -> float:
        """Get market adjustment for savings products based on interest rate trends"""
        if not market_data or "data" not in market_data:
            return 0.0
        
        # Adjust based on forex rates (USD/VND) as proxy for interest rate environment
        forex_data = market_data["data"].get("forex", {})
        usd_vnd = forex_data.get("USDVND", {})
        
        if usd_vnd and "exchange_rate" in usd_vnd:
            rate = usd_vnd["exchange_rate"]
            # Higher USD/VND rate might indicate higher interest rates
            if rate > 24000:
                return 0.5  # Slightly higher returns
            elif rate < 23000:
                return -0.5  # Slightly lower returns
        
        return 0.0
    
    def _get_fund_market_adjustment(self, market_data: Dict[str, Any]) -> float:
        """Get market adjustment for fund products based on market sentiment"""
        if not market_data or "data" not in market_data:
            return 0.0
        
        market_sentiment = market_data["data"].get("market_sentiment", "NEUTRAL")
        
        if market_sentiment == "BULLISH":
            return 1.0  # Higher returns in bullish market
        elif market_sentiment == "BEARISH":
            return -1.0  # Lower returns in bearish market
        
        return 0.0
    
    def _get_bond_market_adjustment(self, market_data: Dict[str, Any]) -> float:
        """Get market adjustment for bond products based on interest rate environment"""
        if not market_data or "data" not in market_data:
            return 0.0
        
        # Bonds perform better when interest rates are falling
        market_sentiment = market_data["data"].get("market_sentiment", "NEUTRAL")
        
        if market_sentiment == "BEARISH":
            return 0.5  # Bonds are safer in bear markets
        elif market_sentiment == "BULLISH":
            return -0.5  # Bonds less attractive in bull markets
        
        return 0.0
    
    def _get_stock_market_adjustment(self, market_data: Dict[str, Any]) -> float:
        """Get market adjustment for stock products based on market performance"""
        if not market_data or "data" not in market_data:
            return 0.0
        
        market_sentiment = market_data["data"].get("market_sentiment", "NEUTRAL")
        
        if market_sentiment == "BULLISH":
            return 2.0  # Much higher returns in bullish market
        elif market_sentiment == "BEARISH":
            return -2.0  # Much lower returns in bearish market
        
        return 0.0
    
    def _get_gold_market_adjustment(self, market_data: Dict[str, Any]) -> float:
        """Get market adjustment for gold products based on market conditions"""
        if not market_data or "data" not in market_data:
            return 0.0
        
        market_sentiment = market_data["data"].get("market_sentiment", "NEUTRAL")
        
        if market_sentiment == "BEARISH":
            return 1.0  # Gold is safe haven in bear markets
        elif market_sentiment == "BULLISH":
            return -0.5  # Gold less attractive in bull markets
        
        return 0.0
    
    def _get_market_based_advantages(self, asset_type: str, market_data: Dict[str, Any]) -> List[str]:
        """Get market-based advantages for a product type"""
        advantages = []
        
        if not market_data or "data" not in market_data:
            return advantages
        
        market_sentiment = market_data["data"].get("market_sentiment", "NEUTRAL")
        
        if asset_type == "STOCK" and market_sentiment == "BULLISH":
            advantages.append("Thị trường đang tăng trưởng tốt")
        elif asset_type == "BOND" and market_sentiment == "BEARISH":
            advantages.append("Tài sản an toàn trong thời kỳ biến động")
        elif asset_type == "GOLD" and market_sentiment == "BEARISH":
            advantages.append("Tài sản trú ẩn an toàn")
        elif asset_type == "SAVINGS":
            advantages.append("Lãi suất ổn định trong mọi điều kiện thị trường")
        
        return advantages
    
    def _get_market_based_disadvantages(self, asset_type: str, market_data: Dict[str, Any]) -> List[str]:
        """Get market-based disadvantages for a product type"""
        disadvantages = []
        
        if not market_data or "data" not in market_data:
            return disadvantages
        
        market_sentiment = market_data["data"].get("market_sentiment", "NEUTRAL")
        
        if asset_type == "STOCK" and market_sentiment == "BEARISH":
            disadvantages.append("Thị trường đang biến động mạnh")
        elif asset_type == "BOND" and market_sentiment == "BULLISH":
            disadvantages.append("Lợi nhuận thấp so với thị trường tăng trưởng")
        elif asset_type == "GOLD" and market_sentiment == "BULLISH":
            disadvantages.append("Không sinh lời trong thị trường tăng trưởng")
        
        return disadvantages

    async def initialize_products(self):
        """Initialize investment products with market data"""
        if not self.investment_products:
            self.investment_products = await self._load_investment_products()
