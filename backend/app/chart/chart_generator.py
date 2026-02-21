"""Chart data generator from Excel files"""
import json
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum


class ChartType(Enum):
    """Supported chart types"""
    PIE = "pie"
    BAR = "bar"
    LINE = "line"
    SCATTER = "scatter"


class ChartGenerator:
    """Generate chart configurations from Excel data"""

    def __init__(self, file_path: str):
        """
        Initialize chart generator with an Excel file path.

        Args:
            file_path: Path to the Excel file
        """
        self.file_path = file_path
        self.df = None
        self._load_data()

    def _find_best_column_match(self, target: str, candidate_columns: list) -> Optional[str]:
        """
        Find the best matching column from candidates using fuzzy matching.

        Args:
            target: The column name to find (e.g., "sales", "region")
            candidate_columns: List of available column names

        Returns:
            Best matching column name or None
        """
        import logging
        target_lower = target.lower().strip()

        logging.info(f"_find_best_column_match called: target='{target}', candidates={candidate_columns}")

        # Direct match
        for col in candidate_columns:
            if col.lower() == target_lower:
                logging.info(f"Direct match found: '{col}' for target '{target}'")
                return col

        # Substring match
        for col in candidate_columns:
            if target_lower in col.lower() or col.lower() in target_lower:
                logging.info(f"Substring match found: '{col}' for target '{target}'")
                return col

        # Semantic mapping for common terms
        # Keywords are prioritized - first match wins
        mappings = {
            'sales': ['total', 'sales', 'revenue', 'amount', 'price', 'quantity', 'count'],
            'region': ['region', 'area', 'location', 'place', 'zone', 'territory'],
            'date': ['date', 'time', 'day', 'month', 'year'],
            'product': ['product', 'item', 'name', 'title'],
            'price': ['price', 'cost', 'amount', 'unit price', 'total'],
            'quantity': ['quantity', 'qty', 'count', 'number', 'amount'],
            'total': ['total', 'sum', 'amount', 'sales', 'revenue'],
        }

        if target_lower in mappings:
            logging.info(f"Using semantic mapping for target '{target}': {mappings[target_lower]}")
            for keyword in mappings[target_lower]:
                for col in candidate_columns:
                    # More precise matching: keyword should match as a whole word or exact match
                    # Avoid partial matches like "sales" matching "sales rep"
                    col_lower = col.lower()
                    # Check for exact match or keyword surrounded by word boundaries
                    if col_lower == keyword or keyword == col_lower:
                        logging.info(f"Exact match found: '{col}' for target '{target}' (via keyword '{keyword}')")
                        return col
                    # For longer column names, check if keyword is a separate word
                    if keyword in col_lower:
                        # Check that keyword is a whole word (surrounded by spaces or at start/end)
                        # and not part of another word like "sales" in "sales rep"
                        if (col_lower.startswith(keyword + ' ') or
                            col_lower.endswith(' ' + keyword) or
                            ' ' + keyword + ' ' in col_lower):
                            logging.info(f"Word-boundary match found: '{col}' for target '{target}' (via keyword '{keyword}')")
                            return col

        logging.warning(f"No match found for target '{target}' in columns {candidate_columns}")
        return None

    def _load_data(self):
        """Load data from Excel file"""
        try:
            self.df = pd.read_excel(self.file_path)
            # Clean column names - strip whitespace and convert to lowercase
            self.df.columns = [str(col).strip().lower() for col in self.df.columns]

            # Only convert columns that are actually numeric strings (not text columns)
            for col in self.df.columns:
                if not pd.api.types.is_numeric_dtype(self.df[col]):
                    # Check if this column contains primarily numeric-like values before converting
                    # Sample the column and see if most values can be converted to numbers
                    sample = self.df[col].dropna().head(20)
                    if len(sample) > 0:
                        try:
                            converted = pd.to_numeric(sample, errors='coerce')
                            # Only convert if more than 80% of values are actually numeric
                            # This prevents converting text columns to NaN
                            if converted.notna().sum() / len(converted) > 0.8:
                                self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
                        except Exception:
                            pass

            import logging
            logging.info(f"Loaded Excel file with {len(self.df)} rows and {len(self.df.columns)} columns")
            logging.info(f"Columns: {list(self.df.columns)}")
            logging.info(f"Data types: {self.df.dtypes.to_dict()}")

        except Exception as e:
            import logging
            logging.error(f"Failed to load Excel file: {e}")
            raise ValueError(f"Failed to load Excel file: {str(e)}")

    def get_column_info(self) -> List[Dict[str, Any]]:
        """
        Get information about columns in the dataset.

        Returns:
            List of column info dictionaries
        """
        if self.df is None:
            return []

        columns = []
        for col in self.df.columns:
            dtype = str(self.df[col].dtype)
            sample_values = self.df[col].dropna().head(3).tolist()
            columns.append({
                "name": col,
                "type": "numeric" if pd.api.types.is_numeric_dtype(self.df[col]) else "categorical",
                "dtype": dtype,
                "sample_values": sample_values
            })
        return columns

    def find_suitable_columns(self) -> Dict[str, List[str]]:
        """
        Find columns suitable for different chart types.

        Returns:
            Dict mapping chart types to suitable column lists
        """
        if self.df is None:
            return {}

        numeric_cols = [
            col for col in self.df.columns
            if pd.api.types.is_numeric_dtype(self.df[col])
        ]

        # Also check if any non-numeric columns have convertible numeric data
        for col in self.df.columns:
            if col not in numeric_cols and not pd.api.types.is_numeric_dtype(self.df[col]):
                # Check if this column has at least some numeric-like values
                sample = self.df[col].dropna().head(10)
                if len(sample) > 0:
                    # Try to convert to numeric
                    try:
                        converted = pd.to_numeric(sample, errors='coerce')
                        # If more than 80% converted successfully, treat as numeric
                        # Higher threshold to avoid misclassifying categorical columns with some numeric-looking values
                        if converted.notna().sum() / len(converted) > 0.8:
                            numeric_cols.append(col)
                    except Exception:
                        pass

        # Also check numeric columns to ensure they have meaningful numeric values
        # (not all zeros, all same values, or very few unique values)
        true_numeric_cols = []
        for col in numeric_cols:
            if pd.api.types.is_numeric_dtype(self.df[col]):
                # Get non-null numeric values
                numeric_vals = self.df[col].dropna()
                if len(numeric_vals) > 0:
                    # Check for column characteristics:
                    # 1. Has more than 2 unique values (to avoid binary flags)
                    # 2. Range of values > 0 (to avoid constant columns)
                    # 3. Mean/median is meaningful
                    unique_vals = numeric_vals.nunique()
                    val_range = numeric_vals.max() - numeric_vals.min()
                    # Column is truly numeric if it has sufficient variation
                    if unique_vals > 2 and val_range > 0:
                        true_numeric_cols.append(col)
                    else:
                        # Column might be categorical despite being stored as numeric
                        import logging
                        logging.info(f"Column '{col}' treated as categorical (unique={unique_vals}, range={val_range})")

        categorical_cols = [
            col for col in self.df.columns
            if col not in true_numeric_cols
        ]

        import logging
        logging.info(f"Numeric columns: {true_numeric_cols}")
        logging.info(f"Categorical columns: {categorical_cols}")

        return {
            "numeric": true_numeric_cols,
            "categorical": categorical_cols
        }

    def generate_pie_chart(
        self,
        label_column: Optional[str] = None,
        value_column: Optional[str] = None,
        top_n: int = 10
    ) -> Dict[str, Any]:
        """
        Generate pie chart configuration.

        Args:
            label_column: Column to use for labels (categories)
            value_column: Column to use for values (numbers)
            top_n: Maximum number of slices to show

        Returns:
            Chart configuration dict for Recharts
        """
        if self.df is None:
            raise ValueError("No data loaded")

        suitable = self.find_suitable_columns()
        import logging
        logging.info(f"generate_pie_chart called with label={label_column}, value={value_column}")
        logging.info(f"Available columns: {list(self.df.columns)}")
        logging.info(f"Numeric: {suitable['numeric']}, Categorical: {suitable['categorical']}")

        # Auto-detect columns if not provided
        if label_column is None:
            # For pie charts, prefer categorical columns that are likely to be good labels
            # Priority: region, category, type, name, product, or first categorical
            # Use semantic matching via _find_best_column_match
            all_cols = list(self.df.columns)
            preferred_label_targets = ['region', 'category', 'type', 'product']
            for target in preferred_label_targets:
                matched = self._find_best_column_match(target, all_cols)
                if matched and matched in suitable["categorical"]:
                    label_column = matched
                    logging.info(f"Auto-detected label_column: {label_column} (matched target: {target})")
                    break

            if label_column is None:
                if suitable["categorical"]:
                    label_column = suitable["categorical"][0]
                    logging.info(f"Auto-detected label_column (fallback): {label_column}")
                elif len(suitable["numeric"]) > 1:
                    # Use first numeric column as label if we have multiple numeric
                    label_column = suitable["numeric"][0]
                    logging.info(f"Auto-detected label_column (numeric fallback): {label_column}")
                elif self.df.shape[1] > 0:
                    # Fallback: use first column as label
                    label_column = self.df.columns[0]
                    logging.info(f"Auto-detected label_column (final fallback): {label_column}")

        if value_column is None:
            # For pie charts, prefer columns that represent values/amounts
            # Use semantic matching via _find_best_column_match
            all_cols = list(self.df.columns)
            preferred_value_targets = ['sales', 'total', 'revenue', 'amount']
            for target in preferred_value_targets:
                matched = self._find_best_column_match(target, all_cols)
                if matched and matched in suitable["numeric"]:
                    value_column = matched
                    logging.info(f"Auto-detected value_column: {value_column} (matched target: {target})")
                    break

            if value_column is None:
                if suitable["numeric"]:
                    value_column = suitable["numeric"][0]
                    # Make sure we're not using the same column for both
                    if value_column == label_column and len(suitable["numeric"]) > 1:
                        value_column = suitable["numeric"][1]
                    logging.info(f"Auto-detected value_column (fallback): {value_column}")
                elif len(suitable["numeric"]) == 1 and label_column != suitable["numeric"][0]:
                    value_column = suitable["numeric"][0]
                    logging.info(f"Auto-detected value_column (single numeric): {value_column}")
                elif self.df.shape[1] > 1:
                    # Fallback: use second column as value
                    value_column = self.df.columns[1] if len(self.df.columns) > 1 else self.df.columns[0]
                    logging.info(f"Auto-detected value_column (final fallback): {value_column}")

        # If columns were provided as arguments, try to match them to actual columns
        # This handles the case where user says "sales by region" but columns are named "Total" and "Region"
        original_label = label_column
        original_value = value_column

        # Try to find the best match if columns don't exist
        if label_column not in self.df.columns:
            matched_label = self._find_best_column_match(label_column, list(self.df.columns))
            if matched_label:
                label_column = matched_label

        if value_column not in self.df.columns:
            matched_value = self._find_best_column_match(value_column, list(self.df.columns))
            if matched_value:
                value_column = matched_value

        # Verify columns exist in dataframe
        if label_column not in self.df.columns or value_column not in self.df.columns:
            # Try one more time with fuzzy matching against all columns
            all_cols = list(self.df.columns)
            if label_column not in self.df.columns:
                # Try semantic matching for common patterns
                label_column = self._find_best_column_match("region" if "label" not in str(label_column).lower() else "label", all_cols)
                if label_column is None and suitable["categorical"]:
                    label_column = suitable["categorical"][0]
            if value_column not in self.df.columns:
                # Try semantic matching for common patterns
                value_column = self._find_best_column_match("sales" if "value" not in str(value_column).lower() else "value", all_cols)
                if value_column is None and suitable["numeric"]:
                    value_column = suitable["numeric"][0]

        logging.info(f"After auto-detect (original: {original_label}, {original_value}): label={label_column}, value={value_column}")
        logging.info(f"DataFrame sample:\n{self.df[[label_column, value_column]].head() if label_column and value_column else self.df.head()}")

        if label_column is None or value_column is None:
            raise ValueError(
                f"Cannot create pie chart: need at least one numeric column. "
                f"Available columns: {list(self.df.columns)}. "
                f"Numeric columns: {suitable['numeric']}. "
                f"Categorical columns: {suitable['categorical']}."
            )

        # Verify columns exist in dataframe
        if label_column not in self.df.columns or value_column not in self.df.columns:
            raise ValueError(f"Columns not found in data: label={label_column}, value={value_column}")

        # Verify value column is actually numeric - if not, find a better one
        if not pd.api.types.is_numeric_dtype(self.df[value_column]):
            logging.warning(f"Selected value column '{value_column}' is not numeric, dtype={self.df[value_column].dtype}")
            # Find the best numeric column as fallback
            all_cols = list(self.df.columns)
            preferred_numeric_targets = ['total', 'sales', 'revenue', 'amount', 'price', 'quantity']
            for target in preferred_numeric_targets:
                matched = self._find_best_column_match(target, all_cols)
                if matched and matched in suitable["numeric"] and pd.api.types.is_numeric_dtype(self.df[matched]):
                    logging.info(f"Replacing non-numeric value column '{value_column}' with '{matched}'")
                    value_column = matched
                    break

            # If still not numeric, use first truly numeric column
            if not pd.api.types.is_numeric_dtype(self.df[value_column]):
                for col in suitable["numeric"]:
                    if pd.api.types.is_numeric_dtype(self.df[col]):
                        logging.warning(f"Using fallback numeric column '{col}' instead of '{value_column}'")
                        value_column = col
                        break

        # Group and sum values by label
        try:
            grouped = self.df.groupby(label_column)[value_column].sum().reset_index()
            grouped = grouped.sort_values(value_column, ascending=False).head(top_n)
        except Exception as e:
            logging.error(f"Failed to group data: {e}")
            # Try converting value column to numeric first
            try:
                self.df[value_column] = pd.to_numeric(self.df[value_column], errors='coerce')
                grouped = self.df.groupby(label_column)[value_column].sum().reset_index()
                grouped = grouped.sort_values(value_column, ascending=False).head(top_n)
            except Exception as e2:
                logging.error(f"Failed to convert and group: {e2}")
                raise ValueError(f"Could not create chart with columns label={label_column}, value={value_column}")

        logging.info(f"Grouped data for pie chart:\n{grouped.to_string()}")

        # Convert to chart data format
        data = [
            {"name": str(row[label_column]), "value": float(row[value_column])}
            for _, row in grouped.iterrows()
        ]

        return {
            "data": data,
            "title": f"{value_column} by {label_column}",
            "valueKey": "value",
            "xKey": "name",
            "yKey": "value"
        }

    def generate_bar_chart(
        self,
        x_column: Optional[str] = None,
        y_column: Optional[str] = None,
        top_n: int = 20
    ) -> Dict[str, Any]:
        """
        Generate bar chart configuration.

        Args:
            x_column: Column to use for x-axis
            y_column: Column to use for y-axis (values)
            top_n: Maximum number of bars to show

        Returns:
            Chart configuration dict for Recharts
        """
        if self.df is None:
            raise ValueError("No data loaded")

        suitable = self.find_suitable_columns()
        import logging

        # Auto-detect columns if not provided
        if x_column is None:
            # Prefer categorical columns that are likely to be good labels
            # Priority: region, category, type, name, product, or first categorical
            preferred_x_keywords = ['region', 'category', 'type', 'name', 'product', 'item', 'area', 'location', 'zone', 'territory']
            found = False
            for keyword in preferred_x_keywords:
                for col in suitable["categorical"]:
                    if keyword in col:
                        x_column = col
                        found = True
                        break
                if found:
                    break
            if not found:
                if suitable["categorical"]:
                    x_column = suitable["categorical"][0]
                elif self.df.columns.any():
                    x_column = self.df.columns[0]

        if y_column is None:
            # Prefer columns that represent values/amounts
            # Priority: total, sales, amount, revenue, price, or first numeric
            preferred_y_keywords = ['total', 'sales', 'amount', 'revenue', 'price', 'value', 'cost', 'sum', 'count', 'quantity']
            found = False
            for keyword in preferred_y_keywords:
                for col in suitable["numeric"]:
                    if keyword in col:
                        y_column = col
                        found = True
                        break
                if found:
                    break
            if not found:
                if suitable["numeric"]:
                    y_column = suitable["numeric"][0]
                    # Use different column if same as x
                    if y_column == x_column and len(suitable["numeric"]) > 1:
                        y_column = suitable["numeric"][1]

        # If columns were provided as arguments, try to match them to actual columns
        # This handles the case where user says "sales by region" but columns are named "Total" and "Region"
        original_x = x_column
        original_y = y_column

        # Try to find the best match if columns don't exist
        if x_column and x_column not in self.df.columns:
            matched_x = self._find_best_column_match(x_column, list(self.df.columns))
            if matched_x:
                x_column = matched_x

        if y_column and y_column not in self.df.columns:
            matched_y = self._find_best_column_match(y_column, list(self.df.columns))
            if matched_y:
                y_column = matched_y

        logging.info(f"Bar chart columns (original: {original_x}, {original_y}): x={x_column}, y={y_column}")
        logging.info(f"Available numeric columns: {suitable['numeric']}, categorical: {suitable['categorical']}")

        if x_column is None or y_column is None:
            raise ValueError(
                f"Cannot create bar chart: need at least one numeric column. "
                f"Available columns: {list(self.df.columns)}. "
                f"Numeric columns: {suitable['numeric']}. "
                f"Categorical columns: {suitable['categorical']}."
            )

        if x_column not in self.df.columns or y_column not in self.df.columns:
            # Try semantic matching for common patterns
            if x_column not in self.df.columns and suitable["categorical"]:
                x_column = suitable["categorical"][0]
            if y_column not in self.df.columns and suitable["numeric"]:
                y_column = suitable["numeric"][0]

        if x_column not in self.df.columns or y_column not in self.df.columns:
            raise ValueError(f"Columns not found in data: x={x_column}, y={y_column}")

        # Aggregate data by x_column
        if not pd.api.types.is_numeric_dtype(self.df[x_column]):
            # Group categorical column and sum the numeric values
            grouped = self.df.groupby(x_column)[y_column].sum().reset_index()
            # Sort by value descending and take top_n
            grouped = grouped.sort_values(y_column, ascending=False).head(top_n)
        else:
            grouped = self.df.sort_values(y_column, ascending=False).head(top_n)

        data = [
            {"name": str(row[x_column]), "value": float(row[y_column])}
            for _, row in grouped.iterrows()
        ]

        return {
            "data": data,
            "title": f"{y_column} by {x_column}",
            "xKey": "name",
            "yKey": "value"
        }

    def generate_line_chart(
        self,
        x_column: Optional[str] = None,
        y_column: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate line chart configuration.

        Args:
            x_column: Column to use for x-axis (should be sequential/datetime)
            y_column: Column to use for y-axis (values)

        Returns:
            Chart configuration dict for Recharts
        """
        if self.df is None:
            raise ValueError("No data loaded")

        suitable = self.find_suitable_columns()

        # Try to find a date/time column for x-axis
        date_cols = [
            col for col in self.df.columns
            if pd.api.types.is_datetime64_any_dtype(self.df[col]) or
               self.df[col].dtype == 'object'
        ]

        if x_column is None:
            x_column = date_cols[0] if date_cols else (suitable["numeric"][0] if suitable["numeric"] else self.df.columns[0])
        if y_column is None:
            if suitable["numeric"]:
                y_column = suitable["numeric"][0]
                if y_column == x_column and len(suitable["numeric"]) > 1:
                    y_column = suitable["numeric"][1]
            elif len(self.df.columns) > 1:
                y_column = self.df.columns[1]

        if x_column is None or y_column is None:
            raise ValueError(
                f"Cannot create line chart: need at least one numeric column. "
                f"Available columns: {list(self.df.columns)}. "
                f"Numeric columns: {suitable['numeric']}."
            )

        if x_column not in self.df.columns or y_column not in self.df.columns:
            raise ValueError(f"Columns not found in data: x={x_column}, y={y_column}")

        # Sort by x column
        sorted_df = self.df.sort_values(x_column)

        data = [
            {"name": str(row[x_column]), "value": float(row[y_column])}
            for _, row in sorted_df.iterrows()
        ]

        return {
            "data": data,
            "title": f"{y_column} over {x_column}",
            "xKey": "name",
            "yKey": "value"
        }

    def generate_scatter_chart(
        self,
        x_column: Optional[str] = None,
        y_column: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate scatter chart configuration.

        Args:
            x_column: Column to use for x-axis (numeric)
            y_column: Column to use for y-axis (numeric)

        Returns:
            Chart configuration dict for Recharts
        """
        if self.df is None:
            raise ValueError("No data loaded")

        suitable = self.find_suitable_columns()

        if len(suitable["numeric"]) < 2:
            raise ValueError(
                f"Scatter chart requires at least 2 numeric columns. "
                f"Available columns: {list(self.df.columns)}. "
                f"Numeric columns: {suitable['numeric']}."
            )

        if x_column is None:
            x_column = suitable["numeric"][0]
        if y_column is None:
            y_column = suitable["numeric"][1] if len(suitable["numeric"]) > 1 else suitable["numeric"][0]

        if x_column not in self.df.columns or y_column not in self.df.columns:
            raise ValueError(f"Columns not found in data: x={x_column}, y={y_column}")

        data = [
            {"x": float(row[x_column]), "y": float(row[y_column])}
            for _, row in self.df.iterrows()
        ]

        return {
            "data": data,
            "title": f"{y_column} vs {x_column}",
            "xKey": "x",
            "yKey": "y",
            "xLabel": x_column,
            "yLabel": y_column,
            "name": f"{y_column} vs {x_column}"
        }

    def auto_generate_chart(
        self,
        chart_type: str,
        label_column: Optional[str] = None,
        value_column: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Auto-generate chart based on type.

        Args:
            chart_type: Type of chart ('pie', 'bar', 'line', 'scatter')
            label_column: Optional column to use for labels/categories
            value_column: Optional column to use for values

        Returns:
            Chart configuration dict
        """
        chart_type = chart_type.lower()

        try:
            if chart_type == "pie":
                return self.generate_pie_chart(label_column, value_column)
            elif chart_type == "bar":
                return self.generate_bar_chart(label_column, value_column)
            elif chart_type == "line":
                return self.generate_line_chart(label_column, value_column)
            elif chart_type == "scatter":
                return self.generate_scatter_chart(label_column, value_column)
            else:
                raise ValueError(f"Unsupported chart type: {chart_type}")
        except Exception as e:
            import logging
            logging.warning(f"Primary chart generation failed: {e}, trying fallback")
            # Fallback: create a simple chart using row count or first available columns
            return self._generate_fallback_chart(chart_type, label_column, value_column)

    def _generate_fallback_chart(
        self,
        chart_type: str,
        label_column: Optional[str] = None,
        value_column: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate a fallback chart when normal generation fails"""
        import logging
        logging.warning("Generating fallback chart")
        logging.info(f"DataFrame shape: {self.df.shape}, columns: {list(self.df.columns)}")
        logging.info(f"DataFrame dtypes: {self.df.dtypes.to_dict()}")
        logging.info(f"Sample data:\n{self.df.head(10).to_string()}")

        # For fallback, try to find actual numeric data instead of just counting
        if len(self.df) == 0:
            raise ValueError("No data available for chart")

        # Try to find a numeric column that hasn't been identified as such
        numeric_col = None
        cat_col = None

        # First check actual numeric dtypes
        for col in self.df.columns:
            if pd.api.types.is_numeric_dtype(self.df[col]) and self.df[col].dropna().sum() > 0:
                numeric_col = col
                break

        # If no numeric found, try to convert columns
        if numeric_col is None:
            for col in self.df.columns:
                try:
                    sample = self.df[col].dropna().head(20)
                    if len(sample) > 0:
                        converted = pd.to_numeric(sample, errors='coerce')
                        # Use columns that convert well and have meaningful values
                        if converted.notna().sum() / len(converted) > 0.9 and converted.sum() > 0:
                            numeric_col = col
                            break
                except Exception:
                    pass

        # Find a categorical column
        for col in self.df.columns:
            if col != numeric_col and not pd.api.types.is_numeric_dtype(self.df[col]):
                cat_col = col
                break
        if cat_col is None and len(self.df.columns) > 1:
            cat_col = self.df.columns[0] if self.df.columns[0] != numeric_col else self.df.columns[1]

        if chart_type in ["pie", "bar"]:
            if numeric_col is not None:
                # Use the numeric column directly - show each row's value
                try:
                    if cat_col is not None:
                        # Group by categorical column and sum numeric values
                        grouped = self.df.groupby(cat_col)[numeric_col].sum().reset_index()
                        grouped = grouped.sort_values(numeric_col, ascending=False).head(10)
                        data = [
                            {"name": str(row[cat_col]), "value": float(row[numeric_col])}
                            for _, row in grouped.iterrows()
                        ]
                        title = f"{numeric_col} by {cat_col}"
                    else:
                        # Just show top values
                        top_data = self.df.nlargest(10, numeric_col)
                        data = [
                            {"name": f"Row {idx}", "value": float(row[numeric_col])}
                            for idx, row in top_data.iterrows()
                        ]
                        title = f"Top 10 values from {numeric_col}"
                    logging.info(f"Fallback chart generated with {len(data)} data points using numeric column '{numeric_col}'")
                except Exception as e:
                    logging.warning(f"Failed to use numeric column '{numeric_col}' for fallback chart: {e}")
                    # Final fallback - show row indices
                    data = [{"name": f"Row {i}", "value": 1} for i in range(min(10, len(self.df)))]
                    title = "Data Overview"
            else:
                # No numeric column found - use row counts
                cat_col = self.df.columns[0] if len(self.df.columns) > 0 else None
                if cat_col is not None:
                    try:
                        col_data = self.df[cat_col]
                        grouped = col_data.value_counts().head(10)
                        data = [
                            {"name": str(idx), "value": int(count)}
                            for idx, count in grouped.items()
                        ]
                        title = f"Count by {cat_col}"
                    except Exception:
                        data = [{"name": f"Row {i}", "value": 1} for i in range(min(10, len(self.df)))]
                        title = "Data Overview"
                else:
                    data = [{"name": f"Row {i}", "value": 1} for i in range(min(10, len(self.df)))]
                    title = "Data Overview"

            return {
                "data": data,
                "title": title,
                "valueKey": "value",
                "xKey": "name",
                "yKey": "value"
            }
        elif chart_type == "line":
            # Just show row progression
            data = [
                {"name": str(i), "value": float(i)}
                for i in range(min(20, len(self.df)))
            ]
            return {
                "data": data,
                "title": "Data Progression",
                "xKey": "name",
                "yKey": "value"
            }
        elif chart_type == "scatter":
            # Use row index and a simple numeric value
            data = [
                {"x": float(i), "y": float(i % 10)}
                for i in range(min(50, len(self.df)))
            ]
            return {
                "data": data,
                "title": "Data Distribution",
                "xKey": "x",
                "yKey": "y",
                "xLabel": "Row Index",
                "yLabel": "Value",
                "name": "Row vs Value"
            }
        else:
            raise ValueError(f"Unsupported chart type: {chart_type}")

    def get_data_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the data for display.

        Returns:
            Summary dict with stats and info
        """
        if self.df is None:
            return {}

        return {
            "rows": len(self.df),
            "columns": len(self.df.columns),
            "column_names": list(self.df.columns),
            "numeric_columns": self.find_suitable_columns()["numeric"],
            "categorical_columns": self.find_suitable_columns()["categorical"]
        }


def parse_chart_request(user_message: str) -> Optional[Dict[str, str]]:
    """
    Parse a user message to detect chart request.

    Args:
        user_message: The user's message text

    Returns:
        Dict with chart_type, label_column, value_column if found, else None
    """
    import logging
    message_lower = user_message.lower()

    # Detect chart type - more flexible matching
    chart_type = None
    chart_keywords = {
        "pie": ["pie chart", "piechart", "pie", "donut", "doughnut"],
        "bar": ["bar chart", "barchart", "bar", "column", "histogram"],
        "line": ["line chart", "linechart", "line", "graph", "trend"],
        "scatter": ["scatter", "scatter plot", "scatterplot", "scatter chart"],
    }

    for ct, keywords in chart_keywords.items():
        for keyword in keywords:
            if keyword in message_lower:
                chart_type = ct
                break
        if chart_type:
            break

    # Default to bar chart if just "chart" or "graph" or "visualiz" is mentioned
    if chart_type is None and any(kw in message_lower for kw in ["chart", "graph", "visualiz", "plot", "diagram"]):
        chart_type = "bar"

    if chart_type is None:
        logging.info(f"No chart type detected in message: {user_message}")
        return None

    # Try to extract column mentions
    result = {"chart_type": chart_type}

    # Look for patterns like "sales by region" or "value column"
    if " by " in message_lower:
        parts = message_lower.split(" by ")
        if len(parts) >= 2:
            # Get the last word before "by" as value column
            before_by = parts[0].strip()
            words_before = before_by.split()
            value_column = words_before[-1] if words_before else None

            # Get the first word after "by" as label column
            after_by = parts[1].strip()
            words_after = after_by.split()
            label_column = words_after[0] if words_after else None

            # Expanded common words that should not be treated as column names
            common_words = {
                "a", "the", "show", "create", "make", "chart", "pie", "bar", "line", "of", "for",
                "scatter", "graph", "plot", "visual", "visualize", "visualization", "display",
                "see", "view", "generate", "give", "want", "need", "help", "me"
            }

            # Only set value_column if it's a meaningful column name
            if value_column and value_column not in common_words:
                result["value_column"] = value_column.lower()
            elif len(words_before) >= 2:
                # Try the second-to-last word if the last one is a common word
                second_last = words_before[-2] if len(words_before) >= 2 else None
                if second_last and second_last not in common_words:
                    result["value_column"] = second_last.lower()

            # Always set label_column if we got a word after "by" (it's likely a column name like "region")
            # This handles cases like "bar chart by region" where label_column="region"
            if label_column and label_column not in common_words:
                result["label_column"] = label_column.lower()

    logging.info(f"Chart request parsed: {result} from message: {user_message}")
    return result


if __name__ == "__main__":
    # Test the generator
    import sys

    if len(sys.argv) < 2:
        print("Usage: python chart_generator.py <excel_file> [chart_type]")
        sys.exit(1)

    file_path = sys.argv[1]
    chart_type = sys.argv[2] if len(sys.argv) > 2 else "pie"

    try:
        generator = ChartGenerator(file_path)
        print("Data Summary:")
        print(json.dumps(generator.get_data_summary(), indent=2))
        print()

        config = generator.auto_generate_chart(chart_type)
        print(f"Chart Configuration ({chart_type}):")
        print(json.dumps(config, indent=2))
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
