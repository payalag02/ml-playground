const { getDb, toObjects, toObject, save } = require("./db.client");

const userRepo = {
  async findAll() {
    const db = await getDb();
    return toObjects(db.exec("SELECT * FROM users ORDER BY created_at DESC"));
  },

  async findById(id) {
    const db = await getDb();
    const stmt = db.prepare("SELECT * FROM users WHERE id = ?");
    stmt.bind([id]);
    const rows = [];
    while (stmt.step()) rows.push(stmt.getAsObject());
    stmt.free();
    return rows.length > 0 ? rows[0] : null;
  },

  async create({ id, name, email }) {
    const db = await getDb();
    db.run("INSERT INTO users (id, name, email) VALUES (?, ?, ?)", [id, name, email]);
    save();
    return this.findById(id);
  },

  async update(id, { name, email }) {
    const fields = [];
    const values = [];
    if (name) { fields.push("name = ?"); values.push(name); }
    if (email) { fields.push("email = ?"); values.push(email); }
    if (fields.length === 0) return this.findById(id);

    values.push(id);
    const db = await getDb();
    db.run(`UPDATE users SET ${fields.join(", ")} WHERE id = ?`, values);
    save();
    return this.findById(id);
  },

  async delete(id) {
    const db = await getDb();
    db.run("DELETE FROM users WHERE id = ?", [id]);
    save();
  },
};

module.exports = userRepo;
