
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
  userid TEXT NOT NULL PRIMARY KEY,
  post_id INTEGER NOT NULL
);

INSERT INTO "users" 
  ("userid","username", "password")
VALUES('vvnuwzyy', 'Admin', 'e46416f2250b2f1ac4cac0d4f96bb7bb05761b741d1c1dd40fb3df0e6c23f29a0028950f7a2ae8cd057fef8bf6b48636ac06fc4492c2af0c0f9d357aaf4dcb2b');

INSERT INTO post
  (author_id, author_name, created, title, body)
VALUES('vvnuwzyy', 'Admin', '09/10/2020  19:40:50' ,'Welcome!', "Welcome to our website! We look forward to seeing what new ideas you'll share here.");

