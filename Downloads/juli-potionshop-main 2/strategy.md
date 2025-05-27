# Version 4: Potion Shop Strategy


## 1. Define Your Strategy


### 1. Track Failed Checkouts
- A customer tries to check out but can't because the product is missing or out of stock. I want to log the potion that caused that failure. This would help me understand which potion runs out and helps me adjust the brewing.


### 2. Abandoned Carts
- Sometimes customers add potions to the cart but never check out. I want to track when this happens and try to find out why. There could be different reasons why they would just leave. However, this would help me fix the problems and improve their experiences.


### 3.  Record Customer Class with Each Sale
- Each customer has a class, and I'll track which customer class buys what potions. From this, I can make better guesses on what to brew based on who is going to my shop.


---


## 2. Design Your Experiments


### Hypothesis 1 – Track Failed Checkouts
- **Track?**: Each time a customer tries to check out but fails because something happens to the potion (for example, missing).
- **Test?**: Comparing the potion stock to the types that show up in the failed checkout.
- **Success?**: If the failed checkout goes down, then this would have worked




### Hypothesis 2 – Abandoned Carts
- **Track?**: Customers create carts but never actually get checked out after a certain number of hours
- **Test?**: Look inside those and compare whether or not it's the prices or the inventory that's wrong
- **Success?**: If more carts get completed, from either fixing the prices or fixing the inventory, then the changes help


### Hypothesis 3 –  Record Customer Class with Each Sale
- **Track?**: Each sale, save the customer class.
- **Test?**: Count how many potions are being sold to each of those classes.
- **Success?**: If I make more potions that match what the top classes want, I'll save more.


---


## 3.Additional Instrumentation


To test these, start tracking which:
### Track failed checkouts
- First is to create the table to put each failed attempt
   - In the log there's:
   - potion
   - cart id
   - the time that was created
- By doing so, it will help me find out which potions frequently go out of stock and when.


### Log abandoned carts
- Check the carts that haven't checked out after a certain amount of hours
   - In the log there's:
   - cart ID
   - customer name
   - the time it was created
- It reveals if the price is too high and any gaps in the catalog.


### Track customer Class with what they brought
- When a potion is being brought, log the character class of the customer who brought it.
   - In the log there's:
       - customer with their class
       - potion
       - the time when they brought it
- Since this would let me see what each type of customer likes and help me make the potions tailored to what they want.


---


## 4. Analytics Queries


```sql
-- create a table to track failed checkouts
CREATE TABLE IF NOT EXISTS failed_checkouts (
   id SERIAL PRIMARY KEY,
   potion_sku TEXT NOT NULL,
   cart_id INT,
   timestamp TIMESTAMP DEFAULT NOW()
);


-- count failed checkouts by potion
SELECT potion_sku, COUNT(*) AS failed_count
FROM failed_checkouts
GROUP BY potion_sku;


-- list carts that were never checked out (abandoned)
SELECT id, customer_name, created_at
FROM carts
WHERE checked_out = FALSE
AND created_at < NOW() - INTERVAL '6 hours';


-- add customer class to the sales log (run once)
ALTER TABLE sales_log ADD COLUMN customer_class TEXT;


-- show which customer class buys which potion the most
SELECT customer_class, potion_sku, COUNT(*) AS bought_count
FROM sales_log
GROUP BY customer_class, potion_sku
ORDER BY customer_class, bought_count DESC;
