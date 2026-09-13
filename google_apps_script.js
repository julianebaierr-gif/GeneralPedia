/**
 * =====================================================================
 * Google Apps Script for GeneralPedia.com Auto-Sync
 * =====================================================================
 * 
 * Instructions:
 * 1. Open your Google Sheet: https://docs.google.com/spreadsheets/d/1IDS7DUc4PrlYbxhKwlqsoeQK70JH10-M_Qq80zm_-b0/edit?gid=758476499
 * 2. Click: Extensions > Apps Script
 * 3. Delete existing code, paste this entire script, and click Save (Disk icon).
 * 4. Click: Deploy > New deployment
 * 5. Select type: "Web app"
 * 6. Set "Execute as": "Me"
 * 7. Set "Who has access": "Anyone"
 * 8. Click "Deploy", authorize permissions, and copy the Web App URL!
 */

function doPost(e) {
  try {
    var sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName("Sheet1") || SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
    
    // Check if headers exist; if not, initialize headers in row 1
    if (sheet.getLastRow() === 0) {
      sheet.appendRow(["Keywords", "Category", "Tags", "Status", "Post Url", "Post Date / Time"]);
      sheet.getRange(1, 1, 1, 6).setFontWeight("bold").setBackground("#10b981").setFontColor("#ffffff");
    }
    
    var data = JSON.parse(e.postData.contents);
    
    var keywords = data.keywords || "";
    var category = data.category || "";
    var tags = Array.isArray(data.tags) ? data.tags.join(", ") : (data.tags || "");
    var status = data.status || "Published";
    var postUrl = data.post_url || "";
    var postDateTime = data.post_date_time || Utilities.formatDate(new Date(), "GMT+5", "yyyy-MM-dd HH:mm:ss");
    
    sheet.appendRow([keywords, category, tags, status, postUrl, postDateTime]);
    
    return ContentService.createTextOutput(JSON.stringify({
      status: "success",
      message: "Row added successfully",
      row: sheet.getLastRow()
    })).setMimeType(ContentService.MimeType.JSON);
    
  } catch (error) {
    return ContentService.createTextOutput(JSON.stringify({
      status: "error",
      message: error.toString()
    })).setMimeType(ContentService.MimeType.JSON);
  }
}

function doGet(e) {
  return ContentService.createTextOutput("GeneralPedia Auto-Sync Webhook is Active!");
}
