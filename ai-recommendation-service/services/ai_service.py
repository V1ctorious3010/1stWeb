import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from typing import List, Dict, Any, Optional
import joblib
import os
from datetime import datetime, timedelta
import random

class AIRecommendationService:
    def __init__(self):
        self.risk_model = None
        self.return_model = None
        self.scaler = StandardScaler()
        self.load_or_train_models()
        
        # Mock investment products database
        self.investment_products = self._load_investment_products()
    
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
    
    def _load_investment_products(self) -> List[Dict[str, Any]]:
        """Load mock investment products database"""
        return [
            {
                "product_name": "Tiết kiệm có kỳ hạn 12 tháng",
                "asset_type": "SAVINGS",
                "expected_return": 7.5,
                "risk_level": "LOW",
                "investment_horizon": "1 năm",
                "min_investment": 1000000,
                "max_investment": None,
                "description": "Sản phẩm tiết kiệm an toàn với lãi suất cố định",
                "advantages": ["An toàn", "Lãi suất ổn định", "Thanh khoản tốt"],
                "disadvantages": ["Lợi nhuận thấp", "Không bảo vệ lạm phát"],
                "institution": "Ngân hàng TMCP",
                "product_code": "TK12T"
            },
            {
                "product_name": "Quỹ mở VFMVF1",
                "asset_type": "FUND",
                "expected_return": 12.0,
                "risk_level": "MEDIUM",
                "investment_horizon": "3-5 năm",
                "min_investment": 500000,
                "max_investment": None,
                "description": "Quỹ đầu tư cổ phiếu với danh mục đa dạng",
                "advantages": ["Đa dạng hóa", "Quản lý chuyên nghiệp", "Lợi nhuận tiềm năng cao"],
                "disadvantages": ["Rủi ro thị trường", "Phí quản lý"],
                "institution": "VFM",
                "product_code": "VFMVF1"
            },
            {
                "product_name": "Trái phiếu Chính phủ 5 năm",
                "asset_type": "BOND",
                "expected_return": 8.5,
                "risk_level": "LOW",
                "investment_horizon": "5 năm",
                "min_investment": 100000,
                "max_investment": None,
                "description": "Trái phiếu Chính phủ với độ an toàn cao",
                "advantages": ["An toàn", "Lãi suất ổn định", "Được Chính phủ bảo lãnh"],
                "disadvantages": ["Kỳ hạn dài", "Thanh khoản hạn chế"],
                "institution": "Bộ Tài chính",
                "product_code": "TPCP5Y"
            },
            {
                "product_name": "Cổ phiếu VNM",
                "asset_type": "STOCK",
                "expected_return": 15.0,
                "risk_level": "HIGH",
                "investment_horizon": "5-10 năm",
                "min_investment": 1000000,
                "max_investment": None,
                "description": "Cổ phiếu của Tập đoàn Vinamilk",
                "advantages": ["Tiềm năng tăng trưởng cao", "Cổ tức ổn định"],
                "disadvantages": ["Rủi ro cao", "Biến động giá lớn"],
                "institution": "Vinamilk",
                "product_code": "VNM"
            },
            {
                "product_name": "Vàng SJC",
                "asset_type": "GOLD",
                "expected_return": 6.0,
                "risk_level": "MEDIUM",
                "investment_horizon": "3-5 năm",
                "min_investment": 500000,
                "max_investment": None,
                "description": "Đầu tư vàng vật chất",
                "advantages": ["Bảo vệ lạm phát", "Tài sản thực"],
                "disadvantages": ["Không sinh lời", "Chi phí lưu trữ"],
                "institution": "SJC",
                "product_code": "SJC"
            }
        ]
    
    async def generate_recommendations(
        self,
        customer_data: Dict[str, Any],
        asset_data: List[Dict[str, Any]],
        market_data: Dict[str, Any],
        investment_amount: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """Generate investment recommendations based on customer profile and current assets"""
        
        # Analyze customer profile
        risk_profile = customer_data.get("riskProfile", "MEDIUM")
        risk_score = customer_data.get("riskScore", 5)
        current_assets_value = sum(asset.get("currentValue", 0) for asset in asset_data)
        
        # Filter products based on risk profile
        suitable_products = []
        for product in self.investment_products:
            if self._is_product_suitable(product, risk_profile, risk_score):
                suitable_products.append(product)
        
        # Score and rank products
        scored_products = []
        for product in suitable_products:
            score = self._calculate_product_score(
                product, customer_data, asset_data, market_data, investment_amount
            )
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
            
            recommendations.append(recommendation)
        
        return recommendations
    
    def _is_product_suitable(self, product: Dict[str, Any], risk_profile: str, risk_score: float) -> bool:
        """Check if a product is suitable for the customer's risk profile"""
        risk_mapping = {
            "LOW": ["LOW"],
            "MEDIUM": ["LOW", "MEDIUM"],
            "HIGH": ["LOW", "MEDIUM", "HIGH"]
        }
        
        return product["risk_level"] in risk_mapping.get(risk_profile, ["MEDIUM"])
    
    def _calculate_product_score(
        self,
        product: Dict[str, Any],
        customer_data: Dict[str, Any],
        asset_data: List[Dict[str, Any]],
        market_data: Dict[str, Any],
        investment_amount: Optional[float]
    ) -> float:
        """Calculate a score for a product based on various factors"""
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
        
        # Market condition adjustment
        if market_data:
            # Adjust based on market conditions (simplified)
            if product["asset_type"] == "STOCK" and market_data.get("market_trend") == "bullish":
                score += 10
            elif product["asset_type"] == "BOND" and market_data.get("interest_rate_trend") == "rising":
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
                "total_value": 0,
                "asset_allocation": {},
                "risk_score": 5,
                "diversification_score": 0,
                "performance_score": 0,
                "recommendations": ["Bắt đầu xây dựng danh mục đầu tư"]
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
        
        return {
            "total_value": total_value,
            "asset_allocation": asset_allocation,
            "risk_score": risk_score,
            "diversification_score": diversification_score,
            "performance_score": performance_score,
            "recommendations": recommendations
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
        """Assess overall risk profile of the customer"""
        
        # Calculate overall risk level
        portfolio_risk_score = self._calculate_portfolio_risk_score(asset_data, customer_data)
        customer_risk_score = customer_data.get("riskScore", 5)
        
        # Combine customer and portfolio risk
        overall_risk_score = (portfolio_risk_score + customer_risk_score) / 2
        
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
                        "description": f"Tài sản {asset.get('assetName')} chiếm {round(percentage, 2)}% danh mục"
                    })
        
        # High-risk assets for low-risk customers
        risk_profile = customer_data.get("riskProfile", "MEDIUM")
        if risk_profile == "LOW":
            high_risk_assets = [asset for asset in asset_data if asset.get("riskLevel") == "HIGH"]
            if high_risk_assets:
                risk_factors.append({
                    "type": "risk_mismatch",
                    "description": "Khách hàng có hồ sơ rủi ro thấp nhưng sở hữu tài sản rủi ro cao"
                })
        
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
        
        # Stress test results (simplified)
        stress_test_results = {
            "market_crash_scenario": {
                "description": "Kịch bản thị trường sụp đổ 20%",
                "estimated_loss": round(total_value * 0.15, 2),
                "recovery_time": "2-3 năm"
            },
            "interest_rate_increase": {
                "description": "Kịch bản lãi suất tăng 2%",
                "impact": "Giảm giá trị trái phiếu, tăng lãi tiết kiệm",
                "estimated_impact": round(total_value * 0.05, 2)
            }
        }
        
        return {
            "overall_risk_level": overall_risk_level,
            "risk_score": round(overall_risk_score, 2),
            "risk_factors": risk_factors,
            "risk_mitigation": risk_mitigation,
            "stress_test_results": stress_test_results
        } 