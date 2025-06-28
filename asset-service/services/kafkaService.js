const { Kafka } = require('kafkajs');

let producer;
let consumer;

const setupKafka = async () => {
  try {
    // Setup producer
    producer = global.kafka.producer();
    await producer.connect();
    console.log('Kafka producer connected');

    // Setup consumer
    consumer = global.kafka.consumer({ groupId: 'asset-service-group' });
    await consumer.connect();
    await consumer.subscribe({ topic: 'asset-updates', fromBeginning: true });
    
    await consumer.run({
      eachMessage: async ({ topic, partition, message }) => {
        try {
          const data = JSON.parse(message.value.toString());
          console.log('Received message:', data);
          
          // Handle different message types
          switch (data.type) {
            case 'asset.value.updated':
              await handleAssetValueUpdate(data.payload);
              break;
            case 'market.data.updated':
              await handleMarketDataUpdate(data.payload);
              break;
            default:
              console.log('Unknown message type:', data.type);
          }
        } catch (error) {
          console.error('Error processing message:', error);
        }
      },
    });
    
    console.log('Kafka consumer started');
  } catch (error) {
    console.error('Kafka setup error:', error);
  }
};

const publishAssetUpdate = async (type, payload) => {
  try {
    if (!producer) {
      console.warn('Kafka producer not initialized');
      return;
    }

    const message = {
      type,
      payload,
      timestamp: new Date().toISOString(),
      service: 'asset-service'
    };

    await producer.send({
      topic: 'asset-updates',
      messages: [
        {
          key: payload.assetId || payload._id,
          value: JSON.stringify(message)
        }
      ]
    });

    console.log('Published message:', type);
  } catch (error) {
    console.error('Error publishing message:', error);
  }
};

const handleAssetValueUpdate = async (payload) => {
  try {
    // Handle asset value updates from other services
    console.log('Handling asset value update:', payload);
    
    // Clear relevant cache
    if (payload.customerId) {
      await global.redisClient.del(`customer-assets:${payload.customerId}`);
    }
    await global.redisClient.del('assets');
  } catch (error) {
    console.error('Error handling asset value update:', error);
  }
};

const handleMarketDataUpdate = async (payload) => {
  try {
    // Handle market data updates
    console.log('Handling market data update:', payload);
    
    // Clear market-related cache
    await global.redisClient.del('market-data');
  } catch (error) {
    console.error('Error handling market data update:', error);
  }
};

const disconnectKafka = async () => {
  try {
    if (producer) {
      await producer.disconnect();
    }
    if (consumer) {
      await consumer.disconnect();
    }
    console.log('Kafka connections closed');
  } catch (error) {
    console.error('Error disconnecting Kafka:', error);
  }
};

// Graceful shutdown
process.on('SIGTERM', disconnectKafka);
process.on('SIGINT', disconnectKafka);

module.exports = {
  setupKafka,
  publishAssetUpdate,
  disconnectKafka
}; 