
CREATE TABLE "users" (
	"userid"	TEXT UNIQUE NOT NULL,
	"username"	TEXT NOT NULL,
	"password"	TEXT NOT NULL,
	PRIMARY KEY("userid")
);

CREATE TABLE post (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  author_id INTEGER NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  title TEXT NOT NULL,
  body TEXT NOT NULL,
  FOREIGN KEY (author_id) REFERENCES user (id)
);

CREATE TABLE "friends" (
  "number" INTEGER NOT NULL,
  "userid" TEXT NOT NULL,
  "friendid" TEXT NOT NULL,
  PRIMARY KEY("number")
);

INSERT INTO "users" 
  ("userid","username", "password")
VALUES('djfnj', 'Smashliker', 'HahaTenkOmDetteVarMittEktePassord');
INSERT INTO "users" 
  ("userid","username", "password")
VALUES('asdasd', 'Sakurai', 'haha');
INSERT INTO "users" 
  ("userid","username", "password")
VALUES('afhf', 'min bror', 'funny');

INSERT INTO "friends" ("number","userid","friendid") VALUES(1,"djfnj", "asdasd");
INSERT INTO "friends" ("number","userid","friendid") VALUES(2,"djfnj", "afhf");
