const Joi = require('joi');

const assetSchema = Joi.object({
  assetId: Joi.string().required().min(3).max(50),
  customerId: Joi.string().required(),
  assetType: Joi.string().valid('SAVINGS', 'FUND', 'STOCK', 'BOND', 'REAL_ESTATE', 'GOLD').required(),
  assetName: Joi.string().required().min(2).max(200),
  currentValue: Joi.number().min(0).required(),
  initialValue: Joi.number().min(0).required(),
  currency: Joi.string().valid('VND', 'USD', 'EUR').default('VND'),
  interestRate: Joi.number().min(0).max(100).optional(),
  expectedReturn: Joi.number().min(-100).max(100).optional(),
  maturityDate: Joi.date().optional(),
  startDate: Joi.date().required(),
  endDate: Joi.date().optional(),
  status: Joi.string().valid('ACTIVE', 'MATURED', 'WITHDRAWN', 'SUSPENDED').default('ACTIVE'),
  riskLevel: Joi.string().valid('LOW', 'MEDIUM', 'HIGH').required(),
  institution: Joi.string().optional(),
  accountNumber: Joi.string().optional(),
  description: Joi.string().optional(),
  tags: Joi.array().items(Joi.string()).optional(),
  isActive: Joi.boolean().default(true)
});

const updateAssetSchema = Joi.object({
  assetName: Joi.string().min(2).max(200).optional(),
  currentValue: Joi.number().min(0).optional(),
  initialValue: Joi.number().min(0).optional(),
  currency: Joi.string().valid('VND', 'USD', 'EUR').optional(),
  interestRate: Joi.number().min(0).max(100).optional(),
  expectedReturn: Joi.number().min(-100).max(100).optional(),
  maturityDate: Joi.date().optional(),
  startDate: Joi.date().optional(),
  endDate: Joi.date().optional(),
  status: Joi.string().valid('ACTIVE', 'MATURED', 'WITHDRAWN', 'SUSPENDED').optional(),
  riskLevel: Joi.string().valid('LOW', 'MEDIUM', 'HIGH').optional(),
  institution: Joi.string().optional(),
  accountNumber: Joi.string().optional(),
  description: Joi.string().optional(),
  tags: Joi.array().items(Joi.string()).optional(),
  isActive: Joi.boolean().optional()
});

const validateAsset = (req, res, next) => {
  const { error } = assetSchema.validate(req.body);
  if (error) {
    return res.status(400).json({
      message: 'Validation error',
      details: error.details.map(detail => detail.message)
    });
  }
  next();
};

const validateUpdateAsset = (req, res, next) => {
  const { error } = updateAssetSchema.validate(req.body);
  if (error) {
    return res.status(400).json({
      message: 'Validation error',
      details: error.details.map(detail => detail.message)
    });
  }
  next();
};

module.exports = {
  validateAsset,
  validateUpdateAsset
}; 