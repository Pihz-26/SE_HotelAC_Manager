# frontend/exporter.py
import xlsxwriter

def export_bill(bill_data, filename):
    workbook = xlsxwriter.Workbook(filename)
    sheet = workbook.add_worksheet("账单")
    headers = ["RoomId", "HousingCost", "ACUsageCost"]
    for col, h in enumerate(headers):
        sheet.write(0, col, h)
    for row, bd in enumerate(bill_data, 1):
        sheet.write(row, 0, bd.get("roomId", ""))
        sheet.write(row, 1, bd.get("housingCost", 0))
        sheet.write(row, 2, bd.get("acUsageCost", 0))
    workbook.close()

def export_detail(detail_data, filename):
    workbook = xlsxwriter.Workbook(filename)
    sheet = workbook.add_worksheet("详单")
    headers = ["RoomId", "Time", "WindSpeed", "Cost"]
    for col, h in enumerate(headers):
        sheet.write(0, col, h)
    for row, dd in enumerate(detail_data, 1):
        sheet.write(row, 0, dd.get("roomId", ""))
        sheet.write(row, 1, dd.get("time", "无"))
        sheet.write(row, 2, dd.get("windSpeed", "N/A"))
        sheet.write(row, 3, dd.get("cost", 0))
    workbook.close()
