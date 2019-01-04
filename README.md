# E-Mail Parser (Python)
The parser saves e-mail attachments automatically and handles different self-defined datatypes (media, documents, etc. ).
It works with IMAP servers.

### Table of Contents
* **[Features](#Features)**<br>
* **[How it works](#How-it-works)**<br>
* **[Configuration of the parser](#Configuration-of-the-parser)**<br>
* **[Easy start with generated Test Mails](#Easy-start-with-generated-Test-Mails)**<br>
* **[More Examples](#More-Examples)**<br>
* **[License](#License)**
 
# Features
* save e-mail attachments automatically
* self-defined datatypes allow different handling for different file types
* parametrization could be done by e-mail, default values or metadata
* save attachments in a defined directory
* rename attached files automatically by different keys or variables
* read / write metadata (i.e. EXIF tags) or use them to handle the attachment
* rename files with a serial number
* use categories to classify attachments
* more features: See [examples](#Examples)

# How it works
The parametrization is done in a configuration file. See [configuration](#configuration) for example.

Different datatypes (media, documents, etc.) are defined in the `General` section. These are 
recognized by their fileextension or by assigning a value to the `Datatype` key in the e-mail text.

For each datatype you can define the fileextensions, which belongs to that type, the attachments new 
filename (if it should be renamed) and the directory where it should be saved (e.g. save incoming jpegs 
and bitmaps in *HOME/photos/* while pdf's are saved in *HOME/documents/*). 
You also can define a **category** key for each datatype and several **keywords** (variables) which you can set in the e-mail or in metadata.

You can access the the values of the keywords and the category by their section name (e.g. `$(Author)` for author-key). 
This keywords have a name, which is used in the e-mail, they can have an default value and you can define if
the value should be written to metadata (e.g. EXIF tags for photos) or if a value from the metadata should 
be used as the value. If you want to use a value from metadata you can mask it with a regular expression 
(e.g. mask the year from the creation date of a photo).
(You should also check the right usage of the metadata key with the test programms in *Testprogramme/pyExifTool*).

The priority for getting the keywords value is: default value, value from e-mail, metadata!
(Default values are overwritten by e-mail or metadata).
Have a look in the script files for more information.

# Configuration of the parser
## Define a Category Tree (if you want to use categories)
Just create a folder tree. The tree also defines the category hierarchy. i.e.,
```
./myCategoryRoot/
|
+-- /photos/
|   |
|   +-- /animals/
|   +-- /vacation/
|
+-- /documents/
|   |
|   +-- /cake_recipe/
|
+-- /unsorted/
```
## Configuration file
The ini-file with the configuration (`MailConfig.ini`) must be saved in the same folder as the parser script.
If needed, the location of the ini-file can be configured at the beginning of the parser script (`MailParser.py`).
**Lists** are comma- or comma-space-seperated.

#### Required Sections:
* **`[General]`**: Important definitions about connection, datatypes and logging, etc.
* **`[DataType]`**: Keyword to change the handling for all files in that e-mail regardless of the fileextension.
                (e.g. handle a jpeg as a document and save it in *HOME/documents*. Even if the parser configuration would save it in *HOME/photos*. See [Example: Save your diary entry with the vacation Photos](###Save-your-diary-entry-with-the-vacation-Photos)).

#### Variables
Variables are allowed in the `default`, `filename`, and `directory` option. Variable syntax is `$(variable_name)`.

Known variables are:
* **`Keywords [Section name]`**: Contains the value which was set in the e-mail or read from attachments metadata. 
  i.e., `$(Author)` for the `[Author]` keyword.
* **`$(Mail_Year)`, `$(Mail_Month)`, `$(Mail_Day)`**: Date of receipt from the e-mail.
* **`$(File_Name)`**: Attachments original filename
* **`$(*)`**: Each '\*' means one digit of a serial number i.e., $(****) names the 10th file to '00010'

#### Keywords
The keywords are defined in the `category` or `keys` option of each datatype.
**Required options for keys:**

| Option | Type   | Description                                                                |
|--------|--------|----------------------------------------------------------------------------|
| name   | String | Identifier in the e-mail.  <br/>(Refer to example configuration below: You can set the *$(Alternate_Title)* variable by writing '*Title=MyValue*' in your e-mail.)|

**Optional options for keys:**

| Option | Type   | Description                                                                |
|--------|------- |----------------------------------------------------------------------------|
| default        | String | Default value, if no other value is given in e-mail or read from metadata.|
| writeMetadata  | List   | Write keyword value to the given metadata tags (overwrite existing).|
| appendMetadata | List   | Add the keyword value to the given metadata tags (append). |
| readMetadata   | List   | Read the first metadata tag, execute the optional regular expresssion and set the keyword variable to that value . If return value was empty read the next tag from list and so on...|
| RegExprPattern | String | optional regular expression for masking the read metadata <br/>e.g., search for '2017' in CreationDate '2017:12:24 18:00:00'|

**Additional options for category keys:**

| Option | Type   | Description                                                                |
|--------|--------|----------------------------------------------------------------------------|
| categoryroot       | String  | Root directory of the category tree. |
| allowsupercategory | Boolean | Specify wether only subdirectories are valid categories. <br/>Refer to category tree above:<br/> `True`: Valid categories are 'photos', 'animals', 'vacation',...<br/> False: Valid categories are 'animals', 'vacation',... but not 'photo'|

#### General Section
| Option | Type   | Description                                                                |
|--------|--------|----------------------------------------------------------------------------|
| protocol     | String  | Used protocol to receive mails. <br/>Act. *imap* and *file* are supported. File could be used for debugging and testing.|
| imapserver   | String  | IMAP server url to fetch e-mails. <br/>e.g., *imap.example.com:123* or *imap.example.com* (default port: 143). |
| smtpserver   | String  | SMTP server url to send e-mails. <br/>e.g., *smtp.example.com:123* or *smtp.example.com* (default port: 587 or 465 in SSL mode. SSL mode is used if default connection is refused.) |
| username     | String  | E-mail account username. |
| password     | String  | E-mail account password. |
| datatypes    | List    | List of datatypes the parser should parse. e.g., *media, documents* |
| logfile      | String  | Path to logfile. |
| cachepath    | String  | Path to cache directory (for incomplete mails). Also used as temp directory if `temppath` is empty or missing. |
| temppath     | String  | **optional** Path to temp directory (in ram-disk maybe). Used for processing attachments. |
| exiftoolpath | String  | **optional** Path to exiftool, if it is used and not set in path-enviorement. |

### Basic structure of a configuration file
This is the basic structure of the configuration file. A commented example follows.
```
[General]
protocol = 
imapserver = 
smtpserver = 
username = 
password = 
datatypes = Data1, Data2
logfile = 
cachepath = 

[Data1]
fileformats = 
keys = Key1, Key2
category = Category1
directory = 
filename = 

[Data2]
...

[DataType]
name = 

[Category1]
...

[Key1]
...

[Key2]
...
```
# Easy start with generated Test Mails
Clone the repository and run the script from `generateTestmails.py` from `Testprogramme/E-Mail/` this will create different E-mails with photos.
Copy this mails to `Parser/InputData/` and run the `MailParser.py` script. You do not need to change the configuration etc. It should work out of the box and moves the images from the e-mails to the output folder. To get full function range you need to install Exiftool and pyexiftool (see [license](#License)).

# More Examples
The examples refer to the configuration file below and the above mentioned category tree

### Save your vacation photos
If you want to save the photos (.jpg-files) from your last vacation in *./myMedia/photos/vacation/2018/* 
(resp. the year you send the mail) and rename them in the way *yyyy-mm_place_0001.jpg*.
Write an e-mail with the following text and add your photos to the attachment:
```
My dear, please save the photos of our last vacation!
Category = vacation
Place = Serengeti National Park
```

### Save your friends favourite cake-recipes
Recipes should be saved as recipe name + friends name or just the filename, if recipes name does not exist.
e.g.:  rename 'buttercake.pdf' to 'Special_Buttercake_anne.pdf' otherwise just 'Special_Buttercake.pdf' 
(or 'buttercake.pdf' if nothing is given):
Attach the file 'buttercake.pdf' to the mail and write:
```
Hi Susi,
this is my famous buttercake. Bye Anne
Title= Special_Buttercake
Author = Anne
```
Both keywords are optional because of the configuration default values.
Trick: Remove the underscore after the recipe name if author is not given (NOT: Special_Buttercake_.pdf).

### Save your diary entry with the vacation Photos
Attachment: vacation-memories.txt
e-mail:
```
here are some memories from our vacation!
Datatype:Photo
Place: Serengeti National Park
Category: vacation
```
This saves the attachment (for Feb. 2018) in *./myMedia/photos/vacation/2018/* as *2018-02-Serengeti National Park_0001.txt*

## Example configuration
This is a configuration file for above mentioned examples:
```
###############################################
# General Settings                            #
###############################################
[General]
protocol = imap
imapserver = imap.example.com
smtpserver = smtp.exapple.com
username = myUserName
password = mySecretPassword
datatypes = Photo, Documents
logfile = ./MailParser.log
exiftoolpath = 
cachepath = ./cache

###############################################
# Datatypes                                   #
###############################################
[Photo]
fileformats = jpg, jpeg, png, bmp
keys = Place, Create_Year, Create_Month
category = Photo_Category
directory = ./myMedia/$(Photo_Category)/$(Mail_Year)
filename = $(Create_Year)-$(Create_Month)-$(Place)_($(**))

[Documents]
fileformats = pdf, txt, docx
keys = Alternate_Title, Author
category = Doc_Category
directory = ./Kitchen/$(Doc_Category)
filename = $(Alternate_Title)_$(Author)

###############################################
# Category keywords                           #
###############################################
[Photo_Category]
name = Category
categoryroot = ./InputData/Categories
allowsupercategory = True
default = unsorted

[Doc_Category]
name = Category
categoryroot = ./InputData/Categories
allowsupercategory = False
default = unsorted

###############################################
# Other keywords                              #
###############################################
[DataType]
name = Datatype

[Alternate_Title]
name = Title
default = $(File_Name)

[Author]
name = Author
readmetadata = Author
default = \\b                       #use double-backslash to escape Ascii commands like \n or \b 

[Create_Year]
name = Create_Year
readmetadata = DateTimeOriginal, CreateDate
regexprpattern = ([0-9]+)(?=:)
default = $(Mail_Year)

[Create_Month]
name = Create_Month
readmetadata = DateTimeOriginal, CreateDate
regexprpattern = (?<=:)([0-9]+)(?=:.+ )
default = $(Mail_Month)

[Place]
name = Place
```

## License
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

The program uses Phil Harvey's Exiftool (https://www.sno.phy.queensu.ca/~phil/exiftool/) 
to change metadata and pyexiftool by Sven Marnach (https://github.com/smarnach/pyexiftool).
