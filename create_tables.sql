CREATE TABLE `metadata_attribute` (
  `ATT_ID` bigint(20) PRIMARY KEY AUTO_INCREMENT,
  `Name` varchar(50),
  `Type` varchar(10),
  `Description` varchar(255),
  `required_att` tinyint(1)
);

CREATE TABLE `project` (
  `Project_ID` varchar(50) PRIMARY KEY,
  `Name` varchar(255),
  `is_public` tinyint(1),
  `Owner_ID` bigint(20),
  `Creator_ID` bigint(20),
  `Creation_date` data(6),
  `Directory` varchar(255)
);

CREATE TABLE `user_project` (
  `Project_ID` varchar(50),
  `User_ID` bigint(20),
  `Type` tinyint(1),
  PRIMARY KEY (`User_ID`, `Project_ID`)
);

CREATE TABLE `share_project` (
  `Project_ID` varchar(50),
  `Share_ID` varchar(50),
  `Type` tinyint(1),
  PRIMARY KEY (`Share_ID`, `Project_ID`)
);

CREATE TABLE `project_file` (
  `File_ID` varchar(50) PRIMARY KEY,
  `File_name` varchar(255),
  `File_display_name` varchar(255),
  `Project_ID` varchar(50),
  `Uploaded_by` bigint(20),
  `Uploaded_Date` datetime
);

CREATE TABLE `sample_metadata` (
  `Project_ID` varchar(50),
  `ATT_ID` bigint(20),
  `Sample_ID` varchar(300),
  `File_ID` varchar(50),
  `Value` varchar(255),
  PRIMARY KEY (`Sample_ID`, `ATT_ID`, `Project_ID`)
);

CREATE TABLE `project_info` (
  `Project_ID` varchar(50) PRIMARY KEY,
  `Description` varchar(255),
  `BioProject_link` varchar(255),
  `Institute` varchar(255),
  `Contact_email` varchar(255),
  `Funding` varchar(255)
);

CREATE TABLE `papers` (
  `Paper_ID` varchar(50) PRIMARY KEY,
  `Title` varchar(255),
  `DOI` varchar(255),
  `link` varchar(255),
  `PM_ID` varchar(100)
);

CREATE TABLE `project_papers` (
  `Project_ID` varchar(50),
  `Paper_ID` varchar(50),
  PRIMARY KEY (`Project_ID`, `Paper_ID`)
);

CREATE TABLE `project_tasks` (
  `Task_ID` varchar(50) PRIMARY KEY,
  `Project_ID` varchar(50),
  `Input_File_ID` varchar(50),
  `Output_File_ID` varchar(50),
  `Type` varchar(50),
  `Status` varchar(50),
  `Timestamp` DATE NOT NULL
);

CREATE TABLE `SRA_record` (
  `Project_ID` varchar(50) PRIMARY KEY,
  `SRA` varchar(50) NOT NULL,
  `Assembly_date` DATE NOT NULL,
  `Status` int NOT NULL
);

CREATE TABLE `user_info` (
  `User_ID` bigint(20) PRIMARY KEY,
  `User_type` int NOT NULL
);

ALTER TABLE `user_info` ADD FOREIGN KEY (`User_ID`) REFERENCES `project` (`Owner_ID`);

ALTER TABLE `user_project` ADD FOREIGN KEY (`Project_ID`) REFERENCES `project` (`Project_ID`);

ALTER TABLE `SRA_record` ADD FOREIGN KEY (`Project_ID`) REFERENCES `project` (`Project_ID`);

ALTER TABLE `share_project` ADD FOREIGN KEY (`Project_ID`) REFERENCES `project` (`Project_ID`);

ALTER TABLE `project_file` ADD FOREIGN KEY (`Project_ID`) REFERENCES `project` (`Project_ID`);

ALTER TABLE `sample_metadata` ADD FOREIGN KEY (`Project_ID`) REFERENCES `project` (`Project_ID`);

ALTER TABLE `sample_metadata` ADD FOREIGN KEY (`ATT_ID`) REFERENCES `metadata_attribute` (`ATT_ID`);

ALTER TABLE `sample_metadata` ADD FOREIGN KEY (`File_ID`) REFERENCES `project_file` (`File_ID`);

ALTER TABLE `project_info` ADD FOREIGN KEY (`Project_ID`) REFERENCES `project` (`Project_ID`);

ALTER TABLE `project_papers` ADD FOREIGN KEY (`Project_ID`) REFERENCES `project` (`Project_ID`);

ALTER TABLE `project_papers` ADD FOREIGN KEY (`Paper_ID`) REFERENCES `papers` (`Paper_ID`);

ALTER TABLE `project_tasks` ADD FOREIGN KEY (`Project_ID`) REFERENCES `project` (`Project_ID`);

ALTER TABLE `project_tasks` ADD FOREIGN KEY (`Input_File_ID`) REFERENCES `project_file` (`File_ID`);

ALTER TABLE `project_tasks` ADD FOREIGN KEY (`Output_File_ID`) REFERENCES `project_file` (`File_ID`);

