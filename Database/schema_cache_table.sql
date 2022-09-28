DROP TABLE IF EXISTS table_cache;

CREATE TABLE table_cache ( 
  begin_int INTEGER,
  end_int INTEGER,
  attr_columns TEXT,
  divs TEXT,
  regs TEXT,
  cities TEXT,
  shops TEXT,
  old_shop INTEGER,    
  mark_argument TEXT,
  attr_values TEXT,   
  value REAL
);