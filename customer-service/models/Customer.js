const mongoose = require('mongoose');

const customerSchema = new mongoose.Schema({
  customerId: {
    type: String,
    required: true,
    unique: true,
    index: true
  },
  name: {
    type: String,
    required: true,
    trim: true
  },
  email: {
    type: String,
    required: true,
    unique: true,
    lowercase: true,
    trim: true
  },
  phone: {
    type: String,
    trim: true
  },
  riskProfile: {
    type: String,
    enum: ['LOW', 'MEDIUM', 'HIGH'],
    default: 'MEDIUM'
  },
  riskScore: {
    type: Number,
    min: 1,
    max: 10,
    default: 5
  },
  investmentGoals: [{
    type: String,
    enum: ['SAVINGS', 'RETIREMENT', 'EDUCATION', 'REAL_ESTATE', 'BUSINESS']
  }],
  investmentHorizon: {
    type: String,
    enum: ['SHORT_TERM', 'MEDIUM_TERM', 'LONG_TERM'],
    default: 'MEDIUM_TERM'
  },
  monthlyIncome: {
    type: Number,
    min: 0
  },
  totalAssets: {
    type: Number,
    default: 0
  },
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
customerSchema.index({ email: 1 });
customerSchema.index({ riskProfile: 1 });
customerSchema.index({ isActive: 1 });

// Pre-save middleware
customerSchema.pre('save', function(next) {
  this.updatedAt = new Date();
  next();
});

// Static methods
customerSchema.statics.findByRiskProfile = function(riskProfile) {
  return this.find({ riskProfile, isActive: true });
};

customerSchema.statics.findActiveCustomers = function() {
  return this.find({ isActive: true });
};

// Instance methods
customerSchema.methods.updateRiskProfile = function(newRiskProfile) {
  this.riskProfile = newRiskProfile;
  return this.save();
};

customerSchema.methods.getRiskLevel = function() {
  const riskLevels = {
    LOW: { min: 1, max: 3, label: 'Thấp' },
    MEDIUM: { min: 4, max: 7, label: 'Trung bình' },
    HIGH: { min: 8, max: 10, label: 'Cao' }
  };
  
  return riskLevels[this.riskProfile] || riskLevels.MEDIUM;
};

module.exports = mongoose.model('Customer', customerSchema); 