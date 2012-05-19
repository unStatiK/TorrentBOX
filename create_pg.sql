CREATE TABLE accounts (
    id serial NOT NULL,
    name varchar(255) NOT NULL UNIQUE,
    psw varchar(255) DEFAULT '' NOT NULL,
    status int,
    primary key(id)
);

CREATE TABLE torrents (
    id serial NOT NULL ,
    name text NOT NULL,
    description text DEFAULT '' NOT NULL,
    filename varchar(255) NOT NULL,
    size real NOT NULL,
    id_acc int REFERENCES accounts(id) ON DELETE CASCADE ON UPDATE CASCADE,
    primary key(id)
);


CREATE TABLE tags (
    id serial NOT NULL ,
    name varchar(20) UNIQUE,
    primary key(id)
);

CREATE TABLE tags_links (
    id_tags int REFERENCES tags(id) ON DELETE CASCADE ON UPDATE CASCADE,
    id_torrent int REFERENCES torrents(id) ON DELETE CASCADE ON UPDATE CASCADE
);
