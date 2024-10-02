
```plane_type tabe
INSERT INTO plane_type (id, plane_type, description)
VALUES 
("001", "HELICOOPTER", "maximum speed 300km/h, maximum distance 1000km, all airports "),
("002", "LIGHT JET", "maximum speed 500km/h, maximum distance 2000km, small airports, medium airports, big airports"),
("003", "JUMBO JET 1", "maximum speed 800km/h, maximum distance 3000km, medium airports, big airports"),
("004", "JUMBO JET 2", "maximum speed 800km/h, maximum distance 4000km, medium airports"),
("005", "HEAVY JET", "maximum speed 600km/h, maximum distance 5000km, big airports");

```plane table
INSERT INTO plane (plane_id, plane_name, plane_color, plane_type, comsume_energy)
VALUES 
("001", " HEL-NH90", "BLACK", "001", "10"),
("002", " PHE-300", "BROWN", "002", "20"),
("003", "AIR-A380",  "BLUE", "003","30"),
("004", "BOE-B787",  "RED", "004","40"),
("005", "CHA-350", "wHITE", "005","50"),
("006", "GUF-G650", "GREEN", "005","50");
```
```task_type table
INSERT INTO task_type (type, timelimit)
VALUES
("1","SOLVE PROBLEM", "60"),
("2","REFUELING", "120");
```
```fk for airport_plane
ALTER TABLE airport_plane
	DROP FOREIGN KEY f_airport_plane_airport;
ALTER TABLE airport
	ADD INDEX type (type) USING BTREE;
ALTER TABLE airport_plane
	ADD CONSTRAINT FK_airport_plane_airport FOREIGN KEY (airport) REFERENCES airport (type) ON UPDATE CASCADE ON DELETE CASCADE;
```
```airport_plane table
INSERT INTO airport_plane (airport,plane_id,initial_score)
VALUES
("heliport","001", "100"),
("small_airport","001", "100"),
("medium_airport","001", "100"),
("large_airport","001", "100"),
("small_airport","002", "100"),
("medium_airport","002", "100"),
("large_airport","002", "100"),
("medium_airport","003", "100"),
("large_airport","003", "100"),
("medium_airport","004", "100"),
("large_airport","005", "100"),
("large_airport","006", "100");
```
```task table
ALTER TABLE task
	DROP FOREIGN KEY f_airport;
ALTER TABLE task
	modify COLUMN airport VARCHAR(20);
	
INSERT INTO task(id, task_name, task_desciption,task_answer, task_type, airport, reward, penalty)
VALUES
("1", "arrage sentence", "being green stones at 3 small airport " ,"3 green stones being at small airport", "1", "large_airport", "10", "20"),
("2", "arrage sentence", "being green stones at 3 small airport " ,"3 green stones being at small airport", "1", "small_airport", "10", "20"),
("3", "arrage sentence", "being green stones at 3 small airport " ,"3 green stones being at small airport", "1", "medium_airport", "10", "20"),
("4", "arrage sentence", "being green stones at 3 small airport " ,"3 green stones being at small airport", "1", "heliport", "10", "20"),
("5", "buy information", " get position of final stone", "yes", "1", "heliport", "0", " 150"),
("6", "buy information", " get position of final stone", "yes", "1", "small_aiport", "0", " 150"),
("7", "buy information", " get position of final stone", "yes", "1", "medium_airport", "0", " 150"),
("8", "buy information", " get position of final stone", "yes", "1", "large_airport", "0", " 150");
```



