from openpyxl import Workbook, load_workbook


wb = load_workbook(filename = 'ME-ProxSensor-TestProgDataFile.xlsx')
ws = wb.active
