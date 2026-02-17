const userService = require("../../domain/user.service");

const userController = {
  async list(req, res) {
    const users = await userService.getAllUsers();
    res.json(users);
  },

  async getById(req, res) {
    const user = await userService.getUserById(req.params.id);
    if (!user) return res.status(404).json({ error: "User not found" });
    res.json(user);
  },

  async create(req, res) {
    const { name, email } = req.body;
    if (!name || !email) {
      return res.status(400).json({ error: "name and email are required" });
    }
    const user = await userService.createUser({ name, email });
    res.status(201).json(user);
  },

  async update(req, res) {
    const user = await userService.updateUser(req.params.id, req.body);
    if (!user) return res.status(404).json({ error: "User not found" });
    res.json(user);
  },

  async remove(req, res) {
    await userService.deleteUser(req.params.id);
    res.status(204).end();
  },
};

module.exports = userController;
