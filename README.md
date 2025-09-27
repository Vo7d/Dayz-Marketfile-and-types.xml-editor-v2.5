# Dayz-Marketfile-and-types.xml-editor-v2.5
This is a tool i made for adjusting marketfiles and types.xml for my Dayz server to help speed the process up. 

If you want to support me you can do so by buying me a coffee right here. It all goes to support my Dayz server.

https://www.paypal.com/donate/?hosted_button_id=U23QPP7RCVDHL

Thank you.


---------------------------------------------------------------------------------------------------------------
Installation.

Quick checklist

Have Python 3.8+ installed.

Open the file you just downloaded in VS Code.

Install the Python extension for VS Code (if not already).

Make a virtual environment (recommended) and install Pillow: pip install pillow.

Run the script (Run button, or Run Python File in Terminal) — the GUI window should open.


Interface overview
--------------------------------------------------------------------------------------------------------------
Tabs:

Market Editor — edit market JSON files.

Types.xml Editor — edit types.xml files.

About — author & copyright.

File panel: Open / Save / Reset / Validate / Close.

Two text panels:

Left: Original file (read-only).

Right: Modified file (editable) — changes are highlighted in green.

Search under each pane: Search box with Case, Whole word, and Regex options and Prev/Next.

Status bar: bottom line shows open file and type.

Workflow & tips

Use the Open button to load the file. The file is shown identically in both panels.

Make edits in the Modified (right) panel. Lines that differ from the original are immediately highlighted in green.

Use Reset to revert the modified panel to the original file contents.

Use Validate JSON/XML to ensure syntax correctness before saving.

Save using Save (or Ctrl+S).

Use the Search panel to find values quickly. Use Regex for advanced patterns.

Keyboard shortcuts

Ctrl+O — Open (active tab)

Ctrl+S — Save (active tab)

Ctrl+R — Reset (active tab)

Ctrl+V — Validate (active tab)

Ctrl+Q — Quit
