const { v4: uuidv4 } = require("uuid");
const userRepo = require("../persistence-layer/user.repository");
const cacheService = require("../cache-layer/cache.service");

const CACHE_PREFIX = "user";

const userService = {
  async getAllUsers() {
    return cacheService.getOrSet(`${CACHE_PREFIX}:all`, () => userRepo.findAll(), 30);
  },

  async getUserById(id) {
    return cacheService.getOrSet(`${CACHE_PREFIX}:${id}`, () => userRepo.findById(id), 60);
  },

  async createUser({ name, email }) {
    const user = await userRepo.create({ id: uuidv4(), name, email });
    // Invalidate the "all users" cache so the next list fetch is fresh
    await cacheService.del(`${CACHE_PREFIX}:all`);
    return user;
  },

  async updateUser(id, data) {
    const user = await userRepo.update(id, data);
    // Invalidate both the individual and list caches
    await cacheService.del(`${CACHE_PREFIX}:${id}`);
    await cacheService.del(`${CACHE_PREFIX}:all`);
    return user;
  },

  async deleteUser(id) {
    await userRepo.delete(id);
    await cacheService.del(`${CACHE_PREFIX}:${id}`);
    await cacheService.del(`${CACHE_PREFIX}:all`);
  },
};

module.exports = userService;
