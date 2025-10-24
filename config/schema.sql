CREATE DATABASE IF NOT EXISTS mortalidad_db;
USE mortalidad_db;

CREATE TABLE IF NOT EXISTS causas (
  codigo VARCHAR(10) PRIMARY KEY,
  descripcion VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS divipola (
  id INT PRIMARY KEY AUTO_INCREMENT,
  departamento VARCHAR(100),
  municipio VARCHAR(100),
  codigo_divipola VARCHAR(20)
);

CREATE TABLE IF NOT EXISTS muertes (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  fecha DATE,
  departamento VARCHAR(100),
  municipio VARCHAR(100),
  sexo CHAR(1),
  edad INT,
  grupo_edad VARCHAR(50),
  codigo_causa VARCHAR(10),
  FOREIGN KEY (codigo_causa) REFERENCES causas(codigo)
);
