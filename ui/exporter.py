# exporter.py
import xlsxwriter

def export_bill(bill_data, filename):
    workbook = xlsxwriter.Workbook(filename)
    sheet = workbook.add_worksheet("账单")
    headers = ["RoomId", "CheckIn", "CheckOut", "TotalCost"]
    for col, h in enumerate(headers):
        sheet.write(0, col, h)
    for row, bd in enumerate(bill_data, 1):
        sheet.write(row, 0, bd["roomId"])
        sheet.write(row, 1, bd["checkIn"])
        sheet.write(row, 2, bd["checkOut"])
        sheet.write(row, 3, bd["totalCost"])
    workbook.close()

def export_detail(detail_data, filename):
    workbook = xlsxwriter.Workbook(filename)
    sheet = workbook.add_worksheet("详单")
    headers = ["RoomId", "StartTime", "EndTime", "WindSpeed", "Cost"]
    for col, h in enumerate(headers):
        sheet.write(0, col, h)
    for row, dd in enumerate(detail_data, 1):
        sheet.write(row, 0, dd["roomId"])
        sheet.write(row, 1, dd["startTime"])
        sheet.write(row, 2, dd["endTime"])
        sheet.write(row, 3, dd["windSpeed"])
        sheet.write(row, 4, dd["cost"])
    workbook.close()
