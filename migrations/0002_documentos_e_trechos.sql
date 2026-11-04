CREATE TABLE documentos (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    origem text NOT NULL,
    titulo text NOT NULL,
    conteudo text NOT NULL,
    hash text NOT NULL,
    criado_em timestamptz NOT NULL DEFAULT now(),
    UNIQUE (origem, hash)
);

CREATE TABLE trechos (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    documento_id bigint NOT NULL REFERENCES documentos (id) ON DELETE CASCADE,
    ordem integer NOT NULL,
    conteudo text NOT NULL,
    UNIQUE (documento_id, ordem)
);
