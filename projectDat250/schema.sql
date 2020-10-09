
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
VALUES('AJFNAJFpiebfqfwbj29334059uihsdnDD124', 'Admin', '2u129bRUbf91ucwJsa9w9b12ubejd218edubsia9');

