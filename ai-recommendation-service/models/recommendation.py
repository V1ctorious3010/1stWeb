from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum

class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

class AssetType(str, Enum):
    SAVINGS = "SAVINGS"
    FUND = "FUND"
    STOCK = "STOCK"
    BOND = "BOND"
    REAL_ESTATE = "REAL_ESTATE"
    GOLD = "GOLD"

class InvestmentRecommendation(BaseModel):
    product_name: str = Field(..., description="Tên sản phẩm đầu tư")
    asset_type: AssetType = Field(..., description="Loại tài sản")
    expected_return: float = Field(..., description="Lợi nhuận kỳ vọng (%)")
    risk_level: RiskLevel = Field(..., description="Mức độ rủi ro")
    investment_horizon: str = Field(..., description="Thời gian đầu tư đề xuất")
    min_investment: float = Field(..., description="Số tiền đầu tư tối thiểu")
    max_investment: Optional[float] = Field(None, description="Số tiền đầu tư tối đa")
    description: str = Field(..., description="Mô tả sản phẩm")
    advantages: List[str] = Field(..., description="Ưu điểm")
    disadvantages: List[str] = Field(..., description="Nhược điểm")
    confidence_score: float = Field(..., ge=0, le=1, description="Độ tin cậy của gợi ý")
    institution: str = Field(..., description="Tổ chức phát hành")
    product_code: Optional[str] = Field(None, description="Mã sản phẩm")

class RecommendationRequest(BaseModel):
    customer_id: str = Field(..., description="ID khách hàng")
    investment_amount: Optional[float] = Field(None, description="Số tiền muốn đầu tư")
    preferred_asset_types: Optional[List[AssetType]] = Field(None, description="Loại tài sản ưa thích")
    investment_goals: Optional[List[str]] = Field(None, description="Mục tiêu đầu tư")
    risk_tolerance: Optional[RiskLevel] = Field(None, description="Mức chấp nhận rủi ro")

class RecommendationResponse(BaseModel):
    customer_id: str = Field(..., description="ID khách hàng")
    recommendations: List[InvestmentRecommendation] = Field(..., description="Danh sách gợi ý đầu tư")
    risk_profile: RiskLevel = Field(..., description="Hồ sơ rủi ro của khách hàng")
    total_current_assets: float = Field(..., description="Tổng giá trị tài sản hiện tại")
    generated_at: str = Field(..., description="Thời gian tạo gợi ý")
    portfolio_analysis: Optional[Dict[str, Any]] = Field(None, description="Phân tích danh mục")
    market_insights: Optional[Dict[str, Any]] = Field(None, description="Thông tin thị trường")

class PortfolioAnalysis(BaseModel):
    total_value: float = Field(..., description="Tổng giá trị danh mục")
    asset_allocation: Dict[str, float] = Field(..., description="Phân bổ tài sản")
    risk_score: float = Field(..., ge=0, le=10, description="Điểm rủi ro")
    diversification_score: float = Field(..., ge=0, le=1, description="Điểm đa dạng hóa")
    performance_score: float = Field(..., ge=0, le=1, description="Điểm hiệu suất")
    recommendations: List[str] = Field(..., description="Khuyến nghị cải thiện")

class RiskAssessment(BaseModel):
    overall_risk_level: RiskLevel = Field(..., description="Mức rủi ro tổng thể")
    risk_score: float = Field(..., ge=0, le=10, description="Điểm rủi ro")
    risk_factors: List[Dict[str, Any]] = Field(..., description="Các yếu tố rủi ro")
    risk_mitigation: List[str] = Field(..., description="Biện pháp giảm thiểu rủi ro")
    stress_test_results: Dict[str, Any] = Field(..., description="Kết quả stress test")

class MarketData(BaseModel):
    timestamp: str = Field(..., description="Thời gian cập nhật")
    interest_rates: Dict[str, float] = Field(..., description="Lãi suất các loại")
    fund_performance: Dict[str, float] = Field(..., description="Hiệu suất quỹ")
    market_indices: Dict[str, float] = Field(..., description="Chỉ số thị trường")
    economic_indicators: Dict[str, Any] = Field(..., description="Chỉ số kinh tế") 