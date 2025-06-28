const axios = require('axios');

const API_BASE_URL = process.env.API_BASE_URL || 'http://localhost:8000';

// Mock data
const customers = [
  {
    customerId: 'CUST001',
    name: 'Nguyễn Văn An',
    email: 'nguyenvanan@email.com',
    phone: '0901234567',
    riskProfile: 'MEDIUM',
    riskScore: 6,
    investmentGoals: ['SAVINGS', 'RETIREMENT'],
    investmentHorizon: 'MEDIUM_TERM',
    monthlyIncome: 25000000,
    totalAssets: 500000000
  },
  {
    customerId: 'CUST002',
    name: 'Trần Thị Bình',
    email: 'tranthibinh@email.com',
    phone: '0901234568',
    riskProfile: 'LOW',
    riskScore: 3,
    investmentGoals: ['SAVINGS', 'EDUCATION'],
    investmentHorizon: 'LONG_TERM',
    monthlyIncome: 15000000,
    totalAssets: 200000000
  },
  {
    customerId: 'CUST003',
    name: 'Lê Văn Cường',
    email: 'levancuong@email.com',
    phone: '0901234569',
    riskProfile: 'HIGH',
    riskScore: 8,
    investmentGoals: ['BUSINESS', 'REAL_ESTATE'],
    investmentHorizon: 'LONG_TERM',
    monthlyIncome: 50000000,
    totalAssets: 1000000000
  }
];

const assets = [
  // Customer 1 assets
  {
    assetId: 'ASSET001',
    customerId: 'CUST001',
    assetType: 'SAVINGS',
    assetName: 'Tiết kiệm có kỳ hạn 12 tháng',
    currentValue: 200000000,
    initialValue: 200000000,
    currency: 'VND',
    interestRate: 7.5,
    expectedReturn: 7.5,
    maturityDate: '2024-12-31',
    startDate: '2024-01-01',
    riskLevel: 'LOW',
    institution: 'Ngân hàng TMCP',
    accountNumber: '1234567890',
    description: 'Sản phẩm tiết kiệm an toàn'
  },
  {
    assetId: 'ASSET002',
    customerId: 'CUST001',
    assetType: 'FUND',
    assetName: 'Quỹ mở VFMVF1',
    currentValue: 150000000,
    initialValue: 100000000,
    currency: 'VND',
    interestRate: null,
    expectedReturn: 12.0,
    startDate: '2023-06-01',
    riskLevel: 'MEDIUM',
    institution: 'VFM',
    accountNumber: 'FUND001',
    description: 'Quỹ đầu tư cổ phiếu'
  },
  {
    assetId: 'ASSET003',
    customerId: 'CUST001',
    assetType: 'BOND',
    assetName: 'Trái phiếu Chính phủ 5 năm',
    currentValue: 100000000,
    initialValue: 100000000,
    currency: 'VND',
    interestRate: 8.5,
    expectedReturn: 8.5,
    maturityDate: '2029-01-01',
    startDate: '2024-01-01',
    riskLevel: 'LOW',
    institution: 'Bộ Tài chính',
    accountNumber: 'BOND001',
    description: 'Trái phiếu Chính phủ'
  },
  
  // Customer 2 assets
  {
    assetId: 'ASSET004',
    customerId: 'CUST002',
    assetType: 'SAVINGS',
    assetName: 'Tiết kiệm không kỳ hạn',
    currentValue: 100000000,
    initialValue: 100000000,
    currency: 'VND',
    interestRate: 2.5,
    expectedReturn: 2.5,
    startDate: '2024-01-01',
    riskLevel: 'LOW',
    institution: 'Ngân hàng TMCP',
    accountNumber: '1234567891',
    description: 'Tiết kiệm linh hoạt'
  },
  {
    assetId: 'ASSET005',
    customerId: 'CUST002',
    assetType: 'GOLD',
    assetName: 'Vàng SJC',
    currentValue: 80000000,
    initialValue: 75000000,
    currency: 'VND',
    interestRate: null,
    expectedReturn: 6.0,
    startDate: '2023-12-01',
    riskLevel: 'MEDIUM',
    institution: 'SJC',
    accountNumber: 'GOLD001',
    description: 'Đầu tư vàng vật chất'
  },
  
  // Customer 3 assets
  {
    assetId: 'ASSET006',
    customerId: 'CUST003',
    assetType: 'STOCK',
    assetName: 'Cổ phiếu VNM',
    currentValue: 300000000,
    initialValue: 250000000,
    currency: 'VND',
    interestRate: null,
    expectedReturn: 15.0,
    startDate: '2023-01-01',
    riskLevel: 'HIGH',
    institution: 'Vinamilk',
    accountNumber: 'STOCK001',
    description: 'Cổ phiếu Vinamilk'
  },
  {
    assetId: 'ASSET007',
    customerId: 'CUST003',
    assetType: 'FUND',
    assetName: 'Quỹ mở SSI-SCA',
    currentValue: 200000000,
    initialValue: 180000000,
    currency: 'VND',
    interestRate: null,
    expectedReturn: 14.0,
    startDate: '2023-03-01',
    riskLevel: 'HIGH',
    institution: 'SSI',
    accountNumber: 'FUND002',
    description: 'Quỹ đầu tư tăng trưởng'
  },
  {
    assetId: 'ASSET008',
    customerId: 'CUST003',
    assetType: 'REAL_ESTATE',
    assetName: 'Căn hộ chung cư',
    currentValue: 500000000,
    initialValue: 450000000,
    currency: 'VND',
    interestRate: null,
    expectedReturn: 10.0,
    startDate: '2022-06-01',
    riskLevel: 'MEDIUM',
    institution: 'Chủ đầu tư',
    accountNumber: 'RE001',
    description: 'Bất động sản cho thuê'
  }
];

async function createCustomer(customerData) {
  try {
    const response = await axios.post(`${API_BASE_URL}/api/customers`, customerData);
    console.log(`✅ Created customer: ${customerData.name}`);
    return response.data;
  } catch (error) {
    if (error.response?.status === 400 && error.response?.data?.message?.includes('already exists')) {
      console.log(`⚠️  Customer already exists: ${customerData.name}`);
      return null;
    }
    console.error(`❌ Error creating customer ${customerData.name}:`, error.response?.data || error.message);
    return null;
  }
}

async function createAsset(assetData) {
  try {
    const response = await axios.post(`${API_BASE_URL}/api/assets`, assetData);
    console.log(`✅ Created asset: ${assetData.assetName}`);
    return response.data;
  } catch (error) {
    if (error.response?.status === 400 && error.response?.data?.message?.includes('already exists')) {
      console.log(`⚠️  Asset already exists: ${assetData.assetName}`);
      return null;
    }
    console.error(`❌ Error creating asset ${assetData.assetName}:`, error.response?.data || error.message);
    return null;
  }
}

async function initData() {
  console.log('🚀 Starting data initialization...\n');
  
  // Create customers
  console.log('📝 Creating customers...');
  for (const customer of customers) {
    await createCustomer(customer);
  }
  
  console.log('\n📊 Creating assets...');
  // Create assets
  for (const asset of assets) {
    await createAsset(asset);
  }
  
  console.log('\n✅ Data initialization completed!');
  console.log('\n📋 Summary:');
  console.log(`- ${customers.length} customers created`);
  console.log(`- ${assets.length} assets created`);
  console.log('\n🔗 You can now access the application at: http://localhost:3000');
  console.log('📱 Test customer IDs: CUST001, CUST002, CUST003');
}

// Run initialization
if (require.main === module) {
  initData().catch(console.error);
}

module.exports = { initData, customers, assets }; 