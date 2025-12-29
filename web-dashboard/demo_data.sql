BEGIN TRANSACTION;
CREATE TABLE user (id INTEGER NOT NULL, email VARCHAR(120) NOT NULL, name VARCHAR(100), role VARCHAR(20) NOT NULL, password_hash VARCHAR(200), created_at DATETIME, PRIMARY KEY (id), UNIQUE (email));
INSERT INTO "user" VALUES(1,'admin','Super Admin','admin','pbkdf2:sha256:600000$....','2023-10-01 10:00:00');
INSERT INTO "user" VALUES(2,'security1','John Sec','security','pbkdf2:sha256:600000$....','2023-10-01 10:00:00');
INSERT INTO "user" VALUES(3,'staff1','Jane Staff','staff','pbkdf2:sha256:600000$....','2023-10-01 10:00:00');

CREATE TABLE map_node (id INTEGER NOT NULL, name VARCHAR(50) NOT NULL, x FLOAT NOT NULL, y FLOAT NOT NULL, description VARCHAR(200), PRIMARY KEY (id));
INSERT INTO "map_node" VALUES(1,'Gate',120.0,340.0,'Main Gate');
INSERT INTO "map_node" VALUES(2,'Admin',200.0,100.0,'Admin Block');

CREATE TABLE incident (id INTEGER NOT NULL, user_id INTEGER NOT NULL, category VARCHAR(50) NOT NULL, description TEXT NOT NULL, image_path VARCHAR(200), x FLOAT, y FLOAT, status VARCHAR(20), created_at DATETIME, PRIMARY KEY (id), FOREIGN KEY(user_id) REFERENCES user (id));
INSERT INTO "incident" VALUES(1,2,'Maintenance','Leaking pipe',NULL,200.0,100.0,'open','2023-10-02 09:00:00');
COMMIT;
