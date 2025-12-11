# TOC Auto-Update Setup Guide

## ✅ What's Implemented

Your report now has a **proper Word TOC field** that:
- Auto-detects all Heading 1, 2, and 3 styles
- Includes clickable hyperlinks  
- Shows page numbers
- Includes subsections (1.1, 2.1, etc.)

## 📋 Two Options for TOC Population

### Option 1: Manual Update (Current Default)
User opens document and:
1. Right-click on TOC placeholder text
2. Select "Update Field"
3. Choose "Update entire table"

**OR:** Press `Ctrl+A` (select all) then `F9` (update fields)

### Option 2: Auto-Update with pywin32 (Recommended)

Makes TOC populate automatically without user action!

#### Requirements:
- ✅ Windows OS
- ✅ Microsoft Word installed
- ✅ pywin32 library

#### Setup Steps:

**1. Install pywin32:**
```bash
pip install pywin32
```

**2. Enable auto-update in `builder.py`:**

Find this line (around line 276):
```python
# self._auto_update_toc_with_word(output_path)
```

**Uncomment it:**
```python
self._auto_update_toc_with_word(output_path)
```

**3. Run the generator:**
```bash
python backend/scripts/v2_architecture/main.py
```

#### What Happens:
```
✅ Report Saved: D:\...\full_report_v2.docx
🔄 Auto-updating TOC with Microsoft Word...
   ✅ TOC auto-updated successfully
```

The report will open in a **hidden** Word instance, update the TOC, save, and close automatically!

## 🎯 Result

**With auto-update enabled:**
- User opens document
- TOC is already fully populated
- All chapters visible with page numbers
- Subsections (1.1, 2.1) included
- No manual action needed!

**Without auto-update:**
- User sees instruction text
- Must right-click → Update Field
- Then TOC populates

## 🐛 Troubleshooting

### Error: "pywin32 not installed"
```bash
pip install pywin32
```

### Error: "Could not auto-update TOC"
- Ensure Microsoft Word is installed
- Close any open Word documents
- Check file isn't locked/read-only

### TOC field shows weird codes
In Word: Press `Alt+F9` to toggle field codes on/off

## 📚 How It Works

**Field Code Structure:**
```
{ TOC \o "1-3" \h \z \u }
  ^    ^       ^  ^  ^
  |    |       |  |  Use outline levels
  |    |       |  Hide page nums in web
  |    |       Hyperlinks
  |    Heading levels 1-3
  TOC command
```

**python-docx creates the field**
→ **pywin32 opens in Word**
→ **Word calculates page breaks**
→ **Fields.Update() populates TOC**
→ **Document saved with populated TOC**

## 🚀 Recommendation

**For development/testing:** Keep manual update (no pywin32 needed)

**For production/deployment:** Enable auto-update for better UX

Your choice! Both work perfectly.
