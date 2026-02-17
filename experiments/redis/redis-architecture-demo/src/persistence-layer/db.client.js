const initSqlJs = require("sql.js");
const fs = require("fs");
const path = require("path");

const DB_PATH = path.join(__dirname, "../../data.db");

let db = null;

/**
 * Convert sql.js result format [{columns, values}] to array of plain objects.
 * sql.js returns: [{ columns: ["id","name"], values: [["1","Alice"],["2","Bob"]] }]
 * We want:        [{ id: "1", name: "Alice" }, { id: "2", name: "Bob" }]
 */
function toObjects(result) {
  if (!result || result.length === 0) return [];
  const { columns, values } = result[0];
  return values.map((row) =>
    Object.fromEntries(columns.map((col, i) => [col, row[i]]))
  );
}

/**
 * Get a single object from a query result, or null.
 */
function toObject(result) {
  const rows = toObjects(result);
  return rows.length > 0 ? rows[0] : null;
}

/**
 * Persist the in-memory DB to disk.
 */
function save() {
  if (!db) return;
  const data = db.export();
  fs.writeFileSync(DB_PATH, Buffer.from(data));
}

/**
 * Initialize the database (async because sql.js loads WASM).
 * Returns the db instance. Safe to call multiple times — returns cached instance.
 */
async function getDb() {
  if (db) return db;

  const SQL = await initSqlJs();

  // Load existing DB file if present, otherwise create new
  if (fs.existsSync(DB_PATH)) {
    const fileBuffer = fs.readFileSync(DB_PATH);
    db = new SQL.Database(fileBuffer);
  } else {
    db = new SQL.Database();
  }

  // Bootstrap schema
  db.run(`
    CREATE TABLE IF NOT EXISTS users (
      id    TEXT PRIMARY KEY,
      name  TEXT NOT NULL,
      email TEXT NOT NULL UNIQUE,
      created_at TEXT DEFAULT (datetime('now'))
    )
  `);
  db.run(`
    CREATE TABLE IF NOT EXISTS metrics (
      id         INTEGER PRIMARY KEY AUTOINCREMENT,
      event_name TEXT NOT NULL,
      payload    TEXT,
      created_at TEXT DEFAULT (datetime('now'))
    )
  `);

  save();
  return db;
}

module.exports = { getDb, toObjects, toObject, save };
