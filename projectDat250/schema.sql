
CREATE TABLE "users" (
	"userid"	TEXT UNIQUE NOT NULL,
	"username"	TEXT NOT NULL,
	"password"	TEXT NOT NULL,
  "authenticated" BOOLEAN,
	PRIMARY KEY("userid")
);

CREATE TABLE post (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  author_id TEXT NOT NULL,
  author_name TEXT NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  title TEXT NOT NULL,
  body TEXT NOT NULL,
  FOREIGN KEY (author_id) REFERENCES user (id)
);

CREATE TABLE "friends" (
  "id" INTEGER PRIMARY KEY AUTOINCREMENT,
  "userid" TEXT NOT NULL,
  "friendid" TEXT NOT NULL
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

INSERT INTO "friends" ("userid","friendid") VALUES("djfnj", "asdasd");
INSERT INTO "friends" ("userid","friendid") VALUES("djfnj", "afhf");

INSERT INTO post (author_id,author_name,created,title,body) VALUES("asdasd","Sakurai",'2000-01-01 00:00:01',"lol",
"funnyfunnyfunnyfunnyfunnyfunnyfunnyfunnyfunnyfunnyfunny");

INSERT INTO post (author_id,author_name,created,title,body) VALUES("afhf","min bror",'2020-10-01 16:02:13',"POGGERS",
"minecraft Steve building");
