FROM python:3.10
RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev curl g++
RUN pip install --upgrade pip && pip install poetry && pip install dbt-core dbt-duckdb
RUN python -m pip install dbt-core dbt-duckdb
WORKDIR /home/healthcare_pricing
COPY ./ingestion ./ingestion
COPY ./dbt-duckdb ./dbt-duckdb

COPY pyproject.toml .

RUN poetry install --with dev && cd dbt-duckdb && dbt deps

CMD ["bash"]
