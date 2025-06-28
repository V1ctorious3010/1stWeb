const express = require('express');
const router = express.Router();
const Asset = require('../models/Asset');
const { validateAsset } = require('../middleware/validation');
const { cacheMiddleware } = require('../middleware/cache');
const { publishAssetUpdate } = require('../services/kafkaService');

// Get all assets
router.get('/', cacheMiddleware('assets', 300), async (req, res, next) => {
  try {
    const { page = 1, limit = 10, customerId, assetType, status, riskLevel } = req.query;
    
    const filter = { isActive: true };
    if (customerId) filter.customerId = customerId;
    if (assetType) filter.assetType = assetType;
    if (status) filter.status = status;
    if (riskLevel) filter.riskLevel = riskLevel;
    
    const assets = await Asset.find(filter)
      .limit(limit * 1)
      .skip((page - 1) * limit)
      .sort({ createdAt: -1 });
    
    const total = await Asset.countDocuments(filter);
    
    res.json({
      assets,
      totalPages: Math.ceil(total / limit),
      currentPage: page,
      total
    });
  } catch (error) {
    next(error);
  }
});

// Get asset by ID
router.get('/:id', cacheMiddleware('asset', 300), async (req, res, next) => {
  try {
    const asset = await Asset.findOne({
      $or: [
        { assetId: req.params.id },
        { _id: req.params.id }
      ]
    });
    
    if (!asset) {
      return res.status(404).json({ message: 'Asset not found' });
    }
    
    res.json(asset);
  } catch (error) {
    next(error);
  }
});

// Get assets by customer
router.get('/customer/:customerId', cacheMiddleware('customer-assets', 300), async (req, res, next) => {
  try {
    const { customerId } = req.params;
    const { assetType, status } = req.query;
    
    const filter = { customerId, isActive: true };
    if (assetType) filter.assetType = assetType;
    if (status) filter.status = status;
    
    const assets = await Asset.find(filter).sort({ createdAt: -1 });
    
    // Calculate summary
    const summary = {
      totalAssets: assets.length,
      totalValue: assets.reduce((sum, asset) => sum + asset.currentValue, 0),
      totalInitialValue: assets.reduce((sum, asset) => sum + asset.initialValue, 0),
      totalProfitLoss: assets.reduce((sum, asset) => sum + asset.profitLoss, 0),
      assetTypeDistribution: {},
      riskLevelDistribution: {}
    };
    
    // Calculate distributions
    assets.forEach(asset => {
      summary.assetTypeDistribution[asset.assetType] = 
        (summary.assetTypeDistribution[asset.assetType] || 0) + 1;
      summary.riskLevelDistribution[asset.riskLevel] = 
        (summary.riskLevelDistribution[asset.riskLevel] || 0) + 1;
    });
    
    res.json({
      assets,
      summary
    });
  } catch (error) {
    next(error);
  }
});

// Create new asset
router.post('/', validateAsset, async (req, res, next) => {
  try {
    const asset = new Asset(req.body);
    await asset.save();
    
    // Publish to Kafka
    await publishAssetUpdate('asset.created', asset);
    
    // Clear cache
    await global.redisClient.del('assets');
    await global.redisClient.del(`customer-assets:${asset.customerId}`);
    
    res.status(201).json(asset);
  } catch (error) {
    if (error.code === 11000) {
      return res.status(400).json({ 
        message: 'Asset with this assetId already exists' 
      });
    }
    next(error);
  }
});

// Update asset
router.put('/:id', validateAsset, async (req, res, next) => {
  try {
    const asset = await Asset.findOneAndUpdate(
      {
        $or: [
          { assetId: req.params.id },
          { _id: req.params.id }
        ]
      },
      req.body,
      { new: true, runValidators: true }
    );
    
    if (!asset) {
      return res.status(404).json({ message: 'Asset not found' });
    }
    
    // Publish to Kafka
    await publishAssetUpdate('asset.updated', asset);
    
    // Clear cache
    await global.redisClient.del('assets');
    await global.redisClient.del(`customer-assets:${asset.customerId}`);
    await global.redisClient.del(`asset:${asset._id}`);
    
    res.json(asset);
  } catch (error) {
    next(error);
  }
});

// Delete asset (soft delete)
router.delete('/:id', async (req, res, next) => {
  try {
    const asset = await Asset.findOneAndUpdate(
      {
        $or: [
          { assetId: req.params.id },
          { _id: req.params.id }
        ]
      },
      { isActive: false, status: 'WITHDRAWN' },
      { new: true }
    );
    
    if (!asset) {
      return res.status(404).json({ message: 'Asset not found' });
    }
    
    // Publish to Kafka
    await publishAssetUpdate('asset.deleted', asset);
    
    // Clear cache
    await global.redisClient.del('assets');
    await global.redisClient.del(`customer-assets:${asset.customerId}`);
    await global.redisClient.del(`asset:${asset._id}`);
    
    res.json({ message: 'Asset deleted successfully' });
  } catch (error) {
    next(error);
  }
});

// Update asset value
router.patch('/:id/value', async (req, res, next) => {
  try {
    const { currentValue } = req.body;
    
    if (typeof currentValue !== 'number' || currentValue < 0) {
      return res.status(400).json({ message: 'Invalid current value' });
    }
    
    const asset = await Asset.findOneAndUpdate(
      {
        $or: [
          { assetId: req.params.id },
          { _id: req.params.id }
        ]
      },
      { currentValue },
      { new: true }
    );
    
    if (!asset) {
      return res.status(404).json({ message: 'Asset not found' });
    }
    
    // Publish to Kafka
    await publishAssetUpdate('asset.value.updated', asset);
    
    // Clear cache
    await global.redisClient.del('assets');
    await global.redisClient.del(`customer-assets:${asset.customerId}`);
    await global.redisClient.del(`asset:${asset._id}`);
    
    res.json(asset);
  } catch (error) {
    next(error);
  }
});

// Get assets by type
router.get('/type/:assetType', cacheMiddleware('assets-by-type', 300), async (req, res, next) => {
  try {
    const { assetType } = req.params;
    const { customerId, status } = req.query;
    
    const filter = { assetType, isActive: true };
    if (customerId) filter.customerId = customerId;
    if (status) filter.status = status;
    
    const assets = await Asset.find(filter).sort({ createdAt: -1 });
    res.json(assets);
  } catch (error) {
    next(error);
  }
});

// Get assets by risk level
router.get('/risk/:riskLevel', cacheMiddleware('assets-by-risk', 300), async (req, res, next) => {
  try {
    const { riskLevel } = req.params;
    const { customerId, assetType } = req.query;
    
    const filter = { riskLevel, isActive: true };
    if (customerId) filter.customerId = customerId;
    if (assetType) filter.assetType = assetType;
    
    const assets = await Asset.find(filter).sort({ createdAt: -1 });
    res.json(assets);
  } catch (error) {
    next(error);
  }
});

// Get asset statistics
router.get('/stats/overview', cacheMiddleware('asset-stats', 600), async (req, res, next) => {
  try {
    const { customerId } = req.query;
    
    const matchStage = { isActive: true };
    if (customerId) matchStage.customerId = customerId;
    
    const stats = await Asset.aggregate([
      { $match: matchStage },
      {
        $group: {
          _id: null,
          totalAssets: { $sum: 1 },
          totalValue: { $sum: '$currentValue' },
          totalInitialValue: { $sum: '$initialValue' },
          avgInterestRate: { $avg: '$interestRate' },
          avgExpectedReturn: { $avg: '$expectedReturn' },
          assetTypeDistribution: {
            $push: '$assetType'
          },
          riskLevelDistribution: {
            $push: '$riskLevel'
          }
        }
      }
    ]);
    
    if (stats.length === 0) {
      return res.json({
        totalAssets: 0,
        totalValue: 0,
        totalInitialValue: 0,
        totalProfitLoss: 0,
        avgInterestRate: 0,
        avgExpectedReturn: 0,
        assetTypeDistribution: {},
        riskLevelDistribution: {}
      });
    }
    
    const assetTypeDistribution = stats[0].assetTypeDistribution.reduce((acc, type) => {
      acc[type] = (acc[type] || 0) + 1;
      return acc;
    }, {});
    
    const riskLevelDistribution = stats[0].riskLevelDistribution.reduce((acc, level) => {
      acc[level] = (acc[level] || 0) + 1;
      return acc;
    }, {});
    
    res.json({
      totalAssets: stats[0].totalAssets,
      totalValue: stats[0].totalValue,
      totalInitialValue: stats[0].totalInitialValue,
      totalProfitLoss: stats[0].totalValue - stats[0].totalInitialValue,
      avgInterestRate: Math.round(stats[0].avgInterestRate * 100) / 100,
      avgExpectedReturn: Math.round(stats[0].avgExpectedReturn * 100) / 100,
      assetTypeDistribution,
      riskLevelDistribution
    });
  } catch (error) {
    next(error);
  }
});

module.exports = router; 