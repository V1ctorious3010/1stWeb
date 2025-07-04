# Hướng dẫn Cài đặt và Chạy Hệ thống Quản lý Tài sản

## Yêu cầu hệ thống

- Docker & Docker Compose
- Node.js 18+ (để chạy script khởi tạo dữ liệu)
- Python 3.9+ (để chạy AI service riêng lẻ nếu cần)

## Cách 1: Chạy toàn bộ hệ thống bằng Docker (Khuyến nghị)

### Bước 1: Clone và cài đặt

### Bước 2: Kiểm tra các service

### Bước 3: Khởi tạo dữ liệu mẫu


### Bước 4: Truy cập ứng dụng
- **Frontend**: http://localhost:3000
- **API Gateway**: http://localhost:8000
- **Customer Service**: http://localhost:8001
- **Asset Service**: http://localhost:8002
- **Market Data Service**: http://localhost:8003
- **AI Service**: http://localhost:8004

## Cách 2: Chạy từng service riêng lẻ

### Bước 1: Cài đặt dependencies


### Bước 2: Khởi động cơ sở dữ liệu


### Bước 3: Chạy các service


## Dữ liệu mẫu

Sau khi chạy script khởi tạo, bạn sẽ có:

### Khách hàng mẫu:
- **CUST001**: Nguyễn Văn An (Risk: MEDIUM)
- **CUST002**: Trần Thị Bình (Risk: LOW)
- **CUST003**: Lê Văn Cường (Risk: HIGH)

### Tài sản mẫu:
- Tiết kiệm có kỳ hạn
- Quỹ mở VFMVF1
- Trái phiếu Chính phủ
- Cổ phiếu VNM
- Vàng SJC
- Bất động sản

## API Endpoints

### Customer Service (Port 8001)
- `GET /api/customers` - Lấy danh sách khách hàng
- `GET /api/customers/:id` - Lấy thông tin khách hàng
- `POST /api/customers` - Tạo khách hàng mới
- `PUT /api/customers/:id` - Cập nhật khách hàng
- `DELETE /api/customers/:id` - Xóa khách hàng

### Asset Service (Port 8002)
- `GET /api/assets` - Lấy danh sách tài sản
- `GET /api/assets/customer/:customerId` - Lấy tài sản theo khách hàng
- `POST /api/assets` - Tạo tài sản mới
- `PUT /api/assets/:id` - Cập nhật tài sản
- `DELETE /api/assets/:id` - Xóa tài sản

### AI Service (Port 8004)
- `POST /api/ai/recommendations` - Lấy gợi ý đầu tư
- `GET /api/ai/analysis/:customerId` - Phân tích danh mục
- `GET /api/ai/risk-assessment/:customerId` - Đánh giá rủi ro

### API Gateway (Port 8000)
- Tất cả API trên thông qua gateway
- `GET /api/dashboard/:customerId` - Dữ liệu dashboard tổng hợp

## Tính năng chính

### Frontend
- **Dashboard**: Tổng quan tài sản, biểu đồ phân bổ
- **Assets**: Quản lý tài sản, xem chi tiết
- **Recommendations**: Gợi ý đầu tư từ AI
- **Profile**: Thông tin khách hàng
- **Chatbot**: Hỗ trợ tương tác

### Backend
- **Microservice Architecture**: 5 service độc lập
- **AI Integration**: Machine learning cho gợi ý đầu tư
- **Real-time Updates**: Kafka message broker
- **Caching**: Redis cache
- **Database**: MongoDB



## Development

### Cấu trúc thư mục
```
1stWeb/
├── frontend/                 # React frontend
├── customer-service/         # Customer management
├── asset-service/           # Asset management
├── market-data-service/     # Market data
├── ai-recommendation-service/ # AI recommendations
├── api-gateway/             # API Gateway
├── scripts/                 # Utility scripts
├── docker-compose.yml       # Docker configuration
└── README.md               # Documentation
```

### Environment Variables
Tạo file `.env` trong mỗi service nếu cần:
```env
NODE_ENV=development
MONGODB_URI=mongodb://admin:password123@localhost:27017/dbname?authSource=admin
REDIS_URL=redis://localhost:6379
KAFKA_BROKER=localhost:9092
```

## Support

Nếu gặp vấn đề, vui lòng:
1. Kiểm tra logs của service
2. Đảm bảo tất cả dependencies đã được cài đặt
3. Kiểm tra kết nối database và Redis
4. Xem hướng dẫn troubleshooting ở trên 
