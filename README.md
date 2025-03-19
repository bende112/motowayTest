# Motorway
Handles invalid registrations and skips them.
Compares results with expected data and highlights mismatches.
Outputs results in CSV and Excel formats.
mmotorwayTest/
│── motoway_test.py         # Main script
│── requirements.txt        # Required dependencies
│── car_input.txt           # List of vehicle registration numbers
│── car_output.txt          # Expected output (CSV format)
│── comparison_results.csv  # Scraped data and comparison results
│── comparison_results.xlsx # Excel version of the results
│── README.md               # Documentation


git clone https://github.com/bende112/motowayTest.git
cd motorwayTest
pip install pytest-playwright
playwright install
pip install Panda

!Troubleshotting playwright install pip install jinja2
Run test using pytest
I did use python3.13 motoway_test.py
use pytest --headed
pytest --browser webkit for different browser
Enter reg on motoway to get a car value
