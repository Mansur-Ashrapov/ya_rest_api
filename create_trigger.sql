CREATE OR REPLACE FUNCTION main_items_upsert() RETURNS TRIGGER AS
$$
    BEGIN
        INSERT INTO history_of_item
            (id, url, date, parent_id, size, type)
        VALUES
            (NEW.id, NEW.url, NEW.date, NEW.parent_id, NEW.size, NEW.type)
        RETURN NEW;
    END;
$$
LANGUAGE plpgsql;

CREATE TRIGGER history_of_item
AFTER INSERT OR UPDATE ON main_items
    FOR EACH ROW EXECUTE FUNCTION main_items_upsert();