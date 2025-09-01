CREATE DATABASE Local_Food_Wastage;
USE Local_Food_Wastage;

SELECT City, 
       COUNT(DISTINCT Provider_ID) AS Total_Providers,
       COUNT(DISTINCT Receiver_ID) AS Total_Receivers
FROM (
    SELECT City, Provider_ID, NULL AS Receiver_ID FROM providers_data_cleaned
    UNION ALL
    SELECT City, NULL, Receiver_ID FROM receivers_data_cleaned
) combined
GROUP BY City;

SELECT Provider_Type, SUM(Quantity) AS Total_Quantity
FROM food_listings_data_cleaned
GROUP BY Provider_Type
ORDER BY Total_Quantity DESC
LIMIT 1;

SELECT Name, Type, Address, Contact
FROM providers_data_cleaned
WHERE City = 'New Jessica';

SELECT r.Name, r.City, COUNT(c.Claim_ID) AS Total_Claims
FROM claims_data_cleaned c
JOIN receivers_data_cleaned r ON c.Receiver_ID = r.Receiver_ID
GROUP BY r.Name, r.City
ORDER BY Total_Claims DESC
LIMIT 5;

SELECT SUM(Quantity) AS Total_Food_Quantity
FROM food_listings_data_cleaned;

SELECT p.City, COUNT(f.Food_ID) AS Total_Listings
FROM food_listings_data_cleaned f
JOIN providers_data_cleaned p ON f.Provider_ID = p.Provider_ID
GROUP BY p.City
ORDER BY Total_Listings DESC
LIMIT 5;

SELECT Food_Type, COUNT(Food_ID) AS Count_Food
FROM food_listings_data_cleaned
GROUP BY Food_Type
ORDER BY Count_Food DESC;

SELECT f.Food_Name, COUNT(c.Claim_ID) AS Total_Claims
FROM claims_data_cleaned c
JOIN food_listings_data_cleaned f ON c.Food_ID = f.Food_ID
GROUP BY f.Food_Name
ORDER BY Total_Claims DESC;

SELECT p.Name, COUNT(c.Claim_ID) AS Successful_Claims
FROM claims_data_cleaned c
JOIN food_listings_data_cleaned f ON c.Food_ID = f.Food_ID
JOIN providers_data_cleaned p ON f.Provider_ID = p.Provider_ID
WHERE c.Status = 'Completed'
GROUP BY p.Name
ORDER BY Successful_Claims DESC
LIMIT 2;

SELECT Status,
       COUNT(*) * 100.0 / (SELECT COUNT(*) FROM claims_data_cleaned) AS Percentage
FROM claims_data_cleaned
GROUP BY Status;

SELECT r.Name, AVG(f.Quantity) AS Avg_Quantity_Claimed
FROM claims_data_cleaned c
JOIN receivers_data_cleaned r ON c.Receiver_ID = r.Receiver_ID
JOIN food_listings_data_cleaned f ON c.Food_ID = f.Food_ID
GROUP BY r.Name
ORDER BY Avg_Quantity_Claimed DESC;

SELECT f.Meal_Type, COUNT(c.Claim_ID) AS Total_Claims
FROM claims_data_cleaned c
JOIN food_listings_data_cleaned f ON c.Food_ID = f.Food_ID
GROUP BY f.Meal_Type
ORDER BY Total_Claims DESC;

SELECT p.Name, SUM(f.Quantity) AS Total_Donated
FROM food_listings_data_cleaned f
JOIN providers_data_cleaned p ON f.Provider_ID = p.Provider_ID
GROUP BY p.Name
ORDER BY Total_Donated DESC;




