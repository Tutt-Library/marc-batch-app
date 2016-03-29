CREATE TABLE Jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    created_on DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    job_code VARCHAR NOT NULL,
    input_marc BLOB NOT NULL,
    output_marc BLOB,
    record_type_id INTEGER NOT NULL,
    FOREIGN KEY (record_type_id) REFERENCES RecordType (id)
);

CREATE TABLE RecordType (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    name VARCHAR UNIQUE NOT NULL
);

INSERT INTO RecordType (name) VALUES ("Bibliographic");
INSERT INTO RecordType (name) VALUES ("Person Authority");
INSERT INTO RecordType (name) VALUES ("Subject Authority");


CREATE TABLE Notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    created_on DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    log_id INTEGER,
    value TEXT,
    FOREIGN KEY (log_id) REFERENCES Jobs (id)
);

CREATE TABLE Statistics (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    created_on DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    log_id INTEGER,
    stat_type_id INTEGER,
    value FLOAT,
    FOREIGN KEY (log_id) REFERENCES Jobs (id),
    FOREIGN KEY (stat_type_id) REFERENCES StatisticType (id)
);

CREATE TABLE StatisticType (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    name VARCHAR UNIQUE NOT NULL
);

INSERT INTO StatisticType (name) VALUES ("New Records");
INSERT INTO StatisticType (name) VALUES ("Overlaid Records");
INSERT INTO StatisticType (name) VALUES ("Rejected Records");
