"""
BigQueryManager Module

This module provides an interface to interact with Google BigQuery, allowing users to execute
SQL queries and optionally save query results to a specified destination table.

Modules:
--------
- os: Provides operating system dependent functionality.
- dotenv: Loads environment variables from a .env file.
- google.cloud.bigquery: Provides access to BigQuery API.

Classes:
--------
- BigQueryManager: A class that manages queries to BigQuery with options to store results.

Usage:
------
1. Set environment variables in a `.env` file:
   - `GCP_SERVICE_ACCOUNT_JSON_KEY_PATH`: Path to the GCP service account JSON key.
   - `PROJECT_ID`: Google Cloud project ID.
   - `DATASET_ID`: BigQuery dataset ID.

2. Example usage:

    ```python
    from bigquery_manager import BigQueryManager

    bq_manager = BigQueryManager(project_id="your_project_id", dataset_id="your_dataset_id")
    
    query = \"\"\"
    SELECT s.Name
    FROM your_project_id.your_dataset.Students AS s
    WHERE s.WarningCount > 0;
    \"\"\"

    data = bq_manager.execute_query(query)
    print(data)
    ```

Functions:
----------
- `execute_query(query: str, destination_table: Optional[str] = None) -> Optional[pd.DataFrame]`:
    Executes a SQL query on BigQuery. 
    - If `destination_table` is provided, results are stored in the specified table.
    - If not, results are returned as a Pandas DataFrame.

Dependencies:
-------------
- Install the required dependencies via pip:
    ```bash
    pip install google-cloud-bigquery python-dotenv pandas
    ```

Notes:
------
- Ensure the GCP service account JSON key file is correctly configured and accessible.
- The script should be run in an environment where Google Cloud SDK is set up.

"""

import os
from dotenv import load_dotenv
from google.cloud import bigquery
from google.cloud.bigquery.table import RowIterator

load_dotenv()
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv(
    "GCP_SERVICE_ACCOUNT_JSON_KEY_PATH"
)

PROJECT_ID = os.getenv("PROJECT_ID")
DATASET_ID = os.getenv("DATASET_ID")


class BigQueryManager:
    """
    A class to handle interactions with Google BigQuery.

    Attributes:
    -----------
    - project_id (str): The Google Cloud project ID.
    - dataset_id (str): The BigQuery dataset ID.

    Methods:
    --------
    - execute_query(query, destination_table=None):
        Executes a SQL query and optionally saves the result to a table.
    """

    def __init__(self, project_id, dataset_id):
        self.client = bigquery.Client()
        self.project_id = project_id
        self.dataset_id = dataset_id

    def execute_query(self, query, destination_table=None):
        """
        Run a query. Optionally save the results to a table or return the result as a DataFrame.
        """
        job_config = bigquery.QueryJobConfig()

        # Handle destination table for non-DDL queries
        if destination_table and not query.strip().lower().startswith(
            ("create", "alter")
        ):
            table_ref = f"{self.project_id}.{self.dataset_id}.{destination_table}"
            job_config.destination = table_ref
            job_config.write_disposition = bigquery.WriteDisposition.WRITE_TRUNCATE

        query_job = self.client.query(query, job_config=job_config)
        result: RowIterator = query_job.result()  # Wait for the query to complete

        # Return DataFrame if no destination_table is provided
        if not destination_table:
            return result.to_dataframe()

        return None

# Usage
if __name__ == "__main__":

    # Instantiate BigQueryManager with the project and dataset IDs
    bq_manager = BigQueryManager(project_id=PROJECT_ID, dataset_id=DATASET_ID)

    # Example: Run a query to create or fetch data
    QUERY = """
    SELECT s.Name
    FROM llm-testing-447813.LLM.Students AS s
    WHERE s.WarningCount > 0;
    """
    data = bq_manager.execute_query(QUERY)
    print(data)
