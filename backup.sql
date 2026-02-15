--
-- PostgreSQL database dump
--

\restrict BQj7zHeyuwQOJBwVktoub6OkH1hLUm2Via8pb7B3bYmYBbyO5SCvTGleDAoeHWD

-- Dumped from database version 18.1
-- Dumped by pg_dump version 18.1

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

ALTER TABLE IF EXISTS ONLY public.quizzes DROP CONSTRAINT IF EXISTS quizzes_class_no_fkey;
ALTER TABLE IF EXISTS ONLY public.quiz_attempts DROP CONSTRAINT IF EXISTS quiz_attempts_student_id_fkey;
ALTER TABLE IF EXISTS ONLY public.quiz_attempts DROP CONSTRAINT IF EXISTS quiz_attempts_quiz_id_fkey;
ALTER TABLE IF EXISTS ONLY public.enrollments DROP CONSTRAINT IF EXISTS enrollments_student_id_fkey;
ALTER TABLE IF EXISTS ONLY public.enrollments DROP CONSTRAINT IF EXISTS enrollments_class_no_fkey;
ALTER TABLE IF EXISTS ONLY public.courses DROP CONSTRAINT IF EXISTS courses_faculty_id_fkey;
ALTER TABLE IF EXISTS ONLY public.classrooms DROP CONSTRAINT IF EXISTS classrooms_faculty_id_fkey;
ALTER TABLE IF EXISTS ONLY public.users DROP CONSTRAINT IF EXISTS users_pkey;
ALTER TABLE IF EXISTS ONLY public.users DROP CONSTRAINT IF EXISTS users_email_key;
ALTER TABLE IF EXISTS ONLY public.quizzes DROP CONSTRAINT IF EXISTS quizzes_pkey;
ALTER TABLE IF EXISTS ONLY public.quiz_attempts DROP CONSTRAINT IF EXISTS quiz_attempts_quiz_id_student_id_key;
ALTER TABLE IF EXISTS ONLY public.quiz_attempts DROP CONSTRAINT IF EXISTS quiz_attempts_pkey;
ALTER TABLE IF EXISTS ONLY public.question_bank DROP CONSTRAINT IF EXISTS question_bank_pkey;
ALTER TABLE IF EXISTS ONLY public.enrollments DROP CONSTRAINT IF EXISTS enrollments_student_id_class_no_key;
ALTER TABLE IF EXISTS ONLY public.enrollments DROP CONSTRAINT IF EXISTS enrollments_pkey;
ALTER TABLE IF EXISTS ONLY public.courses DROP CONSTRAINT IF EXISTS courses_pkey;
ALTER TABLE IF EXISTS ONLY public.classrooms DROP CONSTRAINT IF EXISTS classrooms_pkey;
ALTER TABLE IF EXISTS ONLY public.classrooms DROP CONSTRAINT IF EXISTS classrooms_class_no_key;
ALTER TABLE IF EXISTS public.users ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.quizzes ALTER COLUMN quiz_id DROP DEFAULT;
ALTER TABLE IF EXISTS public.quiz_attempts ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.question_bank ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.enrollments ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.courses ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.classrooms ALTER COLUMN id DROP DEFAULT;
DROP SEQUENCE IF EXISTS public.users_id_seq;
DROP TABLE IF EXISTS public.users;
DROP SEQUENCE IF EXISTS public.quizzes_quiz_id_seq;
DROP TABLE IF EXISTS public.quizzes;
DROP SEQUENCE IF EXISTS public.quiz_attempts_id_seq;
DROP TABLE IF EXISTS public.quiz_attempts;
DROP SEQUENCE IF EXISTS public.question_bank_id_seq;
DROP TABLE IF EXISTS public.question_bank;
DROP SEQUENCE IF EXISTS public.enrollments_id_seq;
DROP TABLE IF EXISTS public.enrollments;
DROP SEQUENCE IF EXISTS public.courses_id_seq;
DROP TABLE IF EXISTS public.courses;
DROP SEQUENCE IF EXISTS public.classrooms_id_seq;
DROP TABLE IF EXISTS public.classrooms;
DROP FUNCTION IF EXISTS public._lastval();
--
-- Name: _lastval(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public._lastval() RETURNS integer
    LANGUAGE plpgsql
    AS $$
                            BEGIN
                                BEGIN
                                    RETURN (SELECT LASTVAL());
                                EXCEPTION
                                    WHEN SQLSTATE '55000' THEN RETURN NULL;
                                END;
                            END $$;


ALTER FUNCTION public._lastval() OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: classrooms; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.classrooms (
    id integer NOT NULL,
    class_no text NOT NULL,
    faculty_id integer,
    nickname text,
    course_code text
);


ALTER TABLE public.classrooms OWNER TO postgres;

--
-- Name: classrooms_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.classrooms_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.classrooms_id_seq OWNER TO postgres;

--
-- Name: classrooms_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.classrooms_id_seq OWNED BY public.classrooms.id;


--
-- Name: courses; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.courses (
    id integer NOT NULL,
    name text NOT NULL,
    faculty_id integer
);


ALTER TABLE public.courses OWNER TO postgres;

--
-- Name: courses_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.courses_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.courses_id_seq OWNER TO postgres;

--
-- Name: courses_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.courses_id_seq OWNED BY public.courses.id;


--
-- Name: enrollments; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.enrollments (
    id integer NOT NULL,
    student_id integer,
    class_no text
);


ALTER TABLE public.enrollments OWNER TO postgres;

--
-- Name: enrollments_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.enrollments_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.enrollments_id_seq OWNER TO postgres;

--
-- Name: enrollments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.enrollments_id_seq OWNED BY public.enrollments.id;


--
-- Name: question_bank; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.question_bank (
    id integer NOT NULL,
    course_code text NOT NULL,
    question_text text NOT NULL,
    option_a text,
    option_b text,
    option_c text,
    option_d text,
    correct_answer text,
    marks numeric,
    minus numeric,
    created_by integer,
    created_at timestamp without time zone DEFAULT now()
);


ALTER TABLE public.question_bank OWNER TO postgres;

--
-- Name: question_bank_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.question_bank_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.question_bank_id_seq OWNER TO postgres;

--
-- Name: question_bank_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.question_bank_id_seq OWNED BY public.question_bank.id;


--
-- Name: quiz_attempts; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.quiz_attempts (
    id integer NOT NULL,
    quiz_id integer,
    student_id integer,
    answers jsonb,
    score integer,
    submitted_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    questions text
);


ALTER TABLE public.quiz_attempts OWNER TO postgres;

--
-- Name: quiz_attempts_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.quiz_attempts_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.quiz_attempts_id_seq OWNER TO postgres;

--
-- Name: quiz_attempts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.quiz_attempts_id_seq OWNED BY public.quiz_attempts.id;


--
-- Name: quizzes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.quizzes (
    quiz_id integer NOT NULL,
    title text NOT NULL,
    class_no text,
    total_marks integer,
    duration integer,
    data jsonb,
    status text DEFAULT 'draft'::text,
    start_time timestamp without time zone,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    source_type character varying(20) DEFAULT 'upload'::character varying,
    bank_count integer,
    bank_course_code text
);


ALTER TABLE public.quizzes OWNER TO postgres;

--
-- Name: quizzes_quiz_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.quizzes_quiz_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.quizzes_quiz_id_seq OWNER TO postgres;

--
-- Name: quizzes_quiz_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.quizzes_quiz_id_seq OWNED BY public.quizzes.quiz_id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    id integer NOT NULL,
    name text NOT NULL,
    email text NOT NULL,
    hash text NOT NULL,
    role text NOT NULL,
    reg_no text,
    contact text
);


ALTER TABLE public.users OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_id_seq OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: classrooms id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.classrooms ALTER COLUMN id SET DEFAULT nextval('public.classrooms_id_seq'::regclass);


--
-- Name: courses id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.courses ALTER COLUMN id SET DEFAULT nextval('public.courses_id_seq'::regclass);


--
-- Name: enrollments id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.enrollments ALTER COLUMN id SET DEFAULT nextval('public.enrollments_id_seq'::regclass);


--
-- Name: question_bank id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.question_bank ALTER COLUMN id SET DEFAULT nextval('public.question_bank_id_seq'::regclass);


--
-- Name: quiz_attempts id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.quiz_attempts ALTER COLUMN id SET DEFAULT nextval('public.quiz_attempts_id_seq'::regclass);


--
-- Name: quizzes quiz_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.quizzes ALTER COLUMN quiz_id SET DEFAULT nextval('public.quizzes_quiz_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Data for Name: classrooms; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.classrooms (id, class_no, faculty_id, nickname, course_code) FROM stdin;
7	CH2025	2	\N	BCSE302L
\.


--
-- Data for Name: courses; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.courses (id, name, faculty_id) FROM stdin;
\.


--
-- Data for Name: enrollments; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.enrollments (id, student_id, class_no) FROM stdin;
8	1	CH2025
\.


--
-- Data for Name: question_bank; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.question_bank (id, course_code, question_text, option_a, option_b, option_c, option_d, correct_answer, marks, minus, created_by, created_at) FROM stdin;
\.


--
-- Data for Name: quiz_attempts; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.quiz_attempts (id, quiz_id, student_id, answers, score, submitted_at, questions) FROM stdin;
9	3	1	["B", "D"]	5	2026-02-07 00:12:08	\N
\.


--
-- Data for Name: quizzes; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.quizzes (quiz_id, title, class_no, total_marks, duration, data, status, start_time, created_at, source_type, bank_count, bank_course_code) FROM stdin;
3	DMBS QUIZ 1	CH2025	5	5	[{"a": "3", "b": "4", "c": "5", "d": "6", "ques": "What is 2 + 2?", "marks": 1, "minus": 0, "answer": "B"}, {"a": "Hosted DBMS", "b": "NoSQL DB", "c": "Local DB", "d": "Cloud Distributed DB", "ques": "Microsoft Azure is an eg of", "marks": 4, "minus": 2, "answer": "D"}]	live	\N	2026-02-05 11:00:23.070733	upload	\N	\N
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (id, name, email, hash, role, reg_no, contact) FROM stdin;
1	K. Mahesh Chandran	maheshchandran.k2024@vitstudent.ac.in	scrypt:32768:8:1$40JVgAd9ut8cQvsY$dd082ef395f29f70af282b3ff24e8ecc2eb926b072e1133fe42e77157081c723da6a09bf56b3a08941451229a27b48574fdd32d519ce5faa9c16ef1b6f527ab2	student	24BAI1400	8591495253
2	Mahesh	kmahesh110606@outlook.com	scrypt:32768:8:1$Jyl5FdEejF0oqRd4$5d9cedea7724b50175961e0e4b951530e5fab9dd8572f2d41e75683e6a7767819e2140e861bedd89787cdc8e8f84a9a61c2616431af62dfb44bd8104a9d83503	faculty	5253	
6	mahesh	kmahesh110606@outlook.c	scrypt:32768:8:1$SONAFypDwuVmDevW$c1556f289885c45f69a6813326e73b9d939b303c3df6ae1e3492ca8733c3c19556485f5281eff7b0a6b1d98c5e9e087e5bdd480e1f7d07d3d265b0127feaf9ae	student	1234	1234
\.


--
-- Name: classrooms_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.classrooms_id_seq', 7, true);


--
-- Name: courses_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.courses_id_seq', 1, false);


--
-- Name: enrollments_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.enrollments_id_seq', 9, true);


--
-- Name: question_bank_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.question_bank_id_seq', 1, false);


--
-- Name: quiz_attempts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.quiz_attempts_id_seq', 9, true);


--
-- Name: quizzes_quiz_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.quizzes_quiz_id_seq', 3, true);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.users_id_seq', 6, true);


--
-- Name: classrooms classrooms_class_no_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.classrooms
    ADD CONSTRAINT classrooms_class_no_key UNIQUE (class_no);


--
-- Name: classrooms classrooms_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.classrooms
    ADD CONSTRAINT classrooms_pkey PRIMARY KEY (id);


--
-- Name: courses courses_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.courses
    ADD CONSTRAINT courses_pkey PRIMARY KEY (id);


--
-- Name: enrollments enrollments_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.enrollments
    ADD CONSTRAINT enrollments_pkey PRIMARY KEY (id);


--
-- Name: enrollments enrollments_student_id_class_no_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.enrollments
    ADD CONSTRAINT enrollments_student_id_class_no_key UNIQUE (student_id, class_no);


--
-- Name: question_bank question_bank_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.question_bank
    ADD CONSTRAINT question_bank_pkey PRIMARY KEY (id);


--
-- Name: quiz_attempts quiz_attempts_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.quiz_attempts
    ADD CONSTRAINT quiz_attempts_pkey PRIMARY KEY (id);


--
-- Name: quiz_attempts quiz_attempts_quiz_id_student_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.quiz_attempts
    ADD CONSTRAINT quiz_attempts_quiz_id_student_id_key UNIQUE (quiz_id, student_id);


--
-- Name: quizzes quizzes_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.quizzes
    ADD CONSTRAINT quizzes_pkey PRIMARY KEY (quiz_id);


--
-- Name: users users_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: classrooms classrooms_faculty_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.classrooms
    ADD CONSTRAINT classrooms_faculty_id_fkey FOREIGN KEY (faculty_id) REFERENCES public.users(id);


--
-- Name: courses courses_faculty_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.courses
    ADD CONSTRAINT courses_faculty_id_fkey FOREIGN KEY (faculty_id) REFERENCES public.users(id);


--
-- Name: enrollments enrollments_class_no_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.enrollments
    ADD CONSTRAINT enrollments_class_no_fkey FOREIGN KEY (class_no) REFERENCES public.classrooms(class_no);


--
-- Name: enrollments enrollments_student_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.enrollments
    ADD CONSTRAINT enrollments_student_id_fkey FOREIGN KEY (student_id) REFERENCES public.users(id);


--
-- Name: quiz_attempts quiz_attempts_quiz_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.quiz_attempts
    ADD CONSTRAINT quiz_attempts_quiz_id_fkey FOREIGN KEY (quiz_id) REFERENCES public.quizzes(quiz_id);


--
-- Name: quiz_attempts quiz_attempts_student_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.quiz_attempts
    ADD CONSTRAINT quiz_attempts_student_id_fkey FOREIGN KEY (student_id) REFERENCES public.users(id);


--
-- Name: quizzes quizzes_class_no_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.quizzes
    ADD CONSTRAINT quizzes_class_no_fkey FOREIGN KEY (class_no) REFERENCES public.classrooms(class_no);


--
-- PostgreSQL database dump complete
--

\unrestrict BQj7zHeyuwQOJBwVktoub6OkH1hLUm2Via8pb7B3bYmYBbyO5SCvTGleDAoeHWD

