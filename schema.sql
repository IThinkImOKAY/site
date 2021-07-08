--
-- PostgreSQL database dump
--

-- Dumped from database version 12.6
-- Dumped by pg_dump version 12.6

-- Started on 2021-07-08 18:00:46 CEST

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 205 (class 1259 OID 16417)
-- Name: Posts; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public."Posts" (
    id integer NOT NULL,
    title character varying(50),
    body character varying(10000),
    created_utc integer,
    creation_ip character varying(255),
    board_id integer,
    is_removed boolean DEFAULT false,
    removal_reason character varying(255),
    author_id integer,
    body_html text,
    parent_id integer,
    mentions integer[],
    last_bumped_utc integer DEFAULT date_part('epoch'::text, timezone('utc'::text, now()))
);


--
-- TOC entry 210 (class 1255 OID 17851)
-- Name: comment_count(public."Posts"); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.comment_count(public."Posts") RETURNS bigint
    LANGUAGE sql IMMUTABLE STRICT
    AS $_$
SELECT COUNT(*)
FROM "Posts"
WHERE parent_id=$1.id
$_$;


--
-- TOC entry 203 (class 1259 OID 16406)
-- Name: Boards; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public."Boards" (
    id integer NOT NULL,
    name character varying(5) NOT NULL,
    title character varying(25),
    created_utc integer NOT NULL,
    creation_ip character varying(255) NOT NULL,
    banned_utc integer DEFAULT 0,
    ban_reason character varying(255),
    creator_id integer,
    description character varying(255)
);


--
-- TOC entry 202 (class 1259 OID 16404)
-- Name: Boards_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public."Boards_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 3598 (class 0 OID 0)
-- Dependencies: 202
-- Name: Boards_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public."Boards_id_seq" OWNED BY public."Boards".id;


--
-- TOC entry 204 (class 1259 OID 16415)
-- Name: Posts_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public."Posts_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 3599 (class 0 OID 0)
-- Dependencies: 204
-- Name: Posts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public."Posts_id_seq" OWNED BY public."Posts".id;


--
-- TOC entry 207 (class 1259 OID 16494)
-- Name: Users; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public."Users" (
    id integer NOT NULL,
    username character varying(50),
    passhash character varying(750),
    created_utc integer,
    creation_ip character varying(255),
    is_admin boolean DEFAULT false,
    banned_by_id integer,
    banned_utc integer DEFAULT 0,
    ban_reason character varying(255),
    ban_expires_utc integer DEFAULT 0,
    deleted_utc integer DEFAULT 0
);


--
-- TOC entry 206 (class 1259 OID 16492)
-- Name: Users_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public."Users_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 3600 (class 0 OID 0)
-- Dependencies: 206
-- Name: Users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public."Users_id_seq" OWNED BY public."Users".id;


--
-- TOC entry 209 (class 1259 OID 18330)
-- Name: files; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.files (
    id integer NOT NULL,
    name character varying(100),
    path character varying(255),
    hash character varying(255),
    upload_ip character varying(255),
    upload_utc integer,
    post_id integer,
    url character varying(255),
    content_type character varying(50)
);


--
-- TOC entry 208 (class 1259 OID 18328)
-- Name: files_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.files_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 3601 (class 0 OID 0)
-- Dependencies: 208
-- Name: files_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.files_id_seq OWNED BY public.files.id;


--
-- TOC entry 3442 (class 2604 OID 16409)
-- Name: Boards id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."Boards" ALTER COLUMN id SET DEFAULT nextval('public."Boards_id_seq"'::regclass);


--
-- TOC entry 3444 (class 2604 OID 16420)
-- Name: Posts id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."Posts" ALTER COLUMN id SET DEFAULT nextval('public."Posts_id_seq"'::regclass);


--
-- TOC entry 3447 (class 2604 OID 16497)
-- Name: Users id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."Users" ALTER COLUMN id SET DEFAULT nextval('public."Users_id_seq"'::regclass);


--
-- TOC entry 3452 (class 2604 OID 18333)
-- Name: files id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.files ALTER COLUMN id SET DEFAULT nextval('public.files_id_seq'::regclass);


--
-- TOC entry 3454 (class 2606 OID 16414)
-- Name: Boards Boards_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."Boards"
    ADD CONSTRAINT "Boards_pkey" PRIMARY KEY (id);


--
-- TOC entry 3456 (class 2606 OID 16425)
-- Name: Posts Posts_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."Posts"
    ADD CONSTRAINT "Posts_pkey" PRIMARY KEY (id);


--
-- TOC entry 3458 (class 2606 OID 16507)
-- Name: Users Users_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."Users"
    ADD CONSTRAINT "Users_pkey" PRIMARY KEY (id);


--
-- TOC entry 3460 (class 2606 OID 18338)
-- Name: files files_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.files
    ADD CONSTRAINT files_pkey PRIMARY KEY (id);


--
-- TOC entry 3461 (class 2606 OID 16532)
-- Name: Boards Boards_creator_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."Boards"
    ADD CONSTRAINT "Boards_creator_id_fkey" FOREIGN KEY (creator_id) REFERENCES public."Users"(id);


--
-- TOC entry 3463 (class 2606 OID 16522)
-- Name: Posts Posts_author_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."Posts"
    ADD CONSTRAINT "Posts_author_id_fkey" FOREIGN KEY (author_id) REFERENCES public."Users"(id);


--
-- TOC entry 3462 (class 2606 OID 16426)
-- Name: Posts Posts_board_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."Posts"
    ADD CONSTRAINT "Posts_board_id_fkey" FOREIGN KEY (board_id) REFERENCES public."Boards"(id);


--
-- TOC entry 3464 (class 2606 OID 16558)
-- Name: Posts Posts_parent_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."Posts"
    ADD CONSTRAINT "Posts_parent_id_fkey" FOREIGN KEY (parent_id) REFERENCES public."Posts"(id);


--
-- TOC entry 3465 (class 2606 OID 16508)
-- Name: Users Users_banned_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."Users"
    ADD CONSTRAINT "Users_banned_by_id_fkey" FOREIGN KEY (banned_by_id) REFERENCES public."Users"(id);


--
-- TOC entry 3466 (class 2606 OID 18339)
-- Name: files files_post_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.files
    ADD CONSTRAINT files_post_id_fkey FOREIGN KEY (post_id) REFERENCES public."Posts"(id);


-- Completed on 2021-07-08 18:00:47 CEST

--
-- PostgreSQL database dump complete
--

