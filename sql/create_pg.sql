CREATE TABLE accounts (
    id serial NOT NULL,
    name varchar(255) NOT NULL UNIQUE,
    password varchar(255) DEFAULT '' NOT NULL,
    status smallint,
    PRIMARY KEY(id)
);

CREATE TABLE torrents (
    id serial NOT NULL,
    name text NOT NULL,
    description text DEFAULT '' NOT NULL,
    filename varchar(255) NOT NULL,
    size real NOT NULL,
    id_acc int REFERENCES accounts(id) ON DELETE CASCADE ON UPDATE CASCADE,
    PRIMARY KEY(id)
);


CREATE TABLE tags (
    id serial NOT NULL ,
    name varchar(255) UNIQUE,
    PRIMARY KEY(id)
);

CREATE TABLE tags_links (
    id_tags int REFERENCES tags(id) ON DELETE CASCADE ON UPDATE CASCADE,
    id_torrent int REFERENCES torrents(id) ON DELETE CASCADE ON UPDATE CASCADE,
    PRIMARY KEY(id_tags,id_torrent)
);

CREATE TABLE torrents_data (
    id_torrent int REFERENCES torrents(id) ON DELETE CASCADE ON UPDATE CASCADE,
    payload text NOT NULL,
    PRIMARY KEY(id_torrent)
);

CREATE TABLE torrents_files (
    id serial NOT NULL,
    id_torrent int REFERENCES torrents(id) ON DELETE CASCADE ON UPDATE CASCADE,
    filename text NOT NULL,
    PRIMARY KEY(id)
);
