DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS stock;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL,
  admin BOOLEAN NOT NUll
);

CREATE TABLE stock (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  supplier_code TEXT,
  tidings_code TEXT,
  supplier TEXT NOT NULL,
  location TEXT NOT NULL,
  quantity INTEGER CHECK(TYPEOF(quantity) = 'integer') NOT NULL,
  last_modified TEXT NOT NULL
);
