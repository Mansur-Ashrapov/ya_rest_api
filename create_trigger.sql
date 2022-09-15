


CREATE OR REPLACE FUNCTION main_items_upsert() RETURNS TRIGGER AS
$$
    DECLARE
        size_add integer;
        rec RECORD;
    BEGIN   
        size_add := 0;
        IF (NEW.type = 'FOLDER') THEN
            FOR rec IN 
                WITH RECURSIVE sizes(id, parent_id, size) AS (
                    SELECT id, parent_id, size
                    FROM main_items
                    where id = NEW.id

                    UNION 

                    SELECT main_items.id, main_items.parent_id, main_items.size
                    FROM main_items
                        JOIN sizes
                            ON main_items.parent_id = sizes.id
                )
                SELECT * FROM sizes
            LOOP
                size_add := rec.size + size_add;
            END LOOP;
        ELSE 
            size_add := NEW.size;
        END IF;
        INSERT INTO history_of_item
            (id, url, date, parent_id, size, type)
        VALUES
            (NEW.id, NEW.url, NEW.date, NEW.parent_id, size_add, NEW.type);
        RETURN NEW;
    END;
$$
LANGUAGE plpgsql;

CREATE TRIGGER history_of_item
AFTER INSERT OR UPDATE ON main_items
    FOR EACH ROW EXECUTE FUNCTION main_items_upsert();
