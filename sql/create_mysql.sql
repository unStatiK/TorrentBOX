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
    size bigint NOT NULL,
    id_acc bigint UNSIGNED NOT NULL,
    CONSTRAINT fk_id_acc FOREIGN KEY (id_acc) REFERENCES accounts(id) ON DELETE CASCADE ON UPDATE CASCADE,
    FULLTEXT name_idx (name),
    FULLTEXT desc_idx (description)
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

CREATE TABLE torrents_data (
    id_torrent bigint UNSIGNED NOT NULL,
    payload longtext NOT NULL,
    CONSTRAINT fk_id_torrent_data FOREIGN KEY (id_torrent) REFERENCES torrents(id) ON DELETE CASCADE ON UPDATE CASCADE,
    PRIMARY KEY(id_torrent)
) ENGINE=INNODB DEFAULT CHARACTER SET=utf8mb4;

CREATE TABLE torrents_files (
    id serial PRIMARY KEY,
    id_torrent bigint UNSIGNED NOT NULL,
    filename text NOT NULL,
    CONSTRAINT fk_id_torrent_file FOREIGN KEY (id_torrent) REFERENCES torrents(id) ON DELETE CASCADE ON UPDATE CASCADE,
    FULLTEXT filename_idx (filename)
) ENGINE=INNODB DEFAULT CHARACTER SET=utf8mb4;

CREATE TABLE torrents_stat (
    id tinyint NOT NULL,
    size bigint NOT NULL,
    PRIMARY KEY(id)
) ENGINE=INNODB DEFAULT CHARACTER SET=utf8mb4;

CREATE INDEX torrents_files_id_torrent_idx ON torrents_files (id_torrent) USING BTREE;
CREATE INDEX torrents_data_id_torrent_idx ON torrents_data (id_torrent) USING BTREE;
