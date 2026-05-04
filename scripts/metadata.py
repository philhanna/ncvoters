"""
Parser for NC Voter Layout Documentation File (layout_ncvoter.txt)
Reads directly from the S3 URL and extracts schema definitions, code
tables, and metadata, then adds tables to the database:

1. status_codes (maps `status_cd` to `status_name`)
2. race_codes (maps `race_code` to `race_name`)
3. ethnic_codes (maps `ethnic_code` to `ethnic_name`)
4. county_mapping (maps `county_id` to `county_name`)

These codes and mappings will be added to tables
in the database by the names of the four tables above.
"""

import re
import sqlite3
import sys
import tempfile
import requests
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import yaml

CONFIG_PATH = Path.home() / ".config" / "ncvoters" / "config.yaml"

@dataclass
class ColumnDefinition:
    """Represents a column definition from the layout"""
    name: str
    data_type: str
    description: str
    is_previous: bool = False
    version: str = "current"


@dataclass
class CodeTable:
    """Represents a code lookup table (status, race, ethnicity, county)"""
    name: str
    description: str
    codes: Dict[str, str]


class LayoutParser:
    """Parser for the NC voter layout documentation file from URL"""
    
    # Default URL for the layout file
    DEFAULT_URL = "https://s3.amazonaws.com/dl.ncsbe.gov/data/layout_ncvoter.txt"
    
    def __init__(self, timeout: int = 30):
        """
        Initialize the parser.
        
        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout
        self.current_version_date = None
        self.previous_version_dates = []
        self.columns: List[ColumnDefinition] = []
        self.code_tables: List[CodeTable] = []
        self.content = None
        
    def parse_from_url(self, url: str = None) -> Dict[str, Any]:
        """
        Parse the layout file directly from a URL.

        Args:
            url: URL to fetch from (uses DEFAULT_URL if not provided)

        Returns:
            Dictionary containing all extracted information
        """
        content = self.fetch_from_url(url)
        return self.parse_content(content)

    def fetch_from_url(self, url: str = None) -> str:
        """
        Fetch the layout file content from a URL.

        Args:
            url: URL to fetch from (uses DEFAULT_URL if not provided)

        Returns:
            File content as string

        Raises:
            requests.RequestException: If the fetch fails
        """
        if url is None:
            url = self.DEFAULT_URL
        self._last_url = url

        print(f"Fetching layout from: {url}")

        try:
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()  # Raise exception for bad status codes

            # Handle different encodings
            response.encoding = response.apparent_encoding or 'utf-8'

            print(f"Successfully fetched {len(response.text)} characters")
            self.content = response.text
            return response.text

        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to fetch layout file: {e}")
    
    def parse_content(self, content: str) -> Dict[str, Any]:
        """
        Parse layout content that has already been fetched.
        
        Args:
            content: The layout file content as a string
            
        Returns:
            Dictionary containing all extracted information
        """
        self.content = content
        
        return {
            'metadata': self._extract_metadata(content),
            'versions': self._extract_version_info(content),
            'columns': self._extract_all_columns(content),
            'code_tables': self._extract_code_tables(content),
            'county_mapping': self._extract_county_mapping(content),
            'url_source': getattr(self, '_last_url', self.DEFAULT_URL),
            'fetch_timestamp': datetime.now().isoformat()
        }
    
    def _extract_metadata(self, content: str) -> Dict[str, str]:
        """Extract file metadata from the header comments"""
        metadata = {}
        
        # Extract key metadata fields
        patterns = {
            'name': r'name:\s*(\S+)',
            'purpose': r'purpose:\s*(.+?)(?:\n\s*\*|$)',
            'updated': r'updated:\s*([0-9/]+)',
            'format': r'format:\s*(.+)'
        }
        
        for key, pattern in patterns.items():
            match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
            if match:
                value = match.group(1).strip()
                # Clean up multiline values
                if key == 'purpose':
                    value = ' '.join(value.split())
                metadata[key] = value
        
        return metadata
    
    def _extract_version_info(self, content: str) -> Dict[str, Any]:
        """Extract information about different file versions"""
        versions = {
            'current': {},
            'previous': [],
            'oldest': {}
        }
        
        # Find current version date
        current_match = re.search(r'File layout \(from ([0-9/]+)\)', content)
        if current_match:
            versions['current']['date'] = current_match.group(1)
            versions['current']['columns_start'] = self._find_section_start(content, "File layout (from")
        
        # Find previous version sections
        prev_sections = re.finditer(r'-- Previous file layout \(from ([0-9/]+) - ([0-9/]+)\)', content)
        for match in prev_sections:
            versions['previous'].append({
                'start_date': match.group(1),
                'end_date': match.group(2),
                'section_marker': match.group(0)
            })
        
        # Find oldest version
        oldest_match = re.search(r'-- Previous file layout \(until ([0-9/]+)\)', content)
        if oldest_match:
            versions['oldest']['end_date'] = oldest_match.group(1)
        
        return versions
    
    def _find_section_start(self, content: str, section_title: str) -> int:
        """Find the line number where a section starts"""
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if section_title in line:
                return i
        return -1
    
    def _extract_all_columns(self, content: str) -> Dict[str, List[ColumnDefinition]]:
        """Extract column definitions for all versions"""
        result = {
            'current': [],
            'previous_2022_2026': [],
            'oldest_pre_2022': []
        }
        
        # Split content by major sections (80+ dashes)
        sections = re.split(r'-{80,}', content)
        
        for section in sections:
            if re.search(r'File layout \(from', section) and not re.search(r'Previous file layout', section):
                result['current'] = self._parse_column_table(section, "current")
            elif re.search(r'Previous file layout \(from .+ - .+\)', section):
                result['previous_2022_2026'] = self._parse_column_table(section, "2022-2026")
            elif re.search(r'Previous file layout \(until', section):
                result['oldest_pre_2022'] = self._parse_column_table(section, "pre-2022")
        
        return result
    
    def _parse_column_table(self, section: str, version: str) -> List[ColumnDefinition]:
        """Parse a column definition table from a section"""
        columns = []
        
        # Find the table - it starts with "name" and has "---" separators
        lines = section.split('\n')
        in_table = False
        header_found = False
        
        for line in lines:
            line = line.strip()
            
            # Detect table start
            if line.startswith('name') and 'data type' in line and 'description' in line:
                in_table = True
                header_found = True
                continue
            
            # Skip separator lines
            if line.startswith('---') or not line:
                continue
            
            if in_table and header_found:
                # Parse column line - format: "column_name               type        description"
                parts = line.split()
                if len(parts) >= 3:
                    # Column name is first part
                    col_name = parts[0]
                    
                    # Data type is usually the second part, but might be multi-word like 'varchar(15)'
                    data_type = parts[1] if len(parts) > 1 else ""
                    
                    # Description is everything after the data type
                    description = ' '.join(parts[2:]) if len(parts) > 2 else ""
                    
                    # Clean up
                    data_type = data_type.replace('(', ' (').strip()
                    
                    columns.append(ColumnDefinition(
                        name=col_name,
                        data_type=data_type,
                        description=description,
                        is_previous=(version != "current"),
                        version=version
                    ))
        
        return columns
    
    def _extract_code_tables(self, content: str) -> List[CodeTable]:
        """Extract code tables (status, race, ethnicity) from the file"""
        tables = []
        
        # Status codes table
        status_section = self._extract_comment_section(content, "Status codes")
        status_table = self._parse_code_table(
            status_section,
            r'([A-Z]{1,3})\s+(.+)$'
        )
        if status_table:
            tables.append(CodeTable(
                name="status_codes",
                description="Voter registration status codes",
                codes=status_table
            ))
        
        # Race codes table
        race_section = self._extract_comment_section(content, "Race codes")
        race_table = self._parse_code_table(
            race_section,
            r'([A-Z]{1,3})\s+(.+)$'
        )
        if race_table:
            tables.append(CodeTable(
                name="race_codes",
                description="Race codes for voters",
                codes=race_table
            ))
        
        # Ethnic codes table
        ethnic_section = self._extract_comment_section(content, "Ethnic codes")
        ethnic_table = self._parse_code_table(
            ethnic_section,
            r'([A-Z]{1,3})\s+(.+)$'
        )
        if ethnic_table:
            tables.append(CodeTable(
                name="ethnic_codes",
                description="Ethnicity codes",
                codes=ethnic_table
            ))
        
        return tables
    
    def _extract_comment_section(self, content: str, title: str) -> str:
        """Extract the body of a titled comment block."""
        pattern = rf'/\*\s*\*+\s*{re.escape(title)}\s*(.*?)\*/'
        match = re.search(pattern, content, re.DOTALL)
        if not match:
            return ""
        return match.group(1)

    def _parse_code_table(self, section_text: str, line_pattern: str) -> Dict[str, str]:
        """Parse a code table from a comment section body."""
        if not section_text:
            return {}

        codes = {}
        
        for raw_line in section_text.splitlines():
            line = raw_line.strip()
            if not line or line.startswith("*"):
                continue
            if "description" in line.lower() or set(line) == {"*"}:
                continue

            match = re.match(line_pattern, line)
            if not match:
                continue

            code = match.group(1).strip()
            description = match.group(2).strip()

            if code and description and len(code) <= 3:
                codes[code] = description
        
        return codes
    
    def _extract_county_mapping(self, content: str) -> Dict[int, str]:
        """Extract the county ID to name mapping"""
        county_mapping = {}
        
        county_section = self._extract_comment_section(content, "County identification number codes")

        for raw_line in county_section.splitlines():
            line = raw_line.strip()
            if not line or line.startswith("*"):
                continue
            if "county_id" in line.lower() or set(line) == {"*"}:
                continue

            # Match patterns like "ALAMANCE            1" or "NEWHANOVER         65"
            match = re.match(r'([A-Z]+)\s+(\d{1,3})$', line)
            if not match:
                continue

            county_name = match.group(1)
            county_id = int(match.group(2))
            county_mapping[county_id] = county_name
        
        return county_mapping

    def _get_code_table(self, parsed_data: Dict[str, Any], table_name: str) -> CodeTable:
        """Return a named code table from parsed data."""
        for table in parsed_data["code_tables"]:
            if table.name == table_name:
                return table
        raise ValueError(f"Code table not found: {table_name}")

    def _recreate_lookup_table(
        self,
        conn: sqlite3.Connection,
        table_name: str,
        key_column: str,
        value_column: str,
        rows: List[tuple[Any, Any]],
    ) -> None:
        """Drop, recreate, and repopulate a two-column lookup table."""
        conn.execute(f"DROP TABLE IF EXISTS {table_name}")
        conn.execute(
            f"""
            CREATE TABLE {table_name} (
                {key_column} TEXT PRIMARY KEY,
                {value_column} TEXT NOT NULL
            )
            """
        )
        conn.executemany(
            f"INSERT INTO {table_name} ({key_column}, {value_column}) VALUES (?, ?)",
            rows,
        )
        conn.commit()
        print(f"  {table_name} - {len(rows)} rows", file=sys.stderr)

    def create_status_codes_table(
        self, conn: sqlite3.Connection, parsed_data: Dict[str, Any]
    ) -> None:
        """Create and populate the status_codes lookup table."""
        table = self._get_code_table(parsed_data, "status_codes")
        rows = sorted(table.codes.items())
        self._recreate_lookup_table(
            conn, "status_codes", "status_cd", "status_name", rows
        )

    def create_race_codes_table(
        self, conn: sqlite3.Connection, parsed_data: Dict[str, Any]
    ) -> None:
        """Create and populate the race_codes lookup table."""
        table = self._get_code_table(parsed_data, "race_codes")
        rows = sorted(table.codes.items())
        self._recreate_lookup_table(conn, "race_codes", "race_code", "race_name", rows)

    def create_ethnic_codes_table(
        self, conn: sqlite3.Connection, parsed_data: Dict[str, Any]
    ) -> None:
        """Create and populate the ethnic_codes lookup table."""
        table = self._get_code_table(parsed_data, "ethnic_codes")
        rows = sorted(table.codes.items())
        self._recreate_lookup_table(
            conn, "ethnic_codes", "ethnic_code", "ethnic_name", rows
        )

    def create_county_mapping_table(
        self, conn: sqlite3.Connection, parsed_data: Dict[str, Any]
    ) -> None:
        """Create and populate the county_mapping lookup table."""
        conn.execute("DROP TABLE IF EXISTS county_mapping")
        conn.execute(
            """
            CREATE TABLE county_mapping (
                county_id INTEGER PRIMARY KEY,
                county_name TEXT NOT NULL
            )
            """
        )
        rows = sorted(parsed_data["county_mapping"].items())
        conn.executemany(
            "INSERT INTO county_mapping (county_id, county_name) VALUES (?, ?)", rows
        )
        conn.commit()
        print(f"  county_mapping - {len(rows)} rows", file=sys.stderr)

    def apply_metadata_tables(self, db_path: str, parsed_data: Dict[str, Any]) -> None:
        """Create all metadata lookup tables in the target database."""
        print(f"Applying metadata tables to {db_path}", file=sys.stderr)
        conn = sqlite3.connect(db_path)
        try:
            self.create_status_codes_table(conn, parsed_data)
            self.create_race_codes_table(conn, parsed_data)
            self.create_ethnic_codes_table(conn, parsed_data)
            self.create_county_mapping_table(conn, parsed_data)
        finally:
            conn.close()
        print("Done.", file=sys.stderr)
    
    def get_column_names(self, version: str = "current") -> List[str]:
        """Get list of column names for a specific version"""
        if version == "current":
            return [col.name for col in self.columns if not col.is_previous]
        elif version == "2022-2026":
            # This would need version-specific parsing
            return []
        else:
            return []
    
    def get_column_by_name(self, name: str) -> Optional[ColumnDefinition]:
        """Find a column definition by name"""
        for col in self.columns:
            if col.name == name:
                return col
        return None
    
    def print_summary(self, parsed_data: Dict[str, Any]):
        """Print a human-readable summary of the layout"""
        print("=" * 70)
        print("NC VOTER FILE LAYOUT SUMMARY")
        print("=" * 70)
        
        # Source info
        print(f"\n🌐 SOURCE:")
        print(f"   URL: {parsed_data.get('url_source', 'Unknown')}")
        print(f"   Fetched: {parsed_data.get('fetch_timestamp', 'Unknown')}")
        
        # Metadata
        print("\n📋 FILE METADATA:")
        for key, value in parsed_data['metadata'].items():
            print(f"   {key.title()}: {value}")
        
        # Versions
        print(f"\n📅 VERSIONS:")
        print(f"   Current: {parsed_data['versions']['current'].get('date', 'Unknown')}")
        print(f"   Previous versions: {len(parsed_data['versions']['previous'])}")
        if parsed_data['versions']['previous']:
            for prev in parsed_data['versions']['previous']:
                print(f"     • {prev['start_date']} to {prev['end_date']}")
        
        # Columns
        print(f"\n📊 COLUMNS CURRENT VERSION:")
        current_cols = parsed_data['columns']['current']
        print(f"   Total columns: {len(current_cols)}")
        
        # Group columns by type for better overview
        string_cols = [c for c in current_cols if 'varchar' in c.data_type or 'char' in c.data_type]
        int_cols = [c for c in current_cols if 'int' in c.data_type]
        
        print(f"   String columns: {len(string_cols)}")
        print(f"   Integer columns: {len(int_cols)}")
        
        # Show first 10 columns
        if current_cols:
            print(f"\n   First 10 columns:")
            for col in current_cols[:10]:
                desc_preview = col.description[:50] + "..." if len(col.description) > 50 else col.description
                print(f"     • {col.name:<25} {col.data_type:<15} - {desc_preview}")
        
        # Code tables
        print(f"\n🔢 CODE TABLES:")
        for table in parsed_data['code_tables']:
            print(f"   • {table.name}: {len(table.codes)} codes")
            for code, desc in list(table.codes.items())[:5]:
                print(f"       {code} → {desc}")
            if len(table.codes) > 5:
                print(f"       ... and {len(table.codes) - 5} more")
        
        # County mapping
        print(f"\n🗺️  COUNTY MAPPING:")
        print(f"   Total counties: {len(parsed_data['county_mapping'])}")
        sample_counties = list(parsed_data['county_mapping'].items())[:10]
        for county_id, name in sample_counties:
            print(f"     {county_id:3d} → {name.title()}")
        if len(parsed_data['county_mapping']) > 10:
            print(f"     ... and {len(parsed_data['county_mapping']) - 10} more")
        
        print("\n" + "=" * 70)
    
    def export_json(self, parsed_data: Dict[str, Any], output_file: str = None) -> str:
        """
        Export parsed data to JSON format.
        
        Args:
            parsed_data: The parsed data dictionary
            output_file: Optional file path to write JSON to
            
        Returns:
            JSON string
        """
        import json
        
        # Convert dataclasses to dictionaries for JSON serialization
        json_data = {
            'metadata': parsed_data['metadata'],
            'versions': parsed_data['versions'],
            'columns': {
                'current': [
                    {'name': col.name, 'data_type': col.data_type, 'description': col.description}
                    for col in parsed_data['columns']['current']
                ],
                'previous_2022_2026': [
                    {'name': col.name, 'data_type': col.data_type, 'description': col.description}
                    for col in parsed_data['columns']['previous_2022_2026']
                ]
            },
            'code_tables': [
                {'name': table.name, 'description': table.description, 'codes': table.codes}
                for table in parsed_data['code_tables']
            ],
            'county_mapping': parsed_data['county_mapping'],
            'url_source': parsed_data.get('url_source'),
            'fetch_timestamp': parsed_data.get('fetch_timestamp')
        }
        
        json_str = json.dumps(json_data, indent=2)
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(json_str)
            print(f"JSON exported to: {output_file}")
        
        return json_str


def resolve_db_path(cli_arg: str | None) -> str:
    """Return the path to voter_data.db, in priority order."""
    if cli_arg:
        return cli_arg
    try:
        with open(CONFIG_PATH, encoding="utf-8") as f:
            config = yaml.safe_load(f)
        db_dir = config.get("db_dir")
        if db_dir:
            return str(Path(db_dir).expanduser() / "voter_data.db")
    except FileNotFoundError:
        pass
    return str(Path(tempfile.gettempdir()) / "voter_data.db")


def main() -> None:
    """Fetch the NC layout file and load lookup tables into SQLite."""
    db_path = resolve_db_path(sys.argv[1] if len(sys.argv) > 1 else None)
    url = sys.argv[2] if len(sys.argv) > 2 else None

    parser = LayoutParser()
    parsed_data = parser.parse_from_url(url)
    parser.apply_metadata_tables(db_path, parsed_data)


if __name__ == "__main__":
    main()
