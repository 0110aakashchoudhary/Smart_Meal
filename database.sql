CREATE DATABASE IF NOT EXISTS mess_management;
USE mess_management;

CREATE TABLE IF NOT EXISTS meal_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    day_of_week INT NOT NULL,
    meal_type INT NOT NULL,
    special_item INT DEFAULT 0,
    is_weekend INT DEFAULT 0,
    expected_students INT NOT NULL,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO meal_records (day_of_week, meal_type, special_item, is_weekend, expected_students) VALUES
(0, 0, 0, 0, 180), (0, 1, 0, 0, 240), (0, 2, 1, 0, 260),
(1, 0, 0, 0, 175), (1, 1, 0, 0, 235), (1, 2, 0, 0, 220),
(2, 0, 0, 0, 190), (2, 1, 0, 0, 250), (2, 2, 1, 0, 275),
(3, 0, 0, 0, 170), (3, 1, 0, 0, 230), (3, 2, 0, 0, 215),
(4, 0, 0, 0, 160), (4, 1, 0, 0, 210), (4, 2, 1, 0, 240),
(5, 0, 1, 1, 140), (5, 1, 1, 1, 180), (5, 2, 1, 1, 190),
(6, 0, 1, 1, 130), (6, 1, 1, 1, 175), (6, 2, 0, 1, 160);