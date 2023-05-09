CREATE TABLE IF NOT EXISTS accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    label TEXT NOT NULL,
    bank TEXT,
    is_credit BOOLEAN NOT NULL,
    balance REAL
);

CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,
    method TEXT,
    description TEXT,
    type TEXT,
    category INTEGER,
    subcategory INTEGER,
    debit REAL,
    credit REAL,
    account INT,
    balance REAL,
    FOREIGN KEY (category) REFERENCES categories(id),
    FOREIGN KEY (subcategory) REFERENCES subcategories(id),
    FOREIGN KEY (account) REFERENCES accounts(id)
);

CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    label TEXT
);

CREATE TABLE IF NOT EXISTS subcategories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    label TEXT,
    category INTEGER,
    methods TEXT,
    amounts TEXT,
    desc_flags TEXT,
    FOREIGN KEY (category) REFERENCES categories(id)
);

INSERT INTO categories (label) 
VALUES 
  ('Benefits'),
  ('Banking'),
  ('Friends & Family'),
  ('Debt'),
  ('Bills'),
  ('Home'),
  ('Salary'),
  ('Care'),
  ('Activity'),
  ('Entertainment'),
  ('Food'),
  ('Discretionary'),
  ('Transport'),
  ('Travel & Holidays'),
  ('Transfer'),
  ('Work');