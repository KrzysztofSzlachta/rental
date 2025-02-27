CREATE DATABASE rentals IF NOT EXISTS
    WITH
    OWNER = postgres
    ENCODING = 'UTF8'
    CONNECTION LIMIT = -1
    IS_TEMPLATE = False;

CREATE TABLE public.people
(
    "ID_person" integer,
    first_name text,
    surname text,
    pesel bigint,
    document_nr text,
    document_type text,
    birth_date date,
    PRIMARY KEY ("ID_person")
);

ALTER TABLE IF EXISTS public.people
    OWNER to postgres;

CREATE TABLE public.items
(
    "ID_item" integer,
    name text,
    description text,
    type text,
    adult_required boolean,
    PRIMARY KEY ("ID_item")
);

ALTER TABLE IF EXISTS public.items
    OWNER to postgres;

CREATE TABLE public.reservations
(
    "ID_reservation" integer,
    "ID_person" integer,
    "ID_item" integer,
    starting_time timestamp with time zone,
    ending_time timestamp with time zone,
    PRIMARY KEY ("ID_reservation")
);

ALTER TABLE IF EXISTS public.reservations
    OWNER to postgres;