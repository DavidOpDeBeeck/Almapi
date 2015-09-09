-- -----------------------------------------------------
-- Table ALMA
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS ALMA (
  'alma_id' INTEGER PRIMARY KEY,
  'name'    VARCHAR(45) NOT NULL UNIQUE
);


-- -----------------------------------------------------
-- Table OPTION
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS OPTION (
  'option_id'  INTEGER PRIMARY KEY,
  'name'       VARCHAR(45) NOT NULL UNIQUE,
  'vegetarian' TINYINT(1)  NOT NULL
);


-- -----------------------------------------------------
-- Table MENU
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS 'MENU' (
  'menu_id' INTEGER PRIMARY KEY,
  'alma_id' INTEGER  NOT NULL,
  'date'    DATETIME NOT NULL,
  CONSTRAINT 'fk_MENU_ALMA'
  FOREIGN KEY ('alma_id')
  REFERENCES 'ALMA' ('alma_id')
  ON DELETE NO ACTION
  ON UPDATE NO ACTION
);


-- -----------------------------------------------------
-- Table COURSE
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS 'COURSE' (
  'course_id' INTEGER PRIMARY KEY,
  'name'      VARCHAR(45) NOT NULL
);


-- -----------------------------------------------------
-- Table MENU_has_OPTION
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS 'MENU_has_OPTION' (
  'menu_id'   INTEGER NOT NULL,
  'option_id' INTEGER NOT NULL,
  'course_id' INTEGER NOT NULL,
  'price'     FLOAT   NOT NULL,
  PRIMARY KEY ('menu_id', 'option_id', 'course_id'),
  CONSTRAINT 'fk_MENU_has_OPTION_MENU1'
  FOREIGN KEY ('menu_id')
  REFERENCES 'MENU' ('menu_id')
  ON DELETE NO ACTION
  ON UPDATE NO ACTION,
  CONSTRAINT 'fk_MENU_has_OPTION_OPTION1'
  FOREIGN KEY ('option_id')
  REFERENCES 'OPTION' ('option_id')
  ON DELETE NO ACTION
  ON UPDATE NO ACTION,
  CONSTRAINT 'fk_MENU_has_OPTION_COURSE1'
  FOREIGN KEY ('course_id')
  REFERENCES 'COURSE' ('course_id')
  ON DELETE NO ACTION
  ON UPDATE NO ACTION
);
