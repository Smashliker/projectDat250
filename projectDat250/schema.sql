
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
  created TEXT NOT NULL,
  title TEXT NOT NULL,
  body TEXT NOT NULL,
  image_path TEXT,
  FOREIGN KEY (author_id) REFERENCES user (id)
);

CREATE TABLE "friends" (
  "id" INTEGER PRIMARY KEY AUTOINCREMENT,
  "userid" TEXT NOT NULL,
  "friendid" TEXT NOT NULL
);

CREATE TABLE comments (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  author_id TEXT NOT NULL,
  author_name TEXT NOT NULL,
  created TEXT NOT NULL,
  body TEXT NOT NULL,
  post_id INTEGER,
  FOREIGN KEY (post_id) REFERENCES post (id)
);

CREATE TABLE tmp (
  userid TEXT NOT NULL,
  post_id INTEGER NOT NULL
);

INSERT INTO "users" 
  ("userid","username", "password")
VALUES('vvnuwzyy', 'Admin', '$5$rounds=535000$Yi35iVeKoxsg8YM2$WDc2KOGEUIuRzLXsovK5OI.rGGv97lsn1ecl1xLo8D2');

INSERT INTO post
  (author_id, author_name, created, title, body)
VALUES('vvnuwzyy', 'Admin', '09/10/2020  19:40:50' ,'Welcome!', "Welcome to our website! We look forward to seeing what new ideas you'll share here.");

