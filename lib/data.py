#
#   SilverBot is a Python application to interact with IB's TWS API.
#   Copyright (C) 2013 Christopher Jastram <cjastram@gmail.com>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import datetime
import gspread
import time
import yaml

_GDOC = None

class Storage:
   schema = None
   _spreadsheet = None

   def __init__(self):
      global _GDOC
      if _GDOC is None:
         f = open('auth.yaml', 'r')
         auth = yaml.safe_load(f)
         f.close()

         self.schema = {}

         gc = gspread.login(auth["gdoc-login"], auth["gdoc-password"])
         spreadsheet = gc.open("Silverbot 2014")

         schema = {
            #"Pairs": [
               #"BidID", "BidDate", "BidQty", "BidPrice", "BidStatus", 
               #"AskID", "AskDate", "AskQty", "AskPrice", "AskStatus"],
            "Config": [ "Setting", "Value" ],
            "Book": [ "ID", "Side", "Price", "Qty", "Status", "Imagined", "Requested", "Confirmed", "Filled", "Offset", "Cancelled", "Parent" ],
         }

         for title, headers in schema.iteritems():
            self.schema[title] = {}

            print "--> Initializing worksheet: %s" % title

            try:
               worksheet = spreadsheet.worksheet(title)
            except gspread.exceptions.WorksheetNotFound:
               worksheet = spreadsheet.add_worksheet(title=title, rows=1, cols=20)

            row = worksheet.row_values(1)
            for heading in headers:
               if not heading in row:
                  col = 1
                  while col < 99:
                     val = worksheet.cell(1, col).value
                     if val == "":
                        worksheet.update_cell(1, col, heading)
                        break
                     col = col + 1
            col = 1
            for heading in worksheet.row_values(1):
               if not heading is None:
                  if heading in self.schema[title]:
                     print "Duplicate heading %s in sheet %s, avoid this!" % (heading, title)
                  self.schema[title][heading] = col
               col = col + 1

         #wks.update_acell('B2', "it's down there somewhere, let me take another look.")

         # Fetch a cell range
         #cell_list = wks.range('A1:B7')
         __GDOC = spreadsheet
      self._spreadsheet = _GDOC

   def _timestamp(self):
      return time.strftime("%m/%d/%Y %H:%M:%S", time.localtime())

   def _equivalent(self, a, b):
      a = float(a)
      b = float(b)
      margin = 0.001
      if a < b + margin and a > b - margin:
         return True
      else:
         return False

   def _select(self, sheet, header, value):
      result = []
      column = sheet.col_values(self.schema[sheet.title][header])
      headers = sheet.row_values(1)
      for i in range(1, len(column)):
         if column[i] == value:
            row = sheet.row_values(i+1)
            block = {}
            for i in range(0, len(headers)):
               block[headers[i]] = None
               if i < len(row):
                  block[headers[i]] = row[i]
            result.append(block)
      return result

   def _add(self, sheet, values):
      flat = []
      count = 0
      id = sheet.row_count + 1
      while count < len(values):
         added = False
         for key, value in values.iteritems():
            if len(flat)+1 == self.schema[sheet.title][key]:
               if value == "%ID%":
                  value = id
               flat.append(value)
               count = count + 1
               added = True
         if not added:
            flat.append("")
      sheet.append_row(flat)
      return id
      
      #for key, value in values.iteritems():
      #   sheet.update_cell(row, self.schema[sheet_name][key], value)

   def _getConfig(self, key, default=None):
      sheet = self._spreadsheet.worksheet("Config")
      index = None
      try:
         keys = sheet.col_values(1)
         index = keys.index(key) + 1
      except ValueError:
         # Config doesn't exist, add it!
         value = ""
         if not default is None:
            value = default
         sheet.append_row([key, value])
         keys = sheet.col_values(1)
         index = keys.index(key) + 1
      return sheet.cell(index, 2).value
   
   def _setConfig(self, key, value):
      sheet = self._spreadsheet.worksheet("Config")
      index = None
      try:
         keys = sheet.col_values(1)
         index = keys.index(key) + 1
         sheet.update_cell(index, 2, value)
      except ValueError:
         # Config doesn't exist, add it!
         sheet.append_row([key, value])
         keys = sheet.col_values(1)
         index = keys.index(key) + 1

   def _confirm_hypothetical(self, side, price, qty):
      print "--> Confirming hypothetical %s order for %i at %0.02f." % (side, qty, price)
      sheet = self._spreadsheet.worksheet("Book")
      data = { 
         "ID": "%ID%", "Side": side, "Price": price, "Qty": qty,
         "Status": "Imagined", "Imagined": self._timestamp()
      }
      recorded = False
      for row in self._select(sheet, "Status", "Imagined"):
         if self._equivalent(row["Price"], data["Price"]):
            recorded = True

            ### Check and reset quantity if necessary
            if int(row["Qty"]) != int(data["Qty"]):
               print "--> Updating quantity for order %s from %s to %s." % (row["ID"], row["Qty"], data["Qty"])
               sheet.update_cell(row["ID"], self.schema[sheet.title]["Qty"], data["Qty"])
               
            break
      if not recorded:
         self._add(sheet, data)
      
   def set_hypothetical_bids(self, bids):
      self._setConfig("Working", "Hypothetical")
      sheet = self._spreadsheet.worksheet("Book")
      for bid in bids:
         bid_id = self._confirm_hypothetical("bid", bid[0], bid[1])

      for row in self._select(sheet, "Status", "Imagined"):
         desired = False
         for bid in bids:
            if self._equivalent(bid[0], row["Price"]):
               desired = True
               break
         if not desired:
            sheet.update_cell(row["ID"], self.schema[sheet.title]["Status"], "Forgotten")
      self._setConfig("Working", "")

   def place_offsets(self):
      offset = 0.50
      self._setConfig("Working", "Offsets")
      sheet = self._spreadsheet.worksheet("Book")
      for row in self._select(sheet, "Status", "Filled"):
         side = "ask"
         price = float(row["Price"]) + offset
         qty = row["Qty"]
         data = { 
            "ID": "%ID%", "Side": side, "Price": price, "Qty": qty,
            "Status": "Imagined", "Imagined": self._timestamp(), "Parent": row["ID"],
         }
         sheet.update_cell(row["ID"], self.schema[sheet.title]["Status"], "Offset")
         sheet.update_cell(row["ID"], self.schema[sheet.title]["Offset"], self._timestamp())
         self._add(sheet, data)

