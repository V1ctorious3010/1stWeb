const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const rateLimit = require('express-rate-limit');
const { createProxyMiddleware } = require('http-proxy-middleware');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 8000;

// Middleware
app.use(helmet());
app.use(cors());
app.use(express.json());

// Rate limiting
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 1000 // limit each IP to 1000 requests per windowMs
});
app.use(limiter);

// Health check
app.get('/health', (req, res) => {
  res.status(200).json({ 
    status: 'OK', 
    service: 'API Gateway',
    timestamp: new Date().toISOString(),
    services: {
      customer: process.env.CUSTOMER_SERVICE_URL || 'http://customer-service:8001',
      asset: process.env.ASSET_SERVICE_URL || 'http://asset-service:8002',
      market: process.env.MARKET_DATA_SERVICE_URL || 'http://market-data-service:8003',
      ai: process.env.AI_SERVICE_URL || 'http://ai-recommendation-service:8004'
    }
  });
});

// Proxy middleware configuration
const createProxy = (target, pathRewrite = {}) => {
  return createProxyMiddleware({
    target,
    changeOrigin: true,
    pathRewrite,
    onError: (err, req, res) => {
      console.error(`Proxy error for ${target}:`, err.message);
      res.status(503).json({
        error: 'Service temporarily unavailable',
        service: target,
        message: err.message
      });
    },
    onProxyReq: (proxyReq, req, res) => {
      console.log(`${req.method} ${req.path} -> ${target}`);
    }
  });
};

// Customer Service routes
app.use('/api/customers', createProxy(
  process.env.CUSTOMER_SERVICE_URL || 'http://customer-service:8001',
  { '^/api/customers': '/api/customers' }
));

// Asset Service routes
app.use('/api/assets', createProxy(
  process.env.ASSET_SERVICE_URL || 'http://asset-service:8002',
  { '^/api/assets': '/api/assets' }
));

// Market Data Service routes
app.use('/api/market', createProxy(
  process.env.MARKET_DATA_SERVICE_URL || 'http://market-data-service:8003',
  { '^/api/market': '/api/market' }
));

// AI Recommendation Service routes
app.use('/api/ai', createProxy(
  process.env.AI_SERVICE_URL || 'http://ai-recommendation-service:8004',
  { '^/api/ai': '' }
));

// Combined API endpoints
app.get('/api/dashboard/:customerId', async (req, res) => {
  try {
    const { customerId } = req.params;
    const axios = require('axios');
    
    // Fetch data from multiple services
    const [customerResponse, assetsResponse, recommendationsResponse] = await Promise.allSettled([
      axios.get(`${process.env.CUSTOMER_SERVICE_URL || 'http://customer-service:8001'}/api/customers/${customerId}`),
      axios.get(`${process.env.ASSET_SERVICE_URL || 'http://asset-service:8002'}/api/assets/customer/${customerId}`),
      axios.post(`${process.env.AI_SERVICE_URL || 'http://ai-recommendation-service:8004'}/recommendations`, {
        customer_id: customerId
      })
    ]);
    
    const dashboardData = {
      customer: customerResponse.status === 'fulfilled' ? customerResponse.value.data : null,
      assets: assetsResponse.status === 'fulfilled' ? assetsResponse.value.data : null,
      recommendations: recommendationsResponse.status === 'fulfilled' ? recommendationsResponse.value.data : null,
      timestamp: new Date().toISOString()
    };
    
    res.json(dashboardData);
  } catch (error) {
    console.error('Dashboard API error:', error);
    res.status(500).json({
      error: 'Failed to fetch dashboard data',
      message: error.message
    });
  }
});

// 404 handler
app.use('*', (req, res) => {
  res.status(404).json({ 
    message: 'Route not found',
    availableRoutes: [
      '/api/customers/*',
      '/api/assets/*',
      '/api/market/*',
      '/api/ai/*',
      '/api/dashboard/:customerId'
    ]
  });
});

// Error handling middleware
app.use((err, req, res, next) => {
  console.error('API Gateway error:', err);
  res.status(500).json({
    error: 'Internal server error',
    message: process.env.NODE_ENV === 'development' ? err.message : 'Something went wrong'
  });
});

app.listen(PORT, () => {
  console.log(`API Gateway running on port ${PORT}`);
  console.log('Available services:');
  console.log(`- Customer Service: ${process.env.CUSTOMER_SERVICE_URL || 'http://customer-service:8001'}`);
  console.log(`- Asset Service: ${process.env.ASSET_SERVICE_URL || 'http://asset-service:8002'}`);
  console.log(`- Market Data Service: ${process.env.MARKET_DATA_SERVICE_URL || 'http://market-data-service:8003'}`);
  console.log(`- AI Service: ${process.env.AI_SERVICE_URL || 'http://ai-recommendation-service:8004'}`);
});

module.exports = app; 