const express = require('express');
const mongoose = require('mongoose');
const redis = require('redis');
const cors = require('cors');
const helmet = require('helmet');
const rateLimit = require('express-rate-limit');
const { Kafka } = require('kafkajs');
require('dotenv').config();

const assetRoutes = require('./routes/assetRoutes');
const { errorHandler } = require('./middleware/errorHandler');
const { setupKafka } = require('./services/kafkaService');

const app = express();
const PORT = process.env.PORT || 8002;

// Middleware
app.use(helmet());
app.use(cors());
app.use(express.json());

// Rate limiting
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100 // limit each IP to 100 requests per windowMs
});
app.use(limiter);

// Connect to MongoDB
mongoose.connect(process.env.MONGODB_URI || 'mongodb://localhost:27017/asset', {
  useNewUrlParser: true,
  useUnifiedTopology: true,
})
.then(() => console.log('Connected to MongoDB'))
.catch(err => console.error('MongoDB connection error:', err));

// Connect to Redis
const redisClient = redis.createClient({
  url: process.env.REDIS_URL || 'redis://localhost:6379'
});

redisClient.on('error', (err) => console.log('Redis Client Error', err));
redisClient.on('connect', () => console.log('Connected to Redis'));

redisClient.connect().catch(console.error);

// Make Redis available globally
global.redisClient = redisClient;

// Setup Kafka
const kafka = new Kafka({
  clientId: 'asset-service',
  brokers: [process.env.KAFKA_BROKER || 'localhost:9092']
});

global.kafka = kafka;

// Initialize Kafka producer and consumer
setupKafka();

// Routes
app.use('/api/assets', assetRoutes);

// Health check
app.get('/health', (req, res) => {
  res.status(200).json({ 
    status: 'OK', 
    service: 'Asset Service',
    timestamp: new Date().toISOString()
  });
});

// Error handling middleware
app.use(errorHandler);

// 404 handler
app.use('*', (req, res) => {
  res.status(404).json({ message: 'Route not found' });
});

app.listen(PORT, () => {
  console.log(`Asset Service running on port ${PORT}`);
});

module.exports = app; 