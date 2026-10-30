CREATE DATABASE IF NOT EXISTS solar_monitoring
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;
USE solar_monitoring;

DROP TABLE IF EXISTS energy_sales;
DROP TABLE IF EXISTS battery_charge_log;
DROP TABLE IF EXISTS panel_tilt_log;
DROP TABLE IF EXISTS panel_hourly_generation;
DROP TABLE IF EXISTS batteries;
DROP TABLE IF EXISTS panels;
DROP TABLE IF EXISTS station_owners;
DROP TABLE IF EXISTS stations;
DROP TABLE IF EXISTS battery_types;
DROP TABLE IF EXISTS panel_types;
DROP TABLE IF EXISTS owners;
DROP TABLE IF EXISTS energy_prices;
DROP TABLE IF EXISTS addresses;

CREATE TABLE addresses (
    address_id      INT AUTO_INCREMENT PRIMARY KEY,
    country         VARCHAR(100) NOT NULL,
    region          VARCHAR(100) NOT NULL,
    city            VARCHAR(100) NOT NULL,
    street          VARCHAR(150) NOT NULL,
    building_number VARCHAR(20)  NOT NULL,
    postal_code     VARCHAR(20),
    latitude        DECIMAL(9,6),
    longitude       DECIMAL(9,6)
) ENGINE = InnoDB;

CREATE TABLE owners (
    owner_id    INT AUTO_INCREMENT PRIMARY KEY,
    first_name  VARCHAR(100) NOT NULL,
    last_name   VARCHAR(100) NOT NULL,
    phone       VARCHAR(20)  NOT NULL,
    email       VARCHAR(150),
    passport_no VARCHAR(30),
    UNIQUE KEY uq_owner_phone (phone),
    UNIQUE KEY uq_owner_email (email),
    UNIQUE KEY uq_owner_passport (passport_no)
) ENGINE = InnoDB;

CREATE TABLE panel_types (
    panel_type_id   INT AUTO_INCREMENT PRIMARY KEY,
    manufacturer    VARCHAR(100) NOT NULL,
    model           VARCHAR(100) NOT NULL,
    nominal_power_w INT NOT NULL,
    is_adjustable   BOOLEAN NOT NULL DEFAULT FALSE,
    warranty_years  TINYINT NOT NULL,
    UNIQUE KEY uq_panel_model (manufacturer, model)
) ENGINE = InnoDB;

CREATE TABLE battery_types (
    battery_type_id INT AUTO_INCREMENT PRIMARY KEY,
    manufacturer    VARCHAR(100) NOT NULL,
    model           VARCHAR(100) NOT NULL,
    capacity_kwh    DECIMAL(6,2) NOT NULL,
    cycle_life      INT NOT NULL,
    warranty_years  TINYINT NOT NULL,
    UNIQUE KEY uq_battery_model (manufacturer, model)
) ENGINE = InnoDB;

CREATE TABLE energy_prices (
    price_id       BIGINT AUTO_INCREMENT PRIMARY KEY,
    price_datetime DATETIME NOT NULL,
    price_per_kwh  DECIMAL(8,4) NOT NULL,
    UNIQUE KEY uq_price_datetime (price_datetime)
) ENGINE = InnoDB;

CREATE TABLE stations (
    station_id         INT AUTO_INCREMENT PRIMARY KEY,
    address_id         INT NOT NULL,
    station_name       VARCHAR(150) NOT NULL,
    installation_date  DATE NOT NULL,
    grid_connection_id VARCHAR(50),
    status             ENUM('active','inactive','maintenance') NOT NULL DEFAULT 'active',
    UNIQUE KEY uq_station_grid_id (grid_connection_id),
    CONSTRAINT fk_station_address
        FOREIGN KEY (address_id) REFERENCES addresses(address_id)
        ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE = InnoDB;

CREATE TABLE station_owners (
    station_id      INT NOT NULL,
    owner_id        INT NOT NULL,
    ownership_share DECIMAL(5,2) NOT NULL DEFAULT 100.00,
    since_date      DATE NOT NULL,
    PRIMARY KEY (station_id, owner_id),
    CONSTRAINT fk_so_station FOREIGN KEY (station_id) REFERENCES stations(station_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_so_owner FOREIGN KEY (owner_id) REFERENCES owners(owner_id)
        ON DELETE CASCADE,
    CONSTRAINT chk_ownership_share CHECK (ownership_share > 0 AND ownership_share <= 100)
) ENGINE = InnoDB;

CREATE TABLE panels (
    panel_id           INT AUTO_INCREMENT PRIMARY KEY,
    station_id         INT NOT NULL,
    panel_type_id      INT NOT NULL,
    serial_number      VARCHAR(50) NOT NULL,
    installation_date  DATE NOT NULL,
    decommission_date  DATE NULL,
    current_tilt_angle DECIMAL(4,1) NOT NULL DEFAULT 30.0,
    UNIQUE KEY uq_panel_serial (serial_number),
    CONSTRAINT fk_panel_station FOREIGN KEY (station_id) REFERENCES stations(station_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_panel_type FOREIGN KEY (panel_type_id) REFERENCES panel_types(panel_type_id)
        ON DELETE RESTRICT
) ENGINE = InnoDB;

CREATE TABLE batteries (
    battery_id        INT AUTO_INCREMENT PRIMARY KEY,
    station_id        INT NOT NULL,
    battery_type_id   INT NOT NULL,
    serial_number     VARCHAR(50) NOT NULL,
    installation_date DATE NOT NULL,
    decommission_date DATE NULL,
    UNIQUE KEY uq_battery_serial (serial_number),
    CONSTRAINT fk_battery_station FOREIGN KEY (station_id) REFERENCES stations(station_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_battery_type FOREIGN KEY (battery_type_id) REFERENCES battery_types(battery_type_id)
        ON DELETE RESTRICT
) ENGINE = InnoDB;

CREATE TABLE panel_hourly_generation (
    generation_id    BIGINT AUTO_INCREMENT PRIMARY KEY,
    panel_id         INT NOT NULL,
    reading_datetime DATETIME NOT NULL,
    generated_kwh    DECIMAL(6,3) NOT NULL,
    UNIQUE KEY uq_panel_hour (panel_id, reading_datetime),
    CONSTRAINT fk_gen_panel FOREIGN KEY (panel_id) REFERENCES panels(panel_id)
        ON DELETE CASCADE
) ENGINE = InnoDB;

CREATE TABLE panel_tilt_log (
    tilt_log_id     BIGINT AUTO_INCREMENT PRIMARY KEY,
    panel_id        INT NOT NULL,
    change_datetime DATETIME NOT NULL,
    tilt_angle      DECIMAL(4,1) NOT NULL,
    UNIQUE KEY uq_panel_tilt_time (panel_id, change_datetime),
    CONSTRAINT fk_tilt_panel FOREIGN KEY (panel_id) REFERENCES panels(panel_id)
        ON DELETE CASCADE
) ENGINE = InnoDB;

CREATE TABLE battery_charge_log (
    charge_log_id    BIGINT AUTO_INCREMENT PRIMARY KEY,
    battery_id       INT NOT NULL,
    reading_datetime DATETIME NOT NULL,
    charge_level_pct DECIMAL(5,2) NOT NULL,
    charge_level_kwh DECIMAL(6,3) NOT NULL,
    UNIQUE KEY uq_battery_hour (battery_id, reading_datetime),
    CONSTRAINT fk_charge_battery FOREIGN KEY (battery_id) REFERENCES batteries(battery_id)
        ON DELETE CASCADE,
    CONSTRAINT chk_charge_pct CHECK (charge_level_pct BETWEEN 0 AND 100)
) ENGINE = InnoDB;

CREATE TABLE energy_sales (
    sale_id       BIGINT AUTO_INCREMENT PRIMARY KEY,
    station_id    INT NOT NULL,
    sale_datetime DATETIME NOT NULL,
    energy_kwh    DECIMAL(7,3) NOT NULL,
    price_id      BIGINT NOT NULL,
    total_amount  DECIMAL(10,2) NOT NULL,
    UNIQUE KEY uq_station_hour (station_id, sale_datetime),
    CONSTRAINT fk_sale_station FOREIGN KEY (station_id) REFERENCES stations(station_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_sale_price FOREIGN KEY (price_id) REFERENCES energy_prices(price_id)
        ON DELETE RESTRICT
) ENGINE = InnoDB;

CREATE INDEX idx_stations_status ON stations(status);

CREATE INDEX idx_panels_installation_date ON panels(installation_date);

CREATE INDEX idx_panels_station ON panels(station_id);
CREATE INDEX idx_batteries_station ON batteries(station_id);
CREATE INDEX idx_generation_datetime ON panel_hourly_generation(reading_datetime);
CREATE INDEX idx_tilt_datetime ON panel_tilt_log(change_datetime);
CREATE INDEX idx_charge_datetime ON battery_charge_log(reading_datetime);
CREATE INDEX idx_price_datetime ON energy_prices(price_datetime);
CREATE INDEX idx_sales_datetime ON energy_sales(sale_datetime);

INSERT INTO addresses (address_id, country, region, city, street, building_number, postal_code, latitude, longitude) VALUES
(1,'Україна','Львівська обл.','Львів','вул. Зелена','15','79000',49.841980,24.031590),
(2,'Україна','Київська обл.','Київ','просп. Перемоги','40','03057',50.450100,30.523400),
(3,'Україна','Одеська обл.','Одеса','Французький бульвар','12','65000',46.464730,30.744350),
(4,'Україна','Харківська обл.','Харків','вул. Сумська','5','61000',49.993500,36.230380),
(5,'Україна','Львівська обл.','Дрогобич','вул. Шевченка','22','82100',49.350500,23.505500),
(6,'Україна','Івано-Франківська обл.','Івано-Франківськ','вул. Незалежності','8','76000',48.922700,24.710600),
(7,'Україна','Тернопільська обл.','Тернопіль','вул. Руська','10','46000',49.553500,25.594800),
(8,'Україна','Рівненська обл.','Рівне','вул. Соборна','3','33000',50.619800,26.251700),
(9,'Україна','Чернівецька обл.','Чернівці','вул. Головна','45','58000',48.291500,25.935200),
(10,'Україна','Волинська обл.','Луцьк','вул. Лесі Українки','7','43000',50.747200,25.325100),
(11,'Україна','Закарпатська обл.','Ужгород','вул. Корзо','2','88000',48.620800,22.287900),
(12,'Україна','Полтавська обл.','Полтава','вул. Соборності','18','36000',49.588600,34.551200);

INSERT INTO owners (owner_id, first_name, last_name, phone, email, passport_no) VALUES
(1,'Іван','Петренко','+380671234501','ipetrenko@example.com','AA123456'),
(2,'Олена','Коваленко','+380671234502','okovalenko@example.com','AA123457'),
(3,'Андрій','Шевчук','+380671234503','ashevchuk@example.com','AA123458'),
(4,'Марія','Бондаренко','+380671234504','mbondarenko@example.com','AA123459'),
(5,'Петро','Ткаченко','+380671234505','ptkachenko@example.com','AA123460'),
(6,'Наталія','Мороз','+380671234506','nmoroz@example.com','AA123461'),
(7,'Олег','Савченко','+380671234507','osavchenko@example.com','AA123462'),
(8,'Ірина','Полюк','+380671234508','ipoliuk@example.com','AA123463'),
(9,'Василь','Гринюк','+380671234509','vhryniuk@example.com','AA123464'),
(10,'Тетяна','Мельник','+380671234510','tmelnyk@example.com','AA123465'),
(11,'Роман','Бойко','+380671234511','rboiko@example.com','AA123466'),
(12,'Христина','Лисенко','+380671234512','khlysenko@example.com','AA123467'),
(13,'Богдан','Семенюк','+380671234513','bsemeniuk@example.com','AA123468'),
(14,'Софія','Кравець','+380671234514','skravets@example.com','AA123469');

INSERT INTO panel_types (panel_type_id, manufacturer, model, nominal_power_w, is_adjustable, warranty_years) VALUES
(1,'JinkoSolar','Tiger Neo 440',440,FALSE,25),
(2,'LONGi','Hi-MO6 550',550,TRUE,25),
(3,'Trina Solar','Vertex 500',500,FALSE,20),
(4,'Canadian Solar','HiKu6 450',450,TRUE,20),
(5,'SunPower','Maxeon 6 435',435,FALSE,25),
(6,'REC','Alpha Pure 430',430,FALSE,25),
(7,'Qcells','Q.Peak Duo 400',400,TRUE,20),
(8,'Hanwha','Q.Tron 420',420,FALSE,20),
(9,'First Solar','Series 7 480',480,FALSE,20),
(10,'Risen Energy','Titan 560',560,TRUE,25);

INSERT INTO battery_types (battery_type_id, manufacturer, model, capacity_kwh, cycle_life, warranty_years) VALUES
(1,'Tesla','Powerwall 2',13.50,5000,10),
(2,'BYD','Battery-Box Premium HVS',10.24,6000,10),
(3,'LG Energy Solution','RESU10H',9.80,6000,10),
(4,'Huawei','LUNA2000',10.00,6000,10),
(5,'Pylontech','US5000',4.80,6000,10),
(6,'Sonnen','Eco 10',10.00,10000,10),
(7,'Alpha ESS','SMILE5',5.70,6000,10),
(8,'GoodWe','Lynx Home F',10.00,6000,10),
(9,'Growatt','APX',10.00,6000,10),
(10,'Victron Energy','MultiPlus-II 5kWh',5.00,5000,5);

INSERT INTO energy_prices (price_id, price_datetime, price_per_kwh) VALUES
(1,'2026-10-21 00:00:00',2.1500),
(2,'2026-10-21 01:00:00',2.0500),
(3,'2026-10-21 02:00:00',1.9800),
(4,'2026-10-21 03:00:00',1.9500),
(5,'2026-10-21 04:00:00',2.0200),
(6,'2026-10-21 05:00:00',2.3000),
(7,'2026-10-21 06:00:00',2.6500),
(8,'2026-10-21 07:00:00',3.1000),
(9,'2026-10-21 08:00:00',3.4500),
(10,'2026-10-21 09:00:00',3.2000),
(11,'2026-10-21 10:00:00',2.9500),
(12,'2026-10-21 11:00:00',2.7000),
(13,'2026-10-21 12:00:00',2.5000),
(14,'2026-10-21 13:00:00',2.4500),
(15,'2026-10-21 14:00:00',2.6000);

INSERT INTO stations (station_id, address_id, station_name, installation_date, grid_connection_id, status) VALUES
(1,1,'Дах-Львів-1','2022-05-10','GRID-LV-001','active'),
(2,2,'Сад-Київ-1','2021-09-01','GRID-KV-001','active'),
(3,3,'Дах-Одеса-1','2023-02-15','GRID-OD-001','active'),
(4,4,'Ферма-Харків-1','2020-11-20','GRID-KH-001','maintenance'),
(5,5,'Дах-Дрогобич-1','2023-07-01','GRID-DR-001','active'),
(6,6,'Дах-Франківськ-1','2022-03-12','GRID-IF-001','active'),
(7,7,'Дах-Тернопіль-1','2023-09-05','GRID-TR-001','active'),
(8,8,'Дах-Рівне-1','2022-08-18','GRID-RV-001','active'),
(9,9,'Сад-Чернівці-1','2021-12-01','GRID-CV-001','inactive'),
(10,10,'Дах-Луцьк-1','2023-04-22','GRID-LT-001','active'),
(11,11,'Дах-Ужгород-1','2022-10-10','GRID-UZ-001','active'),
(12,12,'Ферма-Полтава-1','2020-06-15','GRID-PL-001','active');

INSERT INTO station_owners (station_id, owner_id, ownership_share, since_date) VALUES
(1,1,100.00,'2022-05-10'),
(2,2,60.00,'2021-09-01'),
(2,3,40.00,'2021-09-01'),
(3,4,100.00,'2023-02-15'),
(4,1,50.00,'2020-11-20'),
(4,5,50.00,'2020-11-20'),
(5,6,100.00,'2023-07-01'),
(6,7,70.00,'2022-03-12'),
(6,8,30.00,'2022-03-12'),
(7,9,100.00,'2023-09-05'),
(8,10,100.00,'2022-08-18'),
(9,11,60.00,'2021-12-01'),
(9,12,40.00,'2021-12-01'),
(10,13,100.00,'2023-04-22'),
(11,14,100.00,'2022-10-10'),
(12,9,100.00,'2020-06-15');

INSERT INTO panels (panel_id, station_id, panel_type_id, serial_number, installation_date, decommission_date, current_tilt_angle) VALUES
(1,1,1,'SN-PNL-0001','2022-05-10',NULL,32.0),
(2,1,2,'SN-PNL-0002','2022-05-10',NULL,35.0),
(3,2,1,'SN-PNL-0003','2021-09-01',NULL,30.0),
(4,2,3,'SN-PNL-0004','2021-09-05',NULL,30.0),
(5,3,4,'SN-PNL-0005','2023-02-15',NULL,28.0),
(6,4,1,'SN-PNL-0006','2020-11-20',NULL,33.0),
(7,4,5,'SN-PNL-0007','2020-11-20',NULL,33.0),
(8,5,2,'SN-PNL-0008','2023-07-01',NULL,31.0),
(9,6,3,'SN-PNL-0009','2022-03-12',NULL,29.0),
(10,6,4,'SN-PNL-0010','2022-03-12',NULL,29.0),
(11,7,6,'SN-PNL-0011','2023-09-05',NULL,34.0),
(12,8,7,'SN-PNL-0012','2022-08-18',NULL,27.0),
(13,9,8,'SN-PNL-0013','2021-12-01',NULL,30.0),
(14,10,9,'SN-PNL-0014','2023-04-22',NULL,31.0),
(15,11,10,'SN-PNL-0015','2022-10-10',NULL,26.0);

INSERT INTO batteries (battery_id, station_id, battery_type_id, serial_number, installation_date, decommission_date) VALUES
(1,1,1,'SN-BAT-0001','2022-05-10',NULL),
(2,2,2,'SN-BAT-0002','2021-09-01',NULL),
(3,3,3,'SN-BAT-0003','2023-02-15',NULL),
(4,4,4,'SN-BAT-0004','2020-11-20',NULL),
(5,5,5,'SN-BAT-0005','2023-07-01',NULL),
(6,6,1,'SN-BAT-0006','2022-03-12',NULL),
(7,7,6,'SN-BAT-0007','2023-09-05',NULL),
(8,8,7,'SN-BAT-0008','2022-08-18',NULL),
(9,9,8,'SN-BAT-0009','2021-12-01',NULL),
(10,10,9,'SN-BAT-0010','2023-04-22',NULL),
(11,11,10,'SN-BAT-0011','2022-10-10',NULL),
(12,12,2,'SN-BAT-0012','2020-06-15',NULL);

INSERT INTO panel_hourly_generation (panel_id, reading_datetime, generated_kwh) VALUES
(1,'2026-10-21 07:00:00',0.050),
(1,'2026-10-21 08:00:00',0.120),
(1,'2026-10-21 09:00:00',0.250),
(1,'2026-10-21 10:00:00',0.350),
(1,'2026-10-21 11:00:00',0.400),
(1,'2026-10-21 12:00:00',0.420),
(1,'2026-10-21 13:00:00',0.410),
(1,'2026-10-21 14:00:00',0.390),
(1,'2026-10-21 15:00:00',0.360),
(1,'2026-10-21 16:00:00',0.300),
(1,'2026-10-21 17:00:00',0.220),
(1,'2026-10-21 18:00:00',0.140),
(1,'2026-10-21 19:00:00',0.070),
(1,'2026-10-21 20:00:00',0.020),
(1,'2026-10-21 21:00:00',0.000);

INSERT INTO panel_tilt_log (panel_id, change_datetime, tilt_angle) VALUES
(2,'2026-10-21 09:00:00',25.0),
(2,'2026-10-21 15:00:00',20.0),
(5,'2026-10-21 08:00:00',20.0),
(5,'2026-10-21 16:00:00',18.0),
(8,'2026-10-21 09:00:00',28.0),
(8,'2026-10-21 15:00:00',24.0),
(10,'2026-10-21 10:00:00',27.0),
(10,'2026-10-21 14:00:00',25.0),
(12,'2026-10-21 08:30:00',22.0),
(12,'2026-10-21 16:30:00',19.0),
(15,'2026-10-21 09:30:00',24.0),
(15,'2026-10-21 15:30:00',21.0);

INSERT INTO battery_charge_log (battery_id, reading_datetime, charge_level_pct, charge_level_kwh) VALUES
(1,'2026-10-21 00:00:00',60.00,8.100),
(1,'2026-10-21 01:00:00',55.00,7.425),
(1,'2026-10-21 02:00:00',50.00,6.750),
(1,'2026-10-21 03:00:00',45.00,6.075),
(1,'2026-10-21 04:00:00',40.00,5.400),
(1,'2026-10-21 05:00:00',38.00,5.130),
(1,'2026-10-21 06:00:00',42.00,5.670),
(1,'2026-10-21 07:00:00',55.00,7.425),
(1,'2026-10-21 08:00:00',70.00,9.450),
(1,'2026-10-21 09:00:00',82.00,11.070),
(1,'2026-10-21 10:00:00',90.00,12.150),
(1,'2026-10-21 11:00:00',95.00,12.825),
(1,'2026-10-21 12:00:00',97.00,13.095),
(1,'2026-10-21 13:00:00',98.00,13.230),
(1,'2026-10-21 14:00:00',96.00,12.960);

INSERT INTO energy_sales (station_id, sale_datetime, energy_kwh, price_id, total_amount) VALUES
(1,'2026-10-21 08:00:00',1.200,9,4.1400),
(1,'2026-10-21 09:00:00',1.500,10,4.8000),
(2,'2026-10-21 08:00:00',0.900,9,3.1050),
(2,'2026-10-21 10:00:00',1.400,11,4.1300),
(3,'2026-10-21 09:00:00',2.100,10,6.7200),
(4,'2026-10-21 07:00:00',1.000,8,3.1000),
(5,'2026-10-21 08:00:00',0.700,9,2.4150),
(6,'2026-10-21 09:00:00',1.800,10,5.7600),
(6,'2026-10-21 06:00:00',0.500,7,1.3250),
(7,'2026-10-21 10:00:00',1.300,11,3.8350),
(8,'2026-10-21 11:00:00',0.950,12,2.5650),
(9,'2026-10-21 12:00:00',1.100,13,2.7500),
(10,'2026-10-21 13:00:00',1.250,14,3.0625),
(11,'2026-10-21 14:00:00',0.800,15,2.0800),
(12,'2026-10-21 08:00:00',1.050,9,3.6225);
