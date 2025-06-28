const Joi = require('joi');

const customerSchema = Joi.object({
  customerId: Joi.string().required().min(3).max(50),
  name: Joi.string().required().min(2).max(100),
  email: Joi.string().email().required(),
  phone: Joi.string().pattern(/^[0-9+\-\s()]+$/).optional(),
  riskProfile: Joi.string().valid('LOW', 'MEDIUM', 'HIGH').default('MEDIUM'),
  riskScore: Joi.number().min(1).max(10).default(5),
  investmentGoals: Joi.array().items(
    Joi.string().valid('SAVINGS', 'RETIREMENT', 'EDUCATION', 'REAL_ESTATE', 'BUSINESS')
  ).optional(),
  investmentHorizon: Joi.string().valid('SHORT_TERM', 'MEDIUM_TERM', 'LONG_TERM').default('MEDIUM_TERM'),
  monthlyIncome: Joi.number().min(0).optional(),
  totalAssets: Joi.number().min(0).default(0),
  isActive: Joi.boolean().default(true)
});

const updateCustomerSchema = Joi.object({
  name: Joi.string().min(2).max(100).optional(),
  email: Joi.string().email().optional(),
  phone: Joi.string().pattern(/^[0-9+\-\s()]+$/).optional(),
  riskProfile: Joi.string().valid('LOW', 'MEDIUM', 'HIGH').optional(),
  riskScore: Joi.number().min(1).max(10).optional(),
  investmentGoals: Joi.array().items(
    Joi.string().valid('SAVINGS', 'RETIREMENT', 'EDUCATION', 'REAL_ESTATE', 'BUSINESS')
  ).optional(),
  investmentHorizon: Joi.string().valid('SHORT_TERM', 'MEDIUM_TERM', 'LONG_TERM').optional(),
  monthlyIncome: Joi.number().min(0).optional(),
  totalAssets: Joi.number().min(0).optional(),
  isActive: Joi.boolean().optional()
});

const validateCustomer = (req, res, next) => {
  const { error } = customerSchema.validate(req.body);
  if (error) {
    return res.status(400).json({
      message: 'Validation error',
      details: error.details.map(detail => detail.message)
    });
  }
  next();
};

const validateUpdateCustomer = (req, res, next) => {
  const { error } = updateCustomerSchema.validate(req.body);
  if (error) {
    return res.status(400).json({
      message: 'Validation error',
      details: error.details.map(detail => detail.message)
    });
  }
  next();
};

module.exports = {
  validateCustomer,
  validateUpdateCustomer
}; 
 