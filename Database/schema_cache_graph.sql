DROP TABLE IF EXISTS graph_cache;

CREATE TABLE graph_cache ( 
  date_month INTEGER, 
  divs TEXT,
  regs TEXT,
  cities TEXT,
  shops TEXT,
  old_shop INTEGER,   
  mark_argument TEXT,   
  value REAL
);