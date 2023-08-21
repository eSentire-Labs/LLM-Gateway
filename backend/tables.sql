--
-- Name: chatgpt_logs; Type: TABLE; Schema: llm_logs
--

CREATE TABLE "llm_logs".chatgpt_logs (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    request jsonb,
    usage_info jsonb,
    user_name text,
    title text,
    response_time timestamp without time zone DEFAULT now(),
    response jsonb,
    convo_title text,
    convo_show boolean DEFAULT true,
    root_gpt_id text
);


--
-- Name: COLUMN chatgpt_logs.root_gpt_id; Type: COMMENT; Schema: llm_logs
--

COMMENT ON COLUMN "llm_logs".chatgpt_logs.root_gpt_id IS 'id returned from llm endpoint, used to link multiple interactions into a single conversation';


--
-- Name: COLUMN chatgpt_logs.convo_title; Type: COMMENT; Schema: llm_logs
--

COMMENT ON COLUMN "llm_logs".chatgpt_logs.convo_title IS 'title for the conversation that is being had';


--
-- Name: COLUMN chatgpt_logs.convo_show; Type: COMMENT; Schema: llm_logs
--

COMMENT ON COLUMN "llm_logs".chatgpt_logs.convo_show IS 'whether you want a conversation to be shown in your histories';


--
-- Name: image_logs; Type: TABLE; Schema: llm_logs
--

CREATE TABLE "llm_logs".image_logs (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    request jsonb,
    response jsonb,
    usage_cost real,
    user_name text,
    title text,
    response_time timestamp without time zone DEFAULT now()
);


--
-- Name: chatgpt_logs chatgpt_logs_id_user_name_key; Type: CONSTRAINT; Schema: llm_logs
--

ALTER TABLE ONLY "llm_logs".chatgpt_logs
    ADD CONSTRAINT chatgpt_logs_id_user_name_key UNIQUE (id, user_name);


--
-- Name: chatgpt_logs chatgpt_logs_pkey; Type: CONSTRAINT; Schema: llm_logs
--

ALTER TABLE ONLY "llm_logs".chatgpt_logs
    ADD CONSTRAINT chatgpt_logs_pkey PRIMARY KEY (id);


--
-- Name: image_logs image_logs_id_user_name_key; Type: CONSTRAINT; Schema: llm_logs; Owner
--

ALTER TABLE ONLY "llm_logs".image_logs
    ADD CONSTRAINT image_logs_id_user_name_key UNIQUE (id, user_name);


--
-- Name: image_logs image_logs_pkey; Type: CONSTRAINT; Schema: llm_logs
--

ALTER TABLE ONLY "llm_logs".image_logs
    ADD CONSTRAINT image_logs_pkey PRIMARY KEY (id);