CREATE OR REPLACE TABLE raw_financial_events (
    event_id STRING,
    source_type STRING,        
    event_timestamp TIMESTAMP_NTZ,
    payload VARIANT,            -- Raw JSON payload
    ingestion_time TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

CREATE OR REPLACE TABLE stage_sp500 (
    ticker STRING,
    event_timestamp TIMESTAMP_NTZ,
    open FLOAT,
    high FLOAT,
    low FLOAT,
    close FLOAT,
    volume FLOAT
);

CREATE OR REPLACE TABLE stage_exchange_rates (
    base_currency STRING,
    event_timestamp TIMESTAMP_NTZ,
    currency STRING,
    rate FLOAT
);

CREATE OR REPLACE TABLE stage_crypto (
    rank INT,
    name STRING,
    symbol STRING,
    price STRING,
    change_24h STRING,
    market_cap STRING,
    volume_24h STRING,
    event_timestamp TIMESTAMP_NTZ
);


CREATE OR REPLACE TABLE data_pipeline_audit_log (
    id STRING,
    source STRING,
    lambda_function_name STRING,
    trigger_time TIMESTAMP_NTZ,
    status STRING,             
    message STRING,
    retry_count INT
);
