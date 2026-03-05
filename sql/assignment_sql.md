### t_insertQueueName

A trigger that will, before a insert in the match table, read the QueueID column and
accordingly set the queue name. Purpose of this is to have

```sql
DELIMITER $$
CREATE TRIGGER t_insertQueueName
BEFORE INSERT ON matches
FOR EACH ROW
BEGIN
    IF NEW.QueueID = 400 THEN
        SET NEW.queueName = "Normal SR";
    ELSEIF NEW.QueueID = 420 THEN
        SET NEW.queueName = "Ranked SR";
    ELSE
        SET NEW.queueName = "Unknown";
    END IF;
END$$
DELIMITER ;
```
