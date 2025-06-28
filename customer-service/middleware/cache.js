const cacheMiddleware = (key, ttl = 300) => {
  return async (req, res, next) => {
    try {
      const cacheKey = `${key}:${JSON.stringify(req.query)}`;
      const cachedData = await global.redisClient.get(cacheKey);
      
      if (cachedData) {
        return res.json(JSON.parse(cachedData));
      }
      
      // Store original send method
      const originalSend = res.json;
      
      // Override send method to cache response
      res.json = function(data) {
        global.redisClient.setEx(cacheKey, ttl, JSON.stringify(data))
          .catch(err => console.error('Cache set error:', err));
        
        return originalSend.call(this, data);
      };
      
      next();
    } catch (error) {
      console.error('Cache middleware error:', error);
      next();
    }
  };
};

module.exports = {
  cacheMiddleware
}; 