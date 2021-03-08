/*

WARNING: RUNNING THIS WILL CLEAR THE DATABASE OF ANY DATA.

*/
DROP TABLE IF EXISTS price;
DROP TABLE IF EXISTS servo;
DROP TABLE IF EXISTS suburb;
DROP TABLE IF EXISTS surrounding;
DROP TABLE IF EXISTS fuel_type;
DROP TABLE IF EXISTS brand;
DROP TABLE IF EXISTS region;
DROP TABLE IF EXISTS state_region;

CREATE TABLE state_region(
    state_region_id         INTEGER PRIMARY KEY NOT NULL UNIQUE,
    state_region_name       VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE region(
    region_id               INTEGER PRIMARY KEY NOT NULL UNIQUE,
    region_name             VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE brand(
    brand_id               INTEGER PRIMARY KEY NOT NULL UNIQUE,
    brand_name             VARCHAR(100)
);

CREATE TABLE fuel_type(
    fuel_id                 INTEGER PRIMARY KEY NOT NULL UNIQUE,
    fuel_name               VARCHAR(100) NOT NULL UNIQUE
);

/*
    Associates a suburb with another, indicating it is a surrounding suburb.
    https://stackoverflow.com/questions/18603372/how-to-make-sql-many-to-many-same-type-relationship-table

    sqlite> select n.suburb_name from suburb s inner join surrounding r on s.suburb_id=r.suburb_id inner join suburb n on r.neighbour_id=n.suburb_id  where s.suburb_id=198;
*/
CREATE TABLE surrounding(
    surrounding_id          INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
    suburb_id               INTEGER NOT NULL,
    neighbour_id            INTEGER NOT NULL,
    FOREIGN KEY(suburb_id) REFERENCES suburb(suburb_id) ON DELETE CASCADE,
    FOREIGN KEY(neighbour_id) REFERENCES suburb(suburb_id) ON DELETE CASCADE
);

/*
    All suburbs are part of a WA state regions as outlined here: http://www.drd.wa.gov.au/regions/Pages/default.aspx
    Some suburbs may be part of town or shire region e.g. North Metro
*/
CREATE TABLE suburb(
    suburb_id               INTEGER PRIMARY KEY NOT NULL UNIQUE,
    suburb_name             VARCHAR(100) NOT NULL UNIQUE,
    region_id               INTEGER,
    state_region_id         INTEGER NOT NULL,
    FOREIGN KEY(region_id) REFERENCES region(region_id) ON DELETE CASCADE,
    FOREIGN KEY(state_region_id) REFERENCES state_region(state_region_id) ON DELETE CASCADE
);

CREATE TABLE servo(
    servo_id                INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
    servo_name              VARCHAR(100) NOT NULL UNIQUE,
    servo_address           VARCHAR(255) UNIQUE,
    servo_phone             VARCHAR(100),
    suburb_id               INTEGER NOT NULL,
    latitude                REAL NOT NULL,
    longitude               REAL NOT NULL,
    brand_id                VARCHAR(100),
    feature_24h             BOOLEAN,
    feature_unmanned        BOOLEAN,
    feature_drivewaysvc     VARCHAR(100),
    feature_other           VARCHAR(255),
    FOREIGN KEY(brand_id) REFERENCES brand(brand_id) ON DELETE CASCADE,
    FOREIGN KEY(suburb_id) REFERENCES suburb(suburb_id) ON DELETE CASCADE
);

CREATE TABLE price(
    price_id                INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
    price_date              DATE NOT NULL,
    price                   REAL NOT NULL,
    fuel_id                 INTEGER NOT NULL,
    servo_id                INTEGER NOT NULL,
    FOREIGN KEY(fuel_id) REFERENCES fuel_type(fuel_id) ON DELETE CASCADE,
    FOREIGN KEY(servo_id) REFERENCES servo(servo_id) ON DELETE CASCADE
    UNIQUE(price_date,price,fuel_id,servo_id)
);