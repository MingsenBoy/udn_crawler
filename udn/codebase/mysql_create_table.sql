CREATE TABLE all_2019
	(artTitle			VARCHAR(255)	NOT NULL,
	artDate				datetime		NOT NULL,
	artCatagory	VARCHAR(255)	NOT NULL,
	artSecondCategory	VARCHAR(255)	NOT NULL,
	artUrl				VARCHAR(160)	NOT NULL,
	artContent			mediumtext		NOT NULL,
	PRIMARY KEY (artUrl));