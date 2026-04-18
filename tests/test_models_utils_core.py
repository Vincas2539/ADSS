"""Additional tests for models and utility functions."""

from datetime import datetime

import pandas as pd
import pytest

from adss.models.metadata import Column, DatabaseMetadata, Schema, Table
from adss.models.query import Query, QueryResult
from adss.utils import format_permission


class TestQueryResultCore:
    def test_query_report_prints_fields(self, capsys):
        query = Query(
            id="q1",
            query_text="select 1",
            status="failed",
            created_at=datetime.utcnow(),
            completed_at=datetime.utcnow(),
            execution_time_ms=12,
            row_count=0,
            error="boom",
        )

        query.report()
        output = capsys.readouterr().out

        assert "Query ID: q1" in output
        assert "Status: failed" in output
        assert "Execution Time (ms): 12" in output
        assert "Row Count: 0" in output
        assert "Error: boom" in output

    def test_query_status_properties(self, mock_query_dict):
        mock_query_dict["status"] = "queued"
        queued = Query.from_dict(mock_query_dict)
        assert queued.is_queued is True
        assert queued.is_successful is False

        mock_query_dict["status"] = "failed"
        failed = Query.from_dict(mock_query_dict)
        assert failed.is_failed is True
        assert failed.is_complete is True

    def test_query_result_exports_and_views(self, tmp_path):
        query = Query(
            id="q1",
            query_text="select 1",
            status="completed",
            created_at=datetime.utcnow(),
        )
        df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
        result = QueryResult(query=query, data=df)

        csv_path = tmp_path / "result.csv"
        json_path = tmp_path / "result.json"
        parquet_path = tmp_path / "result.parquet"

        result.to_csv(str(csv_path), index=False)
        result.to_json(str(json_path), orient="records")
        result.to_parquet(str(parquet_path), index=False)

        assert csv_path.exists()
        assert json_path.exists()
        assert parquet_path.exists()
        assert len(result.head(2)) == 2
        assert len(result.tail(2)) == 2
        assert "a" in result.describe().columns


class TestMetadataCore:
    def test_metadata_lookup_helpers(self):
        table = Table(
            name="stars",
            columns=[
                Column(name="id", data_type="int", is_nullable=False),
                Column(name="name", data_type="text", is_nullable=True),
            ],
        )
        schema = Schema(name="public", tables=[table])
        dbmeta = DatabaseMetadata(schemas=[schema])

        assert table.get_column("id").name == "id"
        assert table.get_column("missing") is None
        assert table.has_column("name") is True
        assert table.column_names() == ["id", "name"]

        assert schema.get_table("stars").name == "stars"
        assert schema.get_table("missing") is None
        assert schema.has_table("stars") is True
        assert schema.table_names() == ["stars"]

        assert dbmeta.get_schema("public").name == "public"
        assert dbmeta.get_schema("missing") is None
        assert dbmeta.has_schema("public") is True
        assert dbmeta.schema_names() == ["public"]
        assert dbmeta.get_table("public", "stars").name == "stars"


class TestUtilsPermission:
    @pytest.mark.parametrize("permission", ["read", "write", "all", "READ"])
    def test_format_permission_valid(self, permission):
        assert format_permission(permission) in {"read", "write", "all"}

    def test_format_permission_invalid(self):
        with pytest.raises(ValueError):
            format_permission("drop")