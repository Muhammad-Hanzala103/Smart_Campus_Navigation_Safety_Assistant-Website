BEGIN TRANSACTION;
CREATE TABLE audit_log (
	id INTEGER NOT NULL, 
	user_id INTEGER, 
	action VARCHAR(100) NOT NULL, 
	timestamp DATETIME, 
	details VARCHAR(500), 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES user (id)
);
CREATE TABLE booking (
	id INTEGER NOT NULL, 
	user_id INTEGER NOT NULL, 
	room_id INTEGER NOT NULL, 
	start_time DATETIME NOT NULL, 
	end_time DATETIME NOT NULL, 
	status VARCHAR(20), 
	reason VARCHAR(200), 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES user (id), 
	FOREIGN KEY(room_id) REFERENCES room (id)
);
INSERT INTO "booking" VALUES(1,3,1,'2025-12-21 14:44:39.269650','2025-12-21 16:44:39.269685','approved','Staff Meeting');
INSERT INTO "booking" VALUES(2,3,2,'2025-12-22 14:44:39.269783','2025-12-22 15:44:39.269786','pending','Class lecture');
CREATE TABLE incident (
	id INTEGER NOT NULL, 
	user_id INTEGER NOT NULL, 
	description TEXT NOT NULL, 
	category VARCHAR(50), 
	x FLOAT, 
	y FLOAT, 
	image_path VARCHAR(200), 
	status VARCHAR(20), 
	created_at DATETIME, 
	ai_labels TEXT, 
	ai_severity VARCHAR(20), 
	ai_recommendation TEXT, 
	ai_analyzed_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES user (id)
);
INSERT INTO "incident" VALUES(1,2,'Broken window near Lab 1','Maintenance',405.0,205.0,NULL,'open','2025-12-20 09:44:39.274997',NULL,NULL,NULL,NULL);
CREATE TABLE map_edge (
	id INTEGER NOT NULL, 
	start_node_id INTEGER NOT NULL, 
	end_node_id INTEGER NOT NULL, 
	weight FLOAT, 
	PRIMARY KEY (id), 
	FOREIGN KEY(start_node_id) REFERENCES map_node (id), 
	FOREIGN KEY(end_node_id) REFERENCES map_node (id)
);
CREATE TABLE map_node (
	id INTEGER NOT NULL, 
	name VARCHAR(50) NOT NULL, 
	x FLOAT NOT NULL, 
	y FLOAT NOT NULL, 
	description VARCHAR(200), 
	PRIMARY KEY (id)
);
INSERT INTO "map_node" VALUES(1,'Gate',100.0,500.0,'Main Entrance');
INSERT INTO "map_node" VALUES(2,'Admin',200.0,400.0,'Administration Block');
INSERT INTO "map_node" VALUES(3,'Library',300.0,300.0,'Central Library');
INSERT INTO "map_node" VALUES(4,'Lab1',400.0,200.0,'Computer Lab 1');
INSERT INTO "map_node" VALUES(5,'Lab2',450.0,250.0,'Physics Lab');
INSERT INTO "map_node" VALUES(6,'Canteen',500.0,500.0,'Stu. Center');
INSERT INTO "map_node" VALUES(7,'Sports',600.0,100.0,'Sports Complex');
CREATE TABLE room (
	id INTEGER NOT NULL, 
	name VARCHAR(50) NOT NULL, 
	node_id INTEGER, 
	capacity INTEGER, 
	PRIMARY KEY (id), 
	FOREIGN KEY(node_id) REFERENCES map_node (id)
);
INSERT INTO "room" VALUES(1,'Conference Room A',2,20);
INSERT INTO "room" VALUES(2,'Lecture Hall 1',3,100);
INSERT INTO "room" VALUES(3,'Lab 101',4,30);
INSERT INTO "room" VALUES(4,'Gym Hall',7,50);
CREATE TABLE user (
	id INTEGER NOT NULL, 
	email VARCHAR(120) NOT NULL, 
	password_hash VARCHAR(128), 
	role VARCHAR(20) NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (email)
);
INSERT INTO "user" VALUES(1,'admin@demo.edu','scrypt:32768:8:1$gQar1DG1s5sNxkI5$e429388a9a51d6689eb2c7f3d64334dd288ebfdad28eada93399d3ff6da4d90b06d7bb1f3f495e5c34bf855a0544e79a2304fa6137d99b60ea8c016df9199309','admin');
INSERT INTO "user" VALUES(2,'security@demo.edu','scrypt:32768:8:1$8bhbqyUtZDAsBoZc$62d5e9242552ad03e3564e3b51bbd8c46f4429660f8edefd747397debfe31df25877dd309cfa27b52844719de8f2bf07df8bccf2c32c25cb8c6c72d1cd7a3fc3','security');
INSERT INTO "user" VALUES(3,'staff@demo.edu','scrypt:32768:8:1$Sw2lEio6NFHh28n7$2192b3fb4665c565ae81e8467896c77a4c01b784785bd3dee70c8b813c4d7c60794dc525c4358a24c43ab197277c1d651ae151bd50ed6e9f7acff763c867f8d1','staff');
COMMIT;
