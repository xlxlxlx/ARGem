CREATE TABLE `metadata_attribute` (
  `ATT_ID` bigint(20) PRIMARY KEY AUTO_INCREMENT,
  `Name` varchar(50),
  `Type` varchar(10),
  `Description` varchar(255),
  `required_att` tinyint(1)
);

CREATE TABLE `sample_metadata` (
  `Project_ID` varchar(50),
  `ATT_ID` bigint(20),
  `Sample_ID` varchar(300),
  `File_ID` varchar(50),
  `Value` varchar(255),
  PRIMARY KEY (`Sample_ID`, `ATT_ID`, `Project_ID`)
);

CREATE TABLE `project` (
  `Project_ID` varchar(50) PRIMARY KEY,
  `Name` varchar(255),
  `is_public` tinyint(1),
  `User_ID` bigint(20),
  `Creation_date` data(6),
  `Directory` varchar(255)
);

CREATE TABLE `project_tasks` (
  `Task_ID` varchar(50) PRIMARY KEY,
  `Project_ID` varchar(50),
  `Input_File_ID` varchar(50),
  `Output_File_ID` varchar(50),
  `Type` varchar(50),
  `Status` varchar(50),
  `Timestamp` datetime,
  `MGE_DB` varchar(50),
  `User_ID` bigint(20)
);

CREATE TABLE `SRA_record` (
  `SRA` varchar(50) NOT NULL,
  `Status` int(11) NOT NULL
);

CREATE TABLE `users` (
  `User_ID` bigint(20) PRIMARY KEY,
  `User_email` varchar(100)
);

ALTER TABLE `users` ADD FOREIGN KEY (`User_ID`) REFERENCES `project` (`User_ID`);

ALTER TABLE `sample_metadata` ADD FOREIGN KEY (`Project_ID`) REFERENCES `project` (`Project_ID`);

ALTER TABLE `sample_metadata` ADD FOREIGN KEY (`ATT_ID`) REFERENCES `metadata_attribute` (`ATT_ID`);

ALTER TABLE `project` ADD FOREIGN KEY (`Project_ID`) REFERENCES `project_tasks` (`Project_ID`);
