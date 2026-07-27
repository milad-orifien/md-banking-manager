--
-- PostgreSQL database dump
--

\restrict erPx3wqGAwxraAVq7SpdMLVU4xAQSgX3bHWcEiFeMgtxqowdEKuJ0b2F79mT44X

-- Dumped from database version 18.3
-- Dumped by pg_dump version 18.3

-- Started on 2026-07-25 16:16:07 CEST

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
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
-- TOC entry 231 (class 1259 OID 22123)
-- Name: benutzergruppe; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.benutzergruppe (
    gruppenid integer NOT NULL,
    gruppenname character varying(100) NOT NULL,
    erstellt_von integer NOT NULL,
    erstellt_am timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE public.benutzergruppe OWNER TO postgres;

--
-- TOC entry 230 (class 1259 OID 22122)
-- Name: benutzergruppe_gruppenid_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.benutzergruppe_gruppenid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.benutzergruppe_gruppenid_seq OWNER TO postgres;

--
-- TOC entry 3957 (class 0 OID 0)
-- Dependencies: 230
-- Name: benutzergruppe_gruppenid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.benutzergruppe_gruppenid_seq OWNED BY public.benutzergruppe.gruppenid;


--
-- TOC entry 234 (class 1259 OID 22159)
-- Name: gruppeneinladung; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.gruppeneinladung (
    einladungid integer NOT NULL,
    gruppenid integer NOT NULL,
    erstellt_von integer NOT NULL,
    empfaengerid integer NOT NULL,
    token character varying(100) NOT NULL,
    angenommen boolean DEFAULT false NOT NULL,
    erstellt_am timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE public.gruppeneinladung OWNER TO postgres;

--
-- TOC entry 233 (class 1259 OID 22158)
-- Name: gruppeneinladung_einladungid_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.gruppeneinladung_einladungid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.gruppeneinladung_einladungid_seq OWNER TO postgres;

--
-- TOC entry 3958 (class 0 OID 0)
-- Dependencies: 233
-- Name: gruppeneinladung_einladungid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.gruppeneinladung_einladungid_seq OWNED BY public.gruppeneinladung.einladungid;


--
-- TOC entry 232 (class 1259 OID 22139)
-- Name: gruppenmitglied; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.gruppenmitglied (
    gruppenid integer NOT NULL,
    kundenid integer NOT NULL,
    beigetreten_am timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE public.gruppenmitglied OWNER TO postgres;

--
-- TOC entry 225 (class 1259 OID 22059)
-- Name: kategorie; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.kategorie (
    kategorieid integer NOT NULL,
    kundenid integer NOT NULL,
    bezeichnung character varying(80) NOT NULL,
    ist_standard boolean DEFAULT false NOT NULL
);


ALTER TABLE public.kategorie OWNER TO postgres;

--
-- TOC entry 224 (class 1259 OID 22058)
-- Name: kategorie_kategorieid_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.kategorie_kategorieid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.kategorie_kategorieid_seq OWNER TO postgres;

--
-- TOC entry 3959 (class 0 OID 0)
-- Dependencies: 224
-- Name: kategorie_kategorieid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.kategorie_kategorieid_seq OWNED BY public.kategorie.kategorieid;


--
-- TOC entry 223 (class 1259 OID 22040)
-- Name: konto; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.konto (
    kontoid integer NOT NULL,
    kundenid integer NOT NULL,
    kontoname character varying(100) NOT NULL,
    erstellt_am timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE public.konto OWNER TO postgres;

--
-- TOC entry 222 (class 1259 OID 22039)
-- Name: konto_kontoid_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.konto_kontoid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.konto_kontoid_seq OWNER TO postgres;

--
-- TOC entry 3960 (class 0 OID 0)
-- Dependencies: 222
-- Name: konto_kontoid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.konto_kontoid_seq OWNED BY public.konto.kontoid;


--
-- TOC entry 229 (class 1259 OID 22095)
-- Name: kontoeintrag; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.kontoeintrag (
    eintragid integer NOT NULL,
    kontoid integer NOT NULL,
    kategorieid integer,
    wertstellungsdatum timestamp without time zone NOT NULL,
    betrag numeric(12,2) NOT NULL,
    empfaenger character varying(200) NOT NULL,
    verwendungszweck text NOT NULL,
    erstellt_am timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT kontoeintrag_betrag_check CHECK ((betrag <> (0)::numeric))
);


ALTER TABLE public.kontoeintrag OWNER TO postgres;

--
-- TOC entry 228 (class 1259 OID 22094)
-- Name: kontoeintrag_eintragid_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.kontoeintrag_eintragid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.kontoeintrag_eintragid_seq OWNER TO postgres;

--
-- TOC entry 3961 (class 0 OID 0)
-- Dependencies: 228
-- Name: kontoeintrag_eintragid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.kontoeintrag_eintragid_seq OWNED BY public.kontoeintrag.eintragid;


--
-- TOC entry 220 (class 1259 OID 22010)
-- Name: kunde; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.kunde (
    kundenid integer NOT NULL,
    email character varying(100) NOT NULL,
    vorname character varying(50) NOT NULL,
    nachname character varying(100) NOT NULL,
    alter integer,
    bankinstitut character varying(100),
    erstellt_am timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT kunde_alter_check CHECK (((alter IS NULL) OR ((alter >= 1) AND (alter <= 119))))
);


ALTER TABLE public.kunde OWNER TO postgres;

--
-- TOC entry 219 (class 1259 OID 22009)
-- Name: kunde_kundenid_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.kunde_kundenid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.kunde_kundenid_seq OWNER TO postgres;

--
-- TOC entry 3962 (class 0 OID 0)
-- Dependencies: 219
-- Name: kunde_kundenid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.kunde_kundenid_seq OWNED BY public.kunde.kundenid;


--
-- TOC entry 236 (class 1259 OID 22192)
-- Name: nachricht; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.nachricht (
    nachrichtid integer NOT NULL,
    absenderid integer NOT NULL,
    empfaengerid integer NOT NULL,
    betreff character varying(150) NOT NULL,
    inhalt text NOT NULL,
    einladungid integer,
    gelesen boolean DEFAULT false NOT NULL,
    gesendet_am timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE public.nachricht OWNER TO postgres;

--
-- TOC entry 235 (class 1259 OID 22191)
-- Name: nachricht_nachrichtid_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.nachricht_nachrichtid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.nachricht_nachrichtid_seq OWNER TO postgres;

--
-- TOC entry 3963 (class 0 OID 0)
-- Dependencies: 235
-- Name: nachricht_nachrichtid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.nachricht_nachrichtid_seq OWNED BY public.nachricht.nachrichtid;


--
-- TOC entry 221 (class 1259 OID 22025)
-- Name: passwort; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.passwort (
    kundenid integer NOT NULL,
    passwort_hash text NOT NULL
);


ALTER TABLE public.passwort OWNER TO postgres;

--
-- TOC entry 227 (class 1259 OID 22078)
-- Name: schlagwort; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.schlagwort (
    schlagwortid integer NOT NULL,
    kategorieid integer NOT NULL,
    wort character varying(100) NOT NULL
);


ALTER TABLE public.schlagwort OWNER TO postgres;

--
-- TOC entry 226 (class 1259 OID 22077)
-- Name: schlagwort_schlagwortid_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.schlagwort_schlagwortid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.schlagwort_schlagwortid_seq OWNER TO postgres;

--
-- TOC entry 3964 (class 0 OID 0)
-- Dependencies: 226
-- Name: schlagwort_schlagwortid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.schlagwort_schlagwortid_seq OWNED BY public.schlagwort.schlagwortid;


--
-- TOC entry 3722 (class 2604 OID 22126)
-- Name: benutzergruppe gruppenid; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.benutzergruppe ALTER COLUMN gruppenid SET DEFAULT nextval('public.benutzergruppe_gruppenid_seq'::regclass);


--
-- TOC entry 3725 (class 2604 OID 22162)
-- Name: gruppeneinladung einladungid; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.gruppeneinladung ALTER COLUMN einladungid SET DEFAULT nextval('public.gruppeneinladung_einladungid_seq'::regclass);


--
-- TOC entry 3717 (class 2604 OID 22062)
-- Name: kategorie kategorieid; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.kategorie ALTER COLUMN kategorieid SET DEFAULT nextval('public.kategorie_kategorieid_seq'::regclass);


--
-- TOC entry 3715 (class 2604 OID 22043)
-- Name: konto kontoid; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.konto ALTER COLUMN kontoid SET DEFAULT nextval('public.konto_kontoid_seq'::regclass);


--
-- TOC entry 3720 (class 2604 OID 22098)
-- Name: kontoeintrag eintragid; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.kontoeintrag ALTER COLUMN eintragid SET DEFAULT nextval('public.kontoeintrag_eintragid_seq'::regclass);


--
-- TOC entry 3713 (class 2604 OID 22013)
-- Name: kunde kundenid; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.kunde ALTER COLUMN kundenid SET DEFAULT nextval('public.kunde_kundenid_seq'::regclass);


--
-- TOC entry 3728 (class 2604 OID 22195)
-- Name: nachricht nachrichtid; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.nachricht ALTER COLUMN nachrichtid SET DEFAULT nextval('public.nachricht_nachrichtid_seq'::regclass);


--
-- TOC entry 3719 (class 2604 OID 22081)
-- Name: schlagwort schlagwortid; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.schlagwort ALTER COLUMN schlagwortid SET DEFAULT nextval('public.schlagwort_schlagwortid_seq'::regclass);


--
-- TOC entry 3946 (class 0 OID 22123)
-- Dependencies: 231
-- Data for Name: benutzergruppe; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.benutzergruppe (gruppenid, gruppenname, erstellt_von, erstellt_am) FROM stdin;
1	WG Finanzen	1	2026-07-25 15:19:27.195462
\.


--
-- TOC entry 3949 (class 0 OID 22159)
-- Dependencies: 234
-- Data for Name: gruppeneinladung; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.gruppeneinladung (einladungid, gruppenid, erstellt_von, empfaengerid, token, angenommen, erstellt_am) FROM stdin;
\.


--
-- TOC entry 3947 (class 0 OID 22139)
-- Dependencies: 232
-- Data for Name: gruppenmitglied; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.gruppenmitglied (gruppenid, kundenid, beigetreten_am) FROM stdin;
1	1	2026-07-25 15:19:27.195462
1	2	2026-07-25 15:19:27.195462
\.


--
-- TOC entry 3940 (class 0 OID 22059)
-- Dependencies: 225
-- Data for Name: kategorie; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.kategorie (kategorieid, kundenid, bezeichnung, ist_standard) FROM stdin;
1	1	Nicht kategorisiert	t
2	1	Einkaufen	t
3	1	Miete	t
5	1	Freizeit	t
6	1	Gehalt	t
7	2	Nicht kategorisiert	t
8	2	Einkaufen	t
9	2	Miete	t
10	2	Mobilität	t
11	2	Freizeit	t
12	2	Gehalt	t
13	3	Nicht kategorisiert	t
14	3	Einkaufen	t
15	3	Miete	t
16	3	Mobilität	t
17	3	Freizeit	t
18	3	Gehalt	t
4	1	Mobilität	t
31	4	Nicht kategorisiert	t
32	4	Einkaufen	t
33	4	Miete	t
34	4	Mobilität	t
35	4	Freizeit	t
36	4	Gehalt	t
\.


--
-- TOC entry 3938 (class 0 OID 22040)
-- Dependencies: 223
-- Data for Name: konto; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.konto (kontoid, kundenid, kontoname, erstellt_am) FROM stdin;
1	1	Girokonto	2026-07-25 15:19:27.195462
2	1	Sparkonto	2026-07-25 15:19:27.195462
3	2	Girokonto	2026-07-25 15:19:27.195462
4	3	Alltagskonto	2026-07-25 15:19:27.195462
6	4	Girokonto	2026-07-25 16:03:07.092576
\.


--
-- TOC entry 3944 (class 0 OID 22095)
-- Dependencies: 229
-- Data for Name: kontoeintrag; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.kontoeintrag (eintragid, kontoid, kategorieid, wertstellungsdatum, betrag, empfaenger, verwendungszweck, erstellt_am) FROM stdin;
1	1	6	2026-07-25 12:00:00	2450.00	Arbeitgeber GmbH	Gehalt Juli	2026-07-25 15:19:27.195462
2	1	2	2026-07-22 12:00:00	-62.45	EDEKA Hildesheim	Wocheneinkauf	2026-07-25 15:19:27.195462
3	1	3	2026-07-19 12:00:00	-740.00	Hausverwaltung Nord	Miete Juli	2026-07-25 15:19:27.195462
4	1	5	2026-07-16 12:00:00	-18.99	Netflix	Monatsabo	2026-07-25 15:19:27.195462
5	1	4	2026-07-13 12:00:00	-54.10	ARAL	Tanken	2026-07-25 15:19:27.195462
6	1	1	2026-07-10 12:00:00	-12.80	Campus Mensa	Mittagessen	2026-07-25 15:19:27.195462
7	1	2	2026-07-07 12:00:00	-31.50	LIDL	Lebensmittel	2026-07-25 15:19:27.195462
8	1	5	2026-07-04 12:00:00	-9.90	Kino Hildesheim	Kinokarte	2026-07-25 15:19:27.195462
9	1	4	2026-07-01 12:00:00	-29.00	Deutsche Bahn	Fahrkarte	2026-07-25 15:19:27.195462
10	1	2	2026-06-28 12:00:00	-15.20	EDEKA	Getränke	2026-07-25 15:19:27.195462
11	1	1	2026-06-25 12:00:00	-8.50	Bäckerei	Frühstück	2026-07-25 15:19:27.195462
12	1	2	2026-06-22 12:00:00	-47.80	ALDI	Wocheneinkauf	2026-07-25 15:19:27.195462
13	1	1	2026-06-19 12:00:00	-22.00	Sportverein	Monatsbeitrag	2026-07-25 15:19:27.195462
14	1	4	2026-06-16 12:00:00	-13.40	SHELL	Tanken	2026-07-25 15:19:27.195462
15	1	1	2026-06-13 12:00:00	-6.99	Streamingdienst	Musikabo	2026-07-25 15:19:27.195462
16	1	2	2026-06-10 12:00:00	-28.70	LIDL	Lebensmittel	2026-07-25 15:19:27.195462
17	1	1	2026-06-07 12:00:00	-45.00	Restaurant	Abendessen	2026-07-25 15:19:27.195462
18	1	5	2026-06-04 12:00:00	-19.50	Kino	Filmabend	2026-07-25 15:19:27.195462
19	1	1	2026-06-01 12:00:00	-7.20	Campus Mensa	Mittagessen	2026-07-25 15:19:27.195462
20	1	2	2026-05-29 12:00:00	-36.10	EDEKA	Wocheneinkauf	2026-07-25 15:19:27.195462
21	6	31	2026-05-29 12:00:00	-36.10	EDEKA	Wocheneinkauf	2026-07-25 16:03:14.170787
22	6	31	2026-06-01 12:00:00	-7.20	Campus Mensa	Mittagessen	2026-07-25 16:03:14.224565
23	6	31	2026-06-04 12:00:00	-19.50	Kino	Filmabend	2026-07-25 16:03:14.281185
24	6	31	2026-06-07 12:00:00	-45.00	Restaurant	Abendessen	2026-07-25 16:03:14.329201
25	6	31	2026-06-10 12:00:00	-28.70	LIDL	Lebensmittel	2026-07-25 16:03:14.371358
26	6	31	2026-06-13 12:00:00	-6.99	Streamingdienst	Musikabo	2026-07-25 16:03:14.409969
27	6	31	2026-06-16 12:00:00	-13.40	SHELL	Tanken	2026-07-25 16:03:14.455046
28	6	31	2026-06-19 12:00:00	-22.00	Sportverein	Monatsbeitrag	2026-07-25 16:03:14.503378
29	6	31	2026-06-22 12:00:00	-47.80	ALDI	Wocheneinkauf	2026-07-25 16:03:14.561647
30	6	31	2026-06-25 12:00:00	-8.50	Bäckerei	Frühstück	2026-07-25 16:03:14.619642
31	6	31	2026-06-28 12:00:00	-15.20	EDEKA	Getränke	2026-07-25 16:03:14.678311
32	6	31	2026-07-01 12:00:00	-29.00	Deutsche Bahn	Fahrkarte	2026-07-25 16:03:14.735281
33	6	31	2026-07-04 12:00:00	-9.90	Kino Hildesheim	Kinokarte	2026-07-25 16:03:14.790114
34	6	31	2026-07-07 12:00:00	-31.50	LIDL	Lebensmittel	2026-07-25 16:03:14.854819
35	6	31	2026-07-10 12:00:00	-12.80	Campus Mensa	Mittagessen	2026-07-25 16:03:14.911207
36	6	31	2026-07-13 12:00:00	-54.10	ARAL	Tanken	2026-07-25 16:03:14.971892
37	6	31	2026-07-16 12:00:00	-18.99	Netflix	Monatsabo	2026-07-25 16:03:15.031572
38	6	31	2026-07-19 12:00:00	-740.00	Hausverwaltung Nord	Miete Juli	2026-07-25 16:03:15.090701
39	6	31	2026-07-22 12:00:00	-62.45	EDEKA Hildesheim	Wocheneinkauf	2026-07-25 16:03:15.146301
40	6	31	2026-07-25 12:00:00	2450.00	Arbeitgeber GmbH	Gehalt Juli	2026-07-25 16:03:15.196784
41	6	31	2026-07-25 16:04:00	-240.87	Uni	Semesterbeitrag	2026-07-25 16:04:16.162435
\.


--
-- TOC entry 3935 (class 0 OID 22010)
-- Dependencies: 220
-- Data for Name: kunde; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.kunde (kundenid, email, vorname, nachname, alter, bankinstitut, erstellt_am) FROM stdin;
1	anna.mueller@example.com	Anna	Müller	28	Sparkasse	2026-07-25 15:19:27.195462
2	ben.schmidt@example.com	Ben	Schmidt	35	Volksbank	2026-07-25 15:19:27.195462
3	clara.weiss@example.com	Clara	Weiß	22	\N	2026-07-25 15:19:27.195462
4	milad.orifien@gmail.com	Milad	Orifien	24	C24 Bank	2026-07-25 15:58:10.916821
\.


--
-- TOC entry 3951 (class 0 OID 22192)
-- Dependencies: 236
-- Data for Name: nachricht; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.nachricht (nachrichtid, absenderid, empfaengerid, betreff, inhalt, einladungid, gelesen, gesendet_am) FROM stdin;
\.


--
-- TOC entry 3936 (class 0 OID 22025)
-- Dependencies: 221
-- Data for Name: passwort; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.passwort (kundenid, passwort_hash) FROM stdin;
1	pbkdf2:sha256:600000$kxFfXwWTTRuwel06$e61845313aac37caff1566c4b21e45086bb8187a2565d19fac8730154b124c1a
2	pbkdf2:sha256:600000$CAfOgPIRXE0AlYfT$0a8cefc4617149a6cb8ed0fabaf78e1110eff20a1813dfa3bb97eaa1f82ebc34
3	pbkdf2:sha256:600000$8NQVVXazuqcKQgy4$d485a6ea50a9f524b5b95349386543813d55aba0a82ba41cf2b3a51ea0b3aab6
4	pbkdf2:sha256:600000$SccKSeniHcc35pHD$ec755ab17c6d09db6b9c2e42e1547030473a53efa57c2b91b61b8a73104b9c82
\.


--
-- TOC entry 3942 (class 0 OID 22078)
-- Dependencies: 227
-- Data for Name: schlagwort; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.schlagwort (schlagwortid, kategorieid, wort) FROM stdin;
1	2	EDEKA
2	2	ALDI
3	2	LIDL
4	4	ARAL
5	4	SHELL
6	4	DEUTSCHE BAHN
7	5	NETFLIX
8	5	KINO
9	6	GEHALT
10	3	MIETE
11	8	EDEKA
12	8	ALDI
13	8	LIDL
14	10	ARAL
15	10	SHELL
16	10	DEUTSCHE BAHN
17	11	NETFLIX
18	11	KINO
19	12	GEHALT
20	9	MIETE
21	14	EDEKA
22	14	ALDI
23	14	LIDL
24	16	ARAL
25	16	SHELL
26	16	DEUTSCHE BAHN
27	17	NETFLIX
28	17	KINO
29	18	GEHALT
30	15	MIETE
\.


--
-- TOC entry 3965 (class 0 OID 0)
-- Dependencies: 230
-- Name: benutzergruppe_gruppenid_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.benutzergruppe_gruppenid_seq', 1, true);


--
-- TOC entry 3966 (class 0 OID 0)
-- Dependencies: 233
-- Name: gruppeneinladung_einladungid_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.gruppeneinladung_einladungid_seq', 1, false);


--
-- TOC entry 3967 (class 0 OID 0)
-- Dependencies: 224
-- Name: kategorie_kategorieid_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.kategorie_kategorieid_seq', 54, true);


--
-- TOC entry 3968 (class 0 OID 0)
-- Dependencies: 222
-- Name: konto_kontoid_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.konto_kontoid_seq', 6, true);


--
-- TOC entry 3969 (class 0 OID 0)
-- Dependencies: 228
-- Name: kontoeintrag_eintragid_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.kontoeintrag_eintragid_seq', 41, true);


--
-- TOC entry 3970 (class 0 OID 0)
-- Dependencies: 219
-- Name: kunde_kundenid_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.kunde_kundenid_seq', 4, true);


--
-- TOC entry 3971 (class 0 OID 0)
-- Dependencies: 235
-- Name: nachricht_nachrichtid_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.nachricht_nachrichtid_seq', 1, false);


--
-- TOC entry 3972 (class 0 OID 0)
-- Dependencies: 226
-- Name: schlagwort_schlagwortid_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.schlagwort_schlagwortid_seq', 30, true);


--
-- TOC entry 3761 (class 2606 OID 22133)
-- Name: benutzergruppe benutzergruppe_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.benutzergruppe
    ADD CONSTRAINT benutzergruppe_pkey PRIMARY KEY (gruppenid);


--
-- TOC entry 3766 (class 2606 OID 22173)
-- Name: gruppeneinladung gruppeneinladung_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.gruppeneinladung
    ADD CONSTRAINT gruppeneinladung_pkey PRIMARY KEY (einladungid);


--
-- TOC entry 3768 (class 2606 OID 22175)
-- Name: gruppeneinladung gruppeneinladung_token_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.gruppeneinladung
    ADD CONSTRAINT gruppeneinladung_token_key UNIQUE (token);


--
-- TOC entry 3763 (class 2606 OID 22147)
-- Name: gruppenmitglied gruppenmitglied_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.gruppenmitglied
    ADD CONSTRAINT gruppenmitglied_pkey PRIMARY KEY (gruppenid, kundenid);


--
-- TOC entry 3747 (class 2606 OID 22071)
-- Name: kategorie kategorie_kundenid_bezeichnung_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.kategorie
    ADD CONSTRAINT kategorie_kundenid_bezeichnung_key UNIQUE (kundenid, bezeichnung);


--
-- TOC entry 3749 (class 2606 OID 22069)
-- Name: kategorie kategorie_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.kategorie
    ADD CONSTRAINT kategorie_pkey PRIMARY KEY (kategorieid);


--
-- TOC entry 3742 (class 2606 OID 22052)
-- Name: konto konto_kundenid_kontoname_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.konto
    ADD CONSTRAINT konto_kundenid_kontoname_key UNIQUE (kundenid, kontoname);


--
-- TOC entry 3744 (class 2606 OID 22050)
-- Name: konto konto_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.konto
    ADD CONSTRAINT konto_pkey PRIMARY KEY (kontoid);


--
-- TOC entry 3759 (class 2606 OID 22111)
-- Name: kontoeintrag kontoeintrag_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.kontoeintrag
    ADD CONSTRAINT kontoeintrag_pkey PRIMARY KEY (eintragid);


--
-- TOC entry 3734 (class 2606 OID 22024)
-- Name: kunde kunde_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.kunde
    ADD CONSTRAINT kunde_email_key UNIQUE (email);


--
-- TOC entry 3736 (class 2606 OID 22022)
-- Name: kunde kunde_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.kunde
    ADD CONSTRAINT kunde_pkey PRIMARY KEY (kundenid);


--
-- TOC entry 3771 (class 2606 OID 22208)
-- Name: nachricht nachricht_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.nachricht
    ADD CONSTRAINT nachricht_pkey PRIMARY KEY (nachrichtid);


--
-- TOC entry 3739 (class 2606 OID 22033)
-- Name: passwort passwort_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.passwort
    ADD CONSTRAINT passwort_pkey PRIMARY KEY (kundenid);


--
-- TOC entry 3753 (class 2606 OID 22088)
-- Name: schlagwort schlagwort_kategorieid_wort_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.schlagwort
    ADD CONSTRAINT schlagwort_kategorieid_wort_key UNIQUE (kategorieid, wort);


--
-- TOC entry 3755 (class 2606 OID 22086)
-- Name: schlagwort schlagwort_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.schlagwort
    ADD CONSTRAINT schlagwort_pkey PRIMARY KEY (schlagwortid);


--
-- TOC entry 3757 (class 1259 OID 22225)
-- Name: idx_eintrag_konto_datum; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_eintrag_konto_datum ON public.kontoeintrag USING btree (kontoid, wertstellungsdatum DESC);


--
-- TOC entry 3764 (class 1259 OID 22228)
-- Name: idx_gruppenmitglied_kundenid; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_gruppenmitglied_kundenid ON public.gruppenmitglied USING btree (kundenid);


--
-- TOC entry 3745 (class 1259 OID 22226)
-- Name: idx_kategorie_kundenid; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_kategorie_kundenid ON public.kategorie USING btree (kundenid);


--
-- TOC entry 3740 (class 1259 OID 22224)
-- Name: idx_konto_kundenid; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_konto_kundenid ON public.konto USING btree (kundenid);


--
-- TOC entry 3769 (class 1259 OID 22229)
-- Name: idx_nachricht_empfaenger; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_nachricht_empfaenger ON public.nachricht USING btree (empfaengerid, gesendet_am DESC);


--
-- TOC entry 3751 (class 1259 OID 22227)
-- Name: idx_schlagwort_kategorieid; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_schlagwort_kategorieid ON public.schlagwort USING btree (kategorieid);


--
-- TOC entry 3750 (class 1259 OID 22231)
-- Name: uq_kategorie_kunde_name_ci; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX uq_kategorie_kunde_name_ci ON public.kategorie USING btree (kundenid, lower((bezeichnung)::text));


--
-- TOC entry 3737 (class 1259 OID 22230)
-- Name: uq_kunde_email_ci; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX uq_kunde_email_ci ON public.kunde USING btree (lower((email)::text));


--
-- TOC entry 3756 (class 1259 OID 22232)
-- Name: uq_schlagwort_kategorie_wort_ci; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX uq_schlagwort_kategorie_wort_ci ON public.schlagwort USING btree (kategorieid, lower((wort)::text));


--
-- TOC entry 3778 (class 2606 OID 22134)
-- Name: benutzergruppe benutzergruppe_erstellt_von_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.benutzergruppe
    ADD CONSTRAINT benutzergruppe_erstellt_von_fkey FOREIGN KEY (erstellt_von) REFERENCES public.kunde(kundenid) ON DELETE CASCADE;


--
-- TOC entry 3781 (class 2606 OID 22186)
-- Name: gruppeneinladung gruppeneinladung_empfaengerid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.gruppeneinladung
    ADD CONSTRAINT gruppeneinladung_empfaengerid_fkey FOREIGN KEY (empfaengerid) REFERENCES public.kunde(kundenid) ON DELETE CASCADE;


--
-- TOC entry 3782 (class 2606 OID 22181)
-- Name: gruppeneinladung gruppeneinladung_erstellt_von_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.gruppeneinladung
    ADD CONSTRAINT gruppeneinladung_erstellt_von_fkey FOREIGN KEY (erstellt_von) REFERENCES public.kunde(kundenid) ON DELETE CASCADE;


--
-- TOC entry 3783 (class 2606 OID 22176)
-- Name: gruppeneinladung gruppeneinladung_gruppenid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.gruppeneinladung
    ADD CONSTRAINT gruppeneinladung_gruppenid_fkey FOREIGN KEY (gruppenid) REFERENCES public.benutzergruppe(gruppenid) ON DELETE CASCADE;


--
-- TOC entry 3779 (class 2606 OID 22148)
-- Name: gruppenmitglied gruppenmitglied_gruppenid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.gruppenmitglied
    ADD CONSTRAINT gruppenmitglied_gruppenid_fkey FOREIGN KEY (gruppenid) REFERENCES public.benutzergruppe(gruppenid) ON DELETE CASCADE;


--
-- TOC entry 3780 (class 2606 OID 22153)
-- Name: gruppenmitglied gruppenmitglied_kundenid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.gruppenmitglied
    ADD CONSTRAINT gruppenmitglied_kundenid_fkey FOREIGN KEY (kundenid) REFERENCES public.kunde(kundenid) ON DELETE CASCADE;


--
-- TOC entry 3774 (class 2606 OID 22072)
-- Name: kategorie kategorie_kundenid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.kategorie
    ADD CONSTRAINT kategorie_kundenid_fkey FOREIGN KEY (kundenid) REFERENCES public.kunde(kundenid) ON DELETE CASCADE;


--
-- TOC entry 3773 (class 2606 OID 22053)
-- Name: konto konto_kundenid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.konto
    ADD CONSTRAINT konto_kundenid_fkey FOREIGN KEY (kundenid) REFERENCES public.kunde(kundenid) ON DELETE CASCADE;


--
-- TOC entry 3776 (class 2606 OID 22117)
-- Name: kontoeintrag kontoeintrag_kategorieid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.kontoeintrag
    ADD CONSTRAINT kontoeintrag_kategorieid_fkey FOREIGN KEY (kategorieid) REFERENCES public.kategorie(kategorieid) ON DELETE SET NULL;


--
-- TOC entry 3777 (class 2606 OID 22112)
-- Name: kontoeintrag kontoeintrag_kontoid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.kontoeintrag
    ADD CONSTRAINT kontoeintrag_kontoid_fkey FOREIGN KEY (kontoid) REFERENCES public.konto(kontoid) ON DELETE CASCADE;


--
-- TOC entry 3784 (class 2606 OID 22209)
-- Name: nachricht nachricht_absenderid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.nachricht
    ADD CONSTRAINT nachricht_absenderid_fkey FOREIGN KEY (absenderid) REFERENCES public.kunde(kundenid) ON DELETE CASCADE;


--
-- TOC entry 3785 (class 2606 OID 22219)
-- Name: nachricht nachricht_einladungid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.nachricht
    ADD CONSTRAINT nachricht_einladungid_fkey FOREIGN KEY (einladungid) REFERENCES public.gruppeneinladung(einladungid) ON DELETE SET NULL;


--
-- TOC entry 3786 (class 2606 OID 22214)
-- Name: nachricht nachricht_empfaengerid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.nachricht
    ADD CONSTRAINT nachricht_empfaengerid_fkey FOREIGN KEY (empfaengerid) REFERENCES public.kunde(kundenid) ON DELETE CASCADE;


--
-- TOC entry 3772 (class 2606 OID 22034)
-- Name: passwort passwort_kundenid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.passwort
    ADD CONSTRAINT passwort_kundenid_fkey FOREIGN KEY (kundenid) REFERENCES public.kunde(kundenid) ON DELETE CASCADE;


--
-- TOC entry 3775 (class 2606 OID 22089)
-- Name: schlagwort schlagwort_kategorieid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.schlagwort
    ADD CONSTRAINT schlagwort_kategorieid_fkey FOREIGN KEY (kategorieid) REFERENCES public.kategorie(kategorieid) ON DELETE CASCADE;


-- Completed on 2026-07-25 16:16:07 CEST

--
-- PostgreSQL database dump complete
--

\unrestrict erPx3wqGAwxraAVq7SpdMLVU4xAQSgX3bHWcEiFeMgtxqowdEKuJ0b2F79mT44X

