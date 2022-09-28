DROP TABLE IF EXISTS last_changes_dates; 
DROP TABLE IF EXISTS tt;
DROP TABLE IF EXISTS dates_integers;
DROP TABLE IF EXISTS data;
DROP TABLE IF EXISTS carts;
DROP TABLE IF EXISTS carts_accumulate;
DROP TABLE IF EXISTS carts_lost;

CREATE TABLE last_changes_dates (
  proc_date TEXT,
  roz_date TEXT
);

CREATE TABLE dates_integers (
  date_int INTEGER
);

CREATE TABLE tt (
  division TEXT NOT NULL,  
  region TEXT NOT NULL,  
  city TEXT NOT NULL, 
  div_id INTEGER NOT NULL,
  reg_id INTEGER NOT NULL,
  city_id INTEGER NOT NULL, 
  old_shop INTEGER,     
  shop TEXT UNIQUE NOT NULL,   
  shop_id INTEGER NOT NULL 
);

CREATE TABLE data (
  date_month INTEGER,
  div_id INTEGER,
  reg_id INTEGER,
  city_id INTEGER,
  shop_id INTEGER,
  old_shop INTEGER,    
  sales REAL, 
  sales_carts REAL,   
  checks_qnt REAL,
  checks_carts_qnt REAL,  
  sales_not_bonus REAL,  
  cost_price REAL,
  woff REAL,
  beer_ltr REAL,
  beer_kz_ltr REAL,
  FOREIGN KEY (shop_id) REFERENCES tt (id)  
);

CREATE INDEX IF NOT EXISTS data_date_ind ON data (date_month);
CREATE INDEX IF NOT EXISTS data_old_ind ON data (date_month, old_shop);
CREATE INDEX IF NOT EXISTS data_div_ind ON data (date_month, div_id);
CREATE INDEX IF NOT EXISTS data_reg_ind ON data (date_month, reg_id);
CREATE INDEX IF NOT EXISTS data_city_ind ON data (date_month, city_id);
CREATE INDEX IF NOT EXISTS data_shop_ind ON data (date_month, shop_id);

CREATE TABLE carts (
  date_month INTEGER,
  div_id INTEGER,
  reg_id INTEGER,
  city_id INTEGER,
  shop_id INTEGER,
  old_shop INTEGER,  
  cart INTEGER,
  FOREIGN KEY (shop_id) REFERENCES tt (id)  
);

CREATE INDEX IF NOT EXISTS date_ind ON carts (date_month);
CREATE INDEX IF NOT EXISTS old_ind ON carts (date_month, old_shop);
CREATE INDEX IF NOT EXISTS div_ind ON carts (date_month, div_id);
CREATE INDEX IF NOT EXISTS reg_ind ON carts (date_month, reg_id);
CREATE INDEX IF NOT EXISTS city_ind ON carts (date_month, city_id);
CREATE INDEX IF NOT EXISTS shop_ind ON carts (date_month, shop_id);

CREATE TABLE carts_accumulate (
  date_month INTEGER,
  div_id INTEGER,
  reg_id INTEGER,
  city_id INTEGER,
  shop_id INTEGER,
  old_shop INTEGER,  
  cart INTEGER,
  FOREIGN KEY (shop_id) REFERENCES tt (id)  
);

CREATE INDEX IF NOT EXISTS date_ind_acc ON carts_accumulate (date_month);
CREATE INDEX IF NOT EXISTS old_ind_acc ON carts_accumulate (date_month, old_shop);
CREATE INDEX IF NOT EXISTS div_ind_acc ON carts_accumulate (date_month, div_id);
CREATE INDEX IF NOT EXISTS reg_ind_acc ON carts_accumulate (date_month, reg_id);
CREATE INDEX IF NOT EXISTS city_ind_acc ON carts_accumulate (date_month, city_id);
CREATE INDEX IF NOT EXISTS shop_ind_acc ON carts_accumulate (date_month, shop_id);

CREATE TABLE carts_lost (
  date_month INTEGER,
  div_id INTEGER,
  reg_id INTEGER,
  city_id INTEGER,
  shop_id INTEGER,
  old_shop INTEGER,  
  cart INTEGER,
  FOREIGN KEY (shop_id) REFERENCES tt (id)  
);

CREATE INDEX IF NOT EXISTS date_ind_lost ON carts_accumulate (date_month);
CREATE INDEX IF NOT EXISTS old_ind_lost ON carts_accumulate (date_month, old_shop);
CREATE INDEX IF NOT EXISTS div_ind_lost ON carts_accumulate (date_month, div_id);
CREATE INDEX IF NOT EXISTS reg_ind_lost ON carts_accumulate (date_month, reg_id);
CREATE INDEX IF NOT EXISTS city_ind_lost ON carts_accumulate (date_month, city_id);
CREATE INDEX IF NOT EXISTS shop_ind_lost ON carts_accumulate (date_month, shop_id);

