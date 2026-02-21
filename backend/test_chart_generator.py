"""Test script for chart generator"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.chart.chart_generator import ChartGenerator, parse_chart_request

# Test the chart request parser
test_messages = [
    "create a pie chart",
    "show me a bar chart",
    "I want a line chart",
    "draw a scatter plot",
    "make a chart",
    "sales by region",
    "create a pie chart showing sales by region",
    "generate a bar chart for revenue",
]

print("=== Testing Chart Request Parser ===")
for msg in test_messages:
    result = parse_chart_request(msg)
    print(f"Message: '{msg}'")
    print(f"  Result: {result}")
    print()

# Test with an actual Excel file if one exists
print("=== Testing Excel File Reading ===")

# Check for the dude_investments_sales.xlsx file in the project root
excel_files = [
    "C:/projects/chatgptLike/dude_investments_sales.xlsx",
    "/c/projects/chatgptLike/dude_investments_sales.xlsx",
    "./dude_investments_sales.xlsx",
]

excel_path = None
for path in excel_files:
    if os.path.exists(path):
        excel_path = path
        break

if excel_path:
    print(f"Using Excel file: {excel_path}")

    try:
        generator = ChartGenerator(excel_path)
        print(f"\nData Summary:")
        summary = generator.get_data_summary()
        print(f"  Rows: {summary['rows']}")
        print(f"  Columns: {summary['columns']}")
        print(f"  Column names: {summary['column_names']}")
        print(f"  Numeric columns: {summary['numeric_columns']}")
        print(f"  Categorical columns: {summary['categorical_columns']}")

        print(f"\n=== Testing Chart Generation ===")

        # Test pie chart
        print("\n1. Pie Chart:")
        try:
            pie_config = generator.auto_generate_chart("pie")
            print(f"   Success! Data points: {len(pie_config['data'])}")
            print(f"   Sample data: {pie_config['data'][:3]}")
        except Exception as e:
            print(f"   Error: {e}")

        # Test bar chart
        print("\n2. Bar Chart:")
        try:
            bar_config = generator.auto_generate_chart("bar")
            print(f"   Success! Data points: {len(bar_config['data'])}")
            print(f"   Sample data: {bar_config['data'][:3]}")
        except Exception as e:
            print(f"   Error: {e}")

        # Test line chart
        print("\n3. Line Chart:")
        try:
            line_config = generator.auto_generate_chart("line")
            print(f"   Success! Data points: {len(line_config['data'])}")
            print(f"   Sample data: {line_config['data'][:3]}")
        except Exception as e:
            print(f"   Error: {e}")

        # Test scatter chart
        print("\n4. Scatter Chart:")
        try:
            scatter_config = generator.auto_generate_chart("scatter")
            print(f"   Success! Data points: {len(scatter_config['data'])}")
            print(f"   Sample data: {scatter_config['data'][:3]}")
        except Exception as e:
            print(f"   Error: {e}")

    except Exception as e:
        print(f"Error creating chart generator: {e}")
        import traceback
        traceback.print_exc()
else:
    print("No Excel file found. Looking for dude_investments_sales.xlsx")
    print("Place an Excel file in the project root to test chart generation.")
