CREATE TABLE accounts (
    id serial PRIMARY KEY,
    name varchar(255) NOT NULL UNIQUE,
    password varchar(255) DEFAULT '' NOT NULL,
    status tinyint
) ENGINE=INNODB DEFAULT CHARACTER SET=utf8mb4;

CREATE TABLE torrents (
    id serial PRIMARY KEY,
    name text NOT NULL,
    description text NOT NULL,
    filename varchar(255) NOT NULL,
    size real NOT NULL,
    id_acc bigint UNSIGNED NOT NULL,
    CONSTRAINT fk_id_acc FOREIGN KEY (id_acc) REFERENCES accounts(id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=INNODB DEFAULT CHARACTER SET=utf8mb4;


CREATE TABLE tags (
    id serial PRIMARY KEY,
    name varchar(255) UNIQUE
) ENGINE=INNODB DEFAULT CHARACTER SET=utf8mb4;

CREATE TABLE tags_links (
    id_tags bigint UNSIGNED NOT NULL,
    id_torrent bigint UNSIGNED NOT NULL,
    CONSTRAINT fk_id_tags FOREIGN KEY (id_tags) REFERENCES tags(id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_id_torrent FOREIGN KEY (id_torrent) REFERENCES torrents(id) ON DELETE CASCADE ON UPDATE CASCADE,
    PRIMARY KEY(id_tags,id_torrent)
) ENGINE=INNODB DEFAULT CHARACTER SET=utf8mb4;