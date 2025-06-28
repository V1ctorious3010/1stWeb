const express = require('express');
const router = express.Router();
const Customer = require('../models/Customer');
const { validateCustomer } = require('../middleware/validation');
const { cacheMiddleware } = require('../middleware/cache');

// Get all customers
router.get('/', cacheMiddleware('customers', 300), async (req, res, next) => {
  try {
    const { page = 1, limit = 10, riskProfile, isActive } = req.query;
    
    const filter = {};
    if (riskProfile) filter.riskProfile = riskProfile;
    if (isActive !== undefined) filter.isActive = isActive === 'true';
    
    const customers = await Customer.find(filter)
      .limit(limit * 1)
      .skip((page - 1) * limit)
      .sort({ createdAt: -1 });
    
    const total = await Customer.countDocuments(filter);
    
    res.json({
      customers,
      totalPages: Math.ceil(total / limit),
      currentPage: page,
      total
    });
  } catch (error) {
    next(error);
  }
});

// Get customer by ID
router.get('/:id', cacheMiddleware('customer', 300), async (req, res, next) => {
  try {
    const customer = await Customer.findOne({
      $or: [
        { customerId: req.params.id },
        { _id: req.params.id }
      ]
    });
    
    if (!customer) {
      return res.status(404).json({ message: 'Customer not found' });
    }
    
    res.json(customer);
  } catch (error) {
    next(error);
  }
});

// Create new customer
router.post('/', validateCustomer, async (req, res, next) => {
  try {
    const customer = new Customer(req.body);
    await customer.save();
    
    // Clear cache
    await global.redisClient.del('customers');
    
    res.status(201).json(customer);
  } catch (error) {
    if (error.code === 11000) {
      return res.status(400).json({ 
        message: 'Customer with this email or customerId already exists' 
      });
    }
    next(error);
  }
});

// Update customer
router.put('/:id', validateCustomer, async (req, res, next) => {
  try {
    const customer = await Customer.findOneAndUpdate(
      {
        $or: [
          { customerId: req.params.id },
          { _id: req.params.id }
        ]
      },
      req.body,
      { new: true, runValidators: true }
    );
    
    if (!customer) {
      return res.status(404).json({ message: 'Customer not found' });
    }
    
    // Clear cache
    await global.redisClient.del('customers');
    await global.redisClient.del(`customer:${customer._id}`);
    
    res.json(customer);
  } catch (error) {
    next(error);
  }
});

// Delete customer (soft delete)
router.delete('/:id', async (req, res, next) => {
  try {
    const customer = await Customer.findOneAndUpdate(
      {
        $or: [
          { customerId: req.params.id },
          { _id: req.params.id }
        ]
      },
      { isActive: false },
      { new: true }
    );
    
    if (!customer) {
      return res.status(404).json({ message: 'Customer not found' });
    }
    
    // Clear cache
    await global.redisClient.del('customers');
    await global.redisClient.del(`customer:${customer._id}`);
    
    res.json({ message: 'Customer deactivated successfully' });
  } catch (error) {
    next(error);
  }
});

// Get customers by risk profile
router.get('/risk-profile/:profile', cacheMiddleware('risk-profile', 300), async (req, res, next) => {
  try {
    const { profile } = req.params;
    const customers = await Customer.findByRiskProfile(profile);
    res.json(customers);
  } catch (error) {
    next(error);
  }
});

// Update customer risk profile
router.patch('/:id/risk-profile', async (req, res, next) => {
  try {
    const { riskProfile, riskScore } = req.body;
    
    if (!riskProfile || !['LOW', 'MEDIUM', 'HIGH'].includes(riskProfile)) {
      return res.status(400).json({ message: 'Invalid risk profile' });
    }
    
    const customer = await Customer.findOneAndUpdate(
      {
        $or: [
          { customerId: req.params.id },
          { _id: req.params.id }
        ]
      },
      { 
        riskProfile,
        riskScore: riskScore || 5
      },
      { new: true }
    );
    
    if (!customer) {
      return res.status(404).json({ message: 'Customer not found' });
    }
    
    // Clear cache
    await global.redisClient.del('customers');
    await global.redisClient.del(`customer:${customer._id}`);
    await global.redisClient.del(`risk-profile:${riskProfile}`);
    
    res.json(customer);
  } catch (error) {
    next(error);
  }
});

// Get customer statistics
router.get('/stats/overview', cacheMiddleware('stats', 600), async (req, res, next) => {
  try {
    const stats = await Customer.aggregate([
      { $match: { isActive: true } },
      {
        $group: {
          _id: null,
          totalCustomers: { $sum: 1 },
          avgRiskScore: { $avg: '$riskScore' },
          totalAssets: { $sum: '$totalAssets' },
          riskProfileDistribution: {
            $push: '$riskProfile'
          }
        }
      }
    ]);
    
    if (stats.length === 0) {
      return res.json({
        totalCustomers: 0,
        avgRiskScore: 0,
        totalAssets: 0,
        riskProfileDistribution: {}
      });
    }
    
    const riskDistribution = stats[0].riskProfileDistribution.reduce((acc, profile) => {
      acc[profile] = (acc[profile] || 0) + 1;
      return acc;
    }, {});
    
    res.json({
      totalCustomers: stats[0].totalCustomers,
      avgRiskScore: Math.round(stats[0].avgRiskScore * 100) / 100,
      totalAssets: stats[0].totalAssets,
      riskProfileDistribution: riskDistribution
    });
  } catch (error) {
    next(error);
  }
});

module.exports = router; 