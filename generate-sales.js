const XLSX = require('xlsx');

// Generate fake sales data for Dude Investments
const salesData = [
  // Header row
  ['Company Name', 'Date', 'Product', 'Quantity', 'Unit Price', 'Total', 'Region', 'Sales Rep', 'Customer'],
  // Data rows
  ['Dude Investments', '2026-01-15', 'Premium Portfolio', 5, 2500, 12500, 'North America', 'John Smith', 'Acme Corp'],
  ['Dude Investments', '2026-01-16', 'Basic Portfolio', 10, 800, 8000, 'Europe', 'Sarah Johnson', 'TechStart Inc'],
  ['Dude Investments', '2026-01-18', 'Premium Portfolio', 3, 2500, 7500, 'Asia Pacific', 'Michael Chen', 'Global Ventures'],
  ['Dude Investments', '2026-01-20', 'Gold Membership', 8, 1200, 9600, 'North America', 'John Smith', 'Future Systems'],
  ['Dude Investments', '2026-01-22', 'Basic Portfolio', 15, 800, 12000, 'Europe', 'Sarah Johnson', 'EuroTech Ltd'],
  ['Dude Investments', '2026-01-25', 'Premium Portfolio', 7, 2500, 17500, 'Asia Pacific', 'Michael Chen', 'Pacific Holdings'],
  ['Dude Investments', '2026-01-28', 'Gold Membership', 12, 1200, 14400, 'North America', 'John Smith', 'Innovate LLC'],
  ['Dude Investments', '2026-02-01', 'Basic Portfolio', 20, 800, 16000, 'Europe', 'Sarah Johnson', 'Digital Partners'],
  ['Dude Investments', '2026-02-03', 'Premium Portfolio', 4, 2500, 10000, 'Asia Pacific', 'Michael Chen', 'Dragon Ventures'],
  ['Dude Investments', '2026-02-05', 'Gold Membership', 6, 1200, 7200, 'North America', 'John Smith', 'Capital Group'],
  ['Dude Investments', '2026-02-08', 'Basic Portfolio', 9, 800, 7200, 'Europe', 'Sarah Johnson', 'EuroFund SA'],
  ['Dude Investments', '2026-02-10', 'Premium Portfolio', 11, 2500, 27500, 'Asia Pacific', 'Michael Chen', 'Emerging Markets Co'],
  ['Dude Investments', '2026-02-12', 'Gold Membership', 14, 1200, 16800, 'North America', 'John Smith', 'Prime Investors'],
  ['Dude Investments', '2026-02-14', 'Basic Portfolio', 18, 800, 14400, 'Europe', 'Sarah Johnson', 'Continental Finance'],
  ['Dude Investments', '2026-02-16', 'Premium Portfolio', 6, 2500, 15000, 'Asia Pacific', 'Michael Chen', 'Orient Capital'],
  ['Dude Investments', '2026-02-18', 'Gold Membership', 10, 1200, 12000, 'North America', 'John Smith', 'NorthStar Investments'],
  ['Dude Investments', '2026-02-19', 'Basic Portfolio', 7, 800, 5600, 'Europe', 'Sarah Johnson', 'Baltic Ventures'],
  ['Dude Investments', '2026-02-20', 'Premium Portfolio', 5, 2500, 12500, 'Asia Pacific', 'Michael Chen', 'Singapore Holdings'],
];

// Create a worksheet
const worksheet = XLSX.utils.aoa_to_sheet(salesData);

// Set column widths
worksheet['!cols'] = [
  { wch: 16 }, // Company Name
  { wch: 12 }, // Date
  { wch: 18 }, // Product
  { wch: 10 }, // Quantity
  { wch: 12 }, // Unit Price
  { wch: 10 }, // Total
  { wch: 14 }, // Region
  { wch: 12 }, // Sales Rep
  { wch: 18 }, // Customer
];

// Create a workbook and add the worksheet
const workbook = XLSX.utils.book_new();
XLSX.utils.book_append_sheet(workbook, worksheet, 'Sales Data');

// Write the file
XLSX.writeFile(workbook, 'dude_investments_sales.xlsx');

console.log('Excel file "dude_investments_sales.xlsx" created successfully!');
