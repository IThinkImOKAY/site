--
-- PostgreSQL database dump
--

-- Dumped from database version 12.6
-- Dumped by pg_dump version 12.6

-- Started on 2021-05-14 23:11:12 CEST

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
-- TOC entry 203 (class 1259 OID 16406)
-- Name: Boards; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public."Boards" (
    id integer NOT NULL,
    name character varying(5) NOT NULL,
    description text,
    created_utc integer NOT NULL,
    creation_ip character varying(255) NOT NULL,
    banned_utc integer DEFAULT 0,
    ban_reason character varying(255),
    creator_id integer
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
-- TOC entry 3597 (class 0 OID 0)
-- Dependencies: 202
-- Name: Boards_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public."Boards_id_seq" OWNED BY public."Boards".id;


--
-- TOC entry 207 (class 1259 OID 16433)
-- Name: Comments; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public."Comments" (
    id integer NOT NULL,
    body text,
    created_utc integer,
    creation_ip character varying(255),
    parent_id integer,
    is_removed boolean DEFAULT false,
    removal_reason character varying(255),
    author_id integer
);


--
-- TOC entry 206 (class 1259 OID 16431)
-- Name: Comments_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public."Comments_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 3598 (class 0 OID 0)
-- Dependencies: 206
-- Name: Comments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public."Comments_id_seq" OWNED BY public."Comments".id;


--
-- TOC entry 205 (class 1259 OID 16417)
-- Name: Posts; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public."Posts" (
    id integer NOT NULL,
    title character varying(50),
    body text,
    created_utc integer,
    creation_ip character varying(255),
    board_id integer,
    is_removed boolean DEFAULT false,
    removal_reason character varying(255),
    author_id integer
);


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
-- TOC entry 209 (class 1259 OID 16494)
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
-- TOC entry 208 (class 1259 OID 16492)
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
-- Dependencies: 208
-- Name: Users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public."Users_id_seq" OWNED BY public."Users".id;


--
-- TOC entry 3441 (class 2604 OID 16409)
-- Name: Boards id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."Boards" ALTER COLUMN id SET DEFAULT nextval('public."Boards_id_seq"'::regclass);


--
-- TOC entry 3445 (class 2604 OID 16436)
-- Name: Comments id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."Comments" ALTER COLUMN id SET DEFAULT nextval('public."Comments_id_seq"'::regclass);


--
-- TOC entry 3443 (class 2604 OID 16420)
-- Name: Posts id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."Posts" ALTER COLUMN id SET DEFAULT nextval('public."Posts_id_seq"'::regclass);


--
-- TOC entry 3447 (class 2604 OID 16497)
-- Name: Users id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."Users" ALTER COLUMN id SET DEFAULT nextval('public."Users_id_seq"'::regclass);


--
-- TOC entry 3453 (class 2606 OID 16414)
-- Name: Boards Boards_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."Boards"
    ADD CONSTRAINT "Boards_pkey" PRIMARY KEY (id);


--
-- TOC entry 3457 (class 2606 OID 16441)
-- Name: Comments Comments_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."Comments"
    ADD CONSTRAINT "Comments_pkey" PRIMARY KEY (id);


--
-- TOC entry 3455 (class 2606 OID 16425)
-- Name: Posts Posts_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."Posts"
    ADD CONSTRAINT "Posts_pkey" PRIMARY KEY (id);


--
-- TOC entry 3459 (class 2606 OID 16507)
-- Name: Users Users_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."Users"
    ADD CONSTRAINT "Users_pkey" PRIMARY KEY (id);


--
-- TOC entry 3460 (class 2606 OID 16532)
-- Name: Boards Boards_creator_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."Boards"
    ADD CONSTRAINT "Boards_creator_id_fkey" FOREIGN KEY (creator_id) REFERENCES public."Users"(id);


--
-- TOC entry 3464 (class 2606 OID 16527)
-- Name: Comments Comments_author_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."Comments"
    ADD CONSTRAINT "Comments_author_id_fkey" FOREIGN KEY (author_id) REFERENCES public."Users"(id);


--
-- TOC entry 3463 (class 2606 OID 16442)
-- Name: Comments Comments_parent_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."Comments"
    ADD CONSTRAINT "Comments_parent_id_fkey" FOREIGN KEY (parent_id) REFERENCES public."Posts"(id);


--
-- TOC entry 3462 (class 2606 OID 16522)
-- Name: Posts Posts_author_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."Posts"
    ADD CONSTRAINT "Posts_author_id_fkey" FOREIGN KEY (author_id) REFERENCES public."Users"(id);


--
-- TOC entry 3461 (class 2606 OID 16426)
-- Name: Posts Posts_board_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."Posts"
    ADD CONSTRAINT "Posts_board_id_fkey" FOREIGN KEY (board_id) REFERENCES public."Boards"(id);


--
-- TOC entry 3465 (class 2606 OID 16508)
-- Name: Users Users_banned_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."Users"
    ADD CONSTRAINT "Users_banned_by_id_fkey" FOREIGN KEY (banned_by_id) REFERENCES public."Users"(id);


-- Completed on 2021-05-14 23:11:12 CEST

--
-- PostgreSQL database dump complete
--

