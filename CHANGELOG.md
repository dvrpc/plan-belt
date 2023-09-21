## 0.5.1 (2023-09-21)

### Fix

- add handler for when a row contains none

## 0.5.0 (2023-08-17)

## 0.4.5 (2023-07-27)

### Fix

- add new report type and add value error

## 0.4.4 (2023-07-13)

### Fix

- check for cases in max delay where dtype is wrong and cast to flot

## 0.4.3 (2023-06-20)

### Fix

- added usr/bin to point to pdftotext

## 0.4.2 (2023-06-09)

### Fix

- return excel path for simsum

## 0.4.1 (2023-06-09)

### Fix

- add excel path so it is ingestible by synchrosumapi

## 0.4.0 (2023-06-05)

### Feat

- add function to combine simtraffic queues into synchro df, handles combined mvmts ie TR
- added simtraffic flag in synchro so that simtraffic dfs can be returned and soon folded into synchro report

### Fix

- fix sim queue summary where there are multiple mvmts with same name
- added csv flag to sim, to determine if to export csv or return dfs

## 0.3.1 (2023-05-26)

### Fix

- additional handlers for no title, unexpected queue length percentage

## 0.3.0 (2023-05-25)

### Feat

- add direction handler, subsequent patches will add other two cases

### Fix

- queue length properly populating
- delay properly calculated and assigned
- delay loosely working but need to iron out a few bugs
- partially working, but doesnt yet properly apply to only arrow cells
- creating a save point where through merging still works

## 0.2.0 (2023-05-10)

### Feat

- docstring changes and refactoring

### Refactor

- delete unneeded print
- round queue lengths and properly pull 50th or 95th for column
- added remainder of fields after feedback in field names gdoc from thom and kelsey
- add convert queue function
- remove unnecessary prints
- add summary with correct keyname
- readded queue length calc
- still refactoring, adding fields
- pulling dfs into csv working correctly
- added / refactored csv function
- transpose and queue length calcs working in hcm 6t
- hcm 6th signalized summary df done
- added handler for hcm 6th, which have different starting rows
- break index of each df and variablize intersection names
- dfs coming in correctly, now to summarize and cleanup
- remove old cli

## 0.1.5 (2023-04-18)

### Fix

- corrected location of uniqueidb

## 0.1.4 (2023-04-18)

### Fix

- move input id b to correct function

## 0.1.3 (2023-04-14)

### Fix

- changed where permissions are in yml
- whitespace but leaving as a fix to increment

## 0.1.2 (2023-04-14)

### Fix

- changed yml config to body as a test
- changed tag format to see if anything changes
- removed release job to see if bump can work on its own
- added additional changelog settings to pyproj toml
- falsely adding this readme change as a fix to test incrementation

## 0.1.1 (2023-04-14)

### Fix

- removed changelog entirely to see if gh action handles it
- added new changelog
- changed changelog to incremental
- black formatting
- changed tagname
- correct versions
- adding versions elsewhere
- restarted from scratch , seeing if auto increment works

## 0.1.0 (2023-04-12)

### Fix

- added blank changelog file
- deleting old changelog
- edited changelog to remove v?
- edited readme, but also created new tag without v
- corrected back to master
- got rid of v and changed branch to proper name (main)
- ugh
- testing fix with bump
- removing
- moved back to v
- fixes failure to create tag issue in ci
- pointed to correct changelog file
- removed erronious colon
- trying to address versioning error
- testing fixes
- testing fixes to bump
- added docs as semver test
