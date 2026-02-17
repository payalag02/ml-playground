const { getDb, toObjects, save } = require("./db.client");

const metricsRepo = {
  async record(eventName, payload = {}) {
    const db = await getDb();
    db.run("INSERT INTO metrics (event_name, payload) VALUES (?, ?)", [
      eventName,
      JSON.stringify(payload),
    ]);
    save();
  },

  async getByEvent(eventName, limit = 50) {
    const db = await getDb();
    const stmt = db.prepare(
      "SELECT * FROM metrics WHERE event_name = ? ORDER BY created_at DESC LIMIT ?"
    );
    stmt.bind([eventName, limit]);
    const rows = [];
    while (stmt.step()) rows.push(stmt.getAsObject());
    stmt.free();
    return rows;
  },

  async getAll(limit = 100) {
    const db = await getDb();
    const stmt = db.prepare("SELECT * FROM metrics ORDER BY created_at DESC LIMIT ?");
    stmt.bind([limit]);
    const rows = [];
    while (stmt.step()) rows.push(stmt.getAsObject());
    stmt.free();
    return rows;
  },

  async countByEvent() {
    const db = await getDb();
    return toObjects(
      db.exec("SELECT event_name, COUNT(*) as count FROM metrics GROUP BY event_name ORDER BY count DESC")
    );
  },
};

module.exports = metricsRepo;
