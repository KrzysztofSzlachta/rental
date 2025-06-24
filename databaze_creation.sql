-- Database: rentals

-- DROP DATABASE IF EXISTS rentals;

CREATE DATABASE rentals
    WITH
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'pl-PL'
    LC_CTYPE = 'pl-PL'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1
    IS_TEMPLATE = False;

-- Table: public.items

-- DROP TABLE IF EXISTS public.items;

CREATE TABLE IF NOT EXISTS public.items
(
    "ID_item" integer NOT NULL DEFAULT nextval('"items_ID_item_seq"'::regclass),
    name text COLLATE pg_catalog."default" NOT NULL,
    description text COLLATE pg_catalog."default",
    type text COLLATE pg_catalog."default" NOT NULL,
    adult_required boolean NOT NULL,
    deleted boolean NOT NULL DEFAULT false,
    CONSTRAINT items_pkey PRIMARY KEY ("ID_item")
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.items
    OWNER to postgres;

-- Table: public.people

-- DROP TABLE IF EXISTS public.people;

CREATE TABLE IF NOT EXISTS public.people
(
    "ID_person" integer NOT NULL DEFAULT nextval('"people_ID_person_seq"'::regclass),
    first_name text COLLATE pg_catalog."default" NOT NULL,
    surname text COLLATE pg_catalog."default" NOT NULL,
    pesel text COLLATE pg_catalog."default",
    document_nr text COLLATE pg_catalog."default",
    document_type text COLLATE pg_catalog."default",
    birth_date date NOT NULL,
    deleted boolean NOT NULL DEFAULT false,
    CONSTRAINT people_pkey PRIMARY KEY ("ID_person")
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.people
    OWNER to postgres;

-- Table: public.reservations

-- DROP TABLE IF EXISTS public.reservations;

CREATE TABLE IF NOT EXISTS public.reservations
(
    "ID_reservation" integer NOT NULL DEFAULT nextval('"reservations_ID_reservation_seq"'::regclass),
    "ID_person" integer NOT NULL,
    "ID_item" integer NOT NULL,
    starting_time timestamp with time zone NOT NULL,
    ending_time timestamp with time zone NOT NULL,
    deleted boolean NOT NULL DEFAULT false,
    CONSTRAINT reservations_pkey PRIMARY KEY ("ID_reservation"),
    CONSTRAINT "reservations_ID_item_fkey" FOREIGN KEY ("ID_item")
        REFERENCES public.items ("ID_item") MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
        NOT VALID,
    CONSTRAINT "reservations_ID_person_fkey" FOREIGN KEY ("ID_person")
        REFERENCES public.people ("ID_person") MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
        NOT VALID
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.reservations
    OWNER to postgres;