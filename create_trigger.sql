CREATE OR REPLACE FUNCTION get_size_folder(root_id character varying) RETURNS integer AS
$$
    DECLARE
        size_add integer;
    BEGIN   
        WITH RECURSIVE sizes(id, parent_id, size, type) AS (
            SELECT id, parent_id, size, type
            FROM main_items
            where id = root_id
            UNION
            SELECT main_items.id, main_items.parent_id, main_items.size, main_items.type
            FROM main_items
                JOIN sizes
                    ON main_items.parent_id = sizes.id
        )
        SELECT sum(size) INTO STRICT size_add
            FROM sizes WHERE type = 'FILE';
        RETURN size_add;
    END;
$$
LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION main_item_update_size_and_date(root_id character varying, root_date bigint) RETURNS VOID AS
$$
    DECLARE
        size_add integer;
    BEGIN   
        size_add := get_size_folder(root_id);
        IF size_add not in (0) THEN
            UPDATE main_items SET size = size_add, date = root_date
                WHERE id = root_id;
        END IF;
    END;
$$
LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION main_items_delete_all_children(root_id character varying) RETURNS VOID AS
$$ 
    DECLARE
        child_id character varying;
    BEGIN   
        FOR child_id IN 
            WITH RECURSIVE children(id) AS (
                SELECT id
                FROM main_items
                where parent_id = root_id
                UNION
                SELECT main_items.id
                FROM main_items
                    JOIN children
                        ON main_items.parent_id = children.id
                )
                SELECT id FROM children
        LOOP
            DELETE FROM main_items WHERE id IN (child_id);
        END LOOP;
    END;
$$
LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION main_items_when_upsert() RETURNS TRIGGER AS $$
    BEGIN  
        IF (NEW.type = 'FOLDER' and NEW.size not in (0)) THEN
            INSERT INTO history_of_item
                (id, url, date, parent_id, size, type)
            VALUES
                (NEW.id, NEW.url, NEW.date, NEW.parent_id, NEW.size, NEW.type);
            PERFORM main_item_update_size_and_date(NEW.parent_id, NEW.date);
            RETURN NEW;
        ELSEIF (NEW.type = 'FILE') THEN
            INSERT INTO history_of_item
                (id, url, date, parent_id, size, type)
            VALUES
                (NEW.id, NEW.url, NEW.date, NEW.parent_id, NEW.size, NEW.type);
            PERFORM main_item_update_size_and_date(NEW.parent_id, NEW.date);
            PERFORM main_item_update_size_and_date(OLD.parent_id, NEW.date);
            RETURN NEW;
        ELSE
            INSERT INTO history_of_item
                (id, url, date, parent_id, size, type)
            VALUES
                (NEW.id, NEW.url, NEW.date, NEW.parent_id, NEW.size, NEW.type);
            PERFORM main_item_update_size_and_date(NEW.id, NEW.date);
            PERFORM main_item_update_size_and_date(NEW.parent_id, NEW.date);

        END IF;
        RETURN NEW;
    END;
$$ LANGUAGE plpgsql;



CREATE OR REPLACE FUNCTION custom_delete(root_id character varying, root_parent_id character varying, root_date bigint) RETURNS VOID AS $$
    DECLARE
        size_add integer;
    BEGIN
        DELETE FROM main_items WHERE id = root_id;
        size_add := get_size_folder(root_parent_id);
        UPDATE main_items SET size = size_add, date = root_date
            WHERE id = root_parent_id;
    END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION main_items_delete() RETURNS TRIGGER AS $$
    BEGIN  
        IF (OLD.type = 'FOLDER') THEN
            PERFORM main_items_delete_all_children(OLD.id);
        END IF;
        RETURN NULL;
    END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE TRIGGER history_item
AFTER INSERT OR UPDATE ON main_items
    FOR EACH ROW EXECUTE FUNCTION main_items_when_upsert();

CREATE OR REPLACE TRIGGER delete_main
AFTER DELETE ON main_items
    FOR EACH ROW EXECUTE FUNCTION main_items_delete();