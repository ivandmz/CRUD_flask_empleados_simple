create database if not exists empleados character set utf8mb4;
use empleados;
/*drop table if exists empleados;*/

create table empleados (
	id int not null auto_increment,
	nombre varchar(255),
	correo varchar(255),
	foto varchar(5000),
	primary key(id)
);

SELECT * FROM `empleados`.`empleados`;

INSERT INTO empleados (nombre, correo, foto) VALUES ('ivan','ivan@gmail.com','fotodeivan.jpg');