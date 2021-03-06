
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