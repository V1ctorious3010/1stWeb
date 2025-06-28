const mongoose = require('mongoose');

const assetSchema = new mongoose.Schema({
  assetId: {
    type: String,
    required: true,
    unique: true,
    index: true
  },
  customerId: {
    type: String,
    required: true,
    index: true
  },
  assetType: {
    type: String,
    enum: ['SAVINGS', 'FUND', 'STOCK', 'BOND', 'REAL_ESTATE', 'GOLD'],
    required: true
  },
  assetName: {
    type: String,
    required: true,
    trim: true
  },
  currentValue: {
    type: Number,
    required: true,
    min: 0
  },
  initialValue: {
    type: Number,
    required: true,
    min: 0
  },
  currency: {
    type: String,
    default: 'VND',
    enum: ['VND', 'USD', 'EUR']
  },
  interestRate: {
    type: Number,
    min: 0,
    max: 100
  },
  expectedReturn: {
    type: Number,
    min: -100,
    max: 100
  },
  maturityDate: {
    type: Date
  },
  startDate: {
    type: Date,
    required: true
  },
  endDate: {
    type: Date
  },
  status: {
    type: String,
    enum: ['ACTIVE', 'MATURED', 'WITHDRAWN', 'SUSPENDED'],
    default: 'ACTIVE'
  },
  riskLevel: {
    type: String,
    enum: ['LOW', 'MEDIUM', 'HIGH'],
    required: true
  },
  institution: {
    type: String,
    trim: true
  },
  accountNumber: {
    type: String,
    trim: true
  },
  description: {
    type: String,
    trim: true
  },
  tags: [{
    type: String,
    trim: true
  }],
  isActive: {
    type: Boolean,
    default: true
  },
  createdAt: {
    type: Date,
    default: Date.now
  },
  updatedAt: {
    type: Date,
    default: Date.now
  }
}, {
  timestamps: true
});

// Indexes
assetSchema.index({ customerId: 1, assetType: 1 });
assetSchema.index({ assetType: 1, status: 1 });
assetSchema.index({ riskLevel: 1 });
assetSchema.index({ maturityDate: 1 });
assetSchema.index({ isActive: 1 });

// Virtual for profit/loss
assetSchema.virtual('profitLoss').get(function() {
  return this.currentValue - this.initialValue;
});

// Virtual for profit/loss percentage
assetSchema.virtual('profitLossPercentage').get(function() {
  if (this.initialValue === 0) return 0;
  return ((this.currentValue - this.initialValue) / this.initialValue) * 100;
});

// Virtual for days to maturity
assetSchema.virtual('daysToMaturity').get(function() {
  if (!this.maturityDate) return null;
  const today = new Date();
  const maturity = new Date(this.maturityDate);
  const diffTime = maturity - today;
  return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
});

// Pre-save middleware
assetSchema.pre('save', function(next) {
  this.updatedAt = new Date();
  next();
});

// Static methods
assetSchema.statics.findByCustomer = function(customerId) {
  return this.find({ customerId, isActive: true }).sort({ createdAt: -1 });
};

assetSchema.statics.findByType = function(assetType) {
  return this.find({ assetType, isActive: true });
};

assetSchema.statics.findByRiskLevel = function(riskLevel) {
  return this.find({ riskLevel, isActive: true });
};

assetSchema.statics.getTotalValueByCustomer = function(customerId) {
  return this.aggregate([
    { $match: { customerId, isActive: true, status: 'ACTIVE' } },
    { $group: { _id: null, totalValue: { $sum: '$currentValue' } } }
  ]);
};

// Instance methods
assetSchema.methods.calculateProfitLoss = function() {
  return {
    absolute: this.currentValue - this.initialValue,
    percentage: this.initialValue > 0 ? ((this.currentValue - this.initialValue) / this.initialValue) * 100 : 0
  };
};

assetSchema.methods.isMatured = function() {
  if (!this.maturityDate) return false;
  return new Date() >= new Date(this.maturityDate);
};

assetSchema.methods.updateValue = function(newValue) {
  this.currentValue = newValue;
  return this.save();
};

// Ensure virtual fields are serialized
assetSchema.set('toJSON', { virtuals: true });
assetSchema.set('toObject', { virtuals: true });

module.exports = mongoose.model('Asset', assetSchema); 