kutoka . agiza Table

_Validation = Table('_Validation')
_Validation.add_field(1,'Table',11552)
_Validation.add_field(2,'Column',11552)
_Validation.add_field(3,'Nullable',3332)
_Validation.add_field(4,'MinValue',4356)
_Validation.add_field(5,'MaxValue',4356)
_Validation.add_field(6,'KeyTable',7679)
_Validation.add_field(7,'KeyColumn',5378)
_Validation.add_field(8,'Category',7456)
_Validation.add_field(9,'Set',7679)
_Validation.add_field(10,'Description',7679)

ActionText = Table('ActionText')
ActionText.add_field(1,'Action',11592)
ActionText.add_field(2,'Description',7936)
ActionText.add_field(3,'Template',7936)

AdminExecuteSequence = Table('AdminExecuteSequence')
AdminExecuteSequence.add_field(1,'Action',11592)
AdminExecuteSequence.add_field(2,'Condition',7679)
AdminExecuteSequence.add_field(3,'Sequence',5378)

Condition = Table('Condition')
Condition.add_field(1,'Feature_',11558)
Condition.add_field(2,'Level',9474)
Condition.add_field(3,'Condition',7679)

AdminUISequence = Table('AdminUISequence')
AdminUISequence.add_field(1,'Action',11592)
AdminUISequence.add_field(2,'Condition',7679)
AdminUISequence.add_field(3,'Sequence',5378)

AdvtExecuteSequence = Table('AdvtExecuteSequence')
AdvtExecuteSequence.add_field(1,'Action',11592)
AdvtExecuteSequence.add_field(2,'Condition',7679)
AdvtExecuteSequence.add_field(3,'Sequence',5378)

AdvtUISequence = Table('AdvtUISequence')
AdvtUISequence.add_field(1,'Action',11592)
AdvtUISequence.add_field(2,'Condition',7679)
AdvtUISequence.add_field(3,'Sequence',5378)

AppId = Table('AppId')
AppId.add_field(1,'AppId',11558)
AppId.add_field(2,'RemoteServerName',7679)
AppId.add_field(3,'LocalService',7679)
AppId.add_field(4,'ServiceParameters',7679)
AppId.add_field(5,'DllSurrogate',7679)
AppId.add_field(6,'ActivateAtStorage',5378)
AppId.add_field(7,'RunAsInteractiveUser',5378)

AppSearch = Table('AppSearch')
AppSearch.add_field(1,'Property',11592)
AppSearch.add_field(2,'Signature_',11592)

Property = Table('Property')
Property.add_field(1,'Property',11592)
Property.add_field(2,'Value',3840)

BBControl = Table('BBControl')
BBControl.add_field(1,'Billboard_',11570)
BBControl.add_field(2,'BBControl',11570)
BBControl.add_field(3,'Type',3378)
BBControl.add_field(4,'X',1282)
BBControl.add_field(5,'Y',1282)
BBControl.add_field(6,'Width',1282)
BBControl.add_field(7,'Height',1282)
BBControl.add_field(8,'Attributes',4356)
BBControl.add_field(9,'Text',7986)

Billboard = Table('Billboard')
Billboard.add_field(1,'Billboard',11570)
Billboard.add_field(2,'Feature_',3366)
Billboard.add_field(3,'Action',7474)
Billboard.add_field(4,'Ordering',5378)

Feature = Table('Feature')
Feature.add_field(1,'Feature',11558)
Feature.add_field(2,'Feature_Parent',7462)
Feature.add_field(3,'Title',8000)
Feature.add_field(4,'Description',8191)
Feature.add_field(5,'Display',5378)
Feature.add_field(6,'Level',1282)
Feature.add_field(7,'Directory_',7496)
Feature.add_field(8,'Attributes',1282)

Binary = Table('Binary')
Binary.add_field(1,'Name',11592)
Binary.add_field(2,'Data',2304)

BindImage = Table('BindImage')
BindImage.add_field(1,'File_',11592)
BindImage.add_field(2,'Path',7679)

File = Table('File')
File.add_field(1,'File',11592)
File.add_field(2,'Component_',3400)
File.add_field(3,'FileName',4095)
File.add_field(4,'FileSize',260)
File.add_field(5,'Version',7496)
File.add_field(6,'Language',7444)
File.add_field(7,'Attributes',5378)
File.add_field(8,'Sequence',1282)

CCPSearch = Table('CCPSearch')
CCPSearch.add_field(1,'Signature_',11592)

CheckBox = Table('CheckBox')
CheckBox.add_field(1,'Property',11592)
CheckBox.add_field(2,'Value',7488)

Class = Table('Class')
Class.add_field(1,'CLSID',11558)
Class.add_field(2,'Context',11552)
Class.add_field(3,'Component_',11592)
Class.add_field(4,'ProgId_Default',7679)
Class.add_field(5,'Description',8191)
Class.add_field(6,'AppId_',7462)
Class.add_field(7,'FileTypeMask',7679)
Class.add_field(8,'Icon_',7496)
Class.add_field(9,'IconIndex',5378)
Class.add_field(10,'DefInprocHandler',7456)
Class.add_field(11,'Argument',7679)
Class.add_field(12,'Feature_',3366)
Class.add_field(13,'Attributes',5378)

Component = Table('Component')
Component.add_field(1,'Component',11592)
Component.add_field(2,'ComponentId',7462)
Component.add_field(3,'Directory_',3400)
Component.add_field(4,'Attributes',1282)
Component.add_field(5,'Condition',7679)
Component.add_field(6,'KeyPath',7496)

Icon = Table('Icon')
Icon.add_field(1,'Name',11592)
Icon.add_field(2,'Data',2304)

ProgId = Table('ProgId')
ProgId.add_field(1,'ProgId',11775)
ProgId.add_field(2,'ProgId_Parent',7679)
ProgId.add_field(3,'Class_',7462)
ProgId.add_field(4,'Description',8191)
ProgId.add_field(5,'Icon_',7496)
ProgId.add_field(6,'IconIndex',5378)

ComboBox = Table('ComboBox')
ComboBox.add_field(1,'Property',11592)
ComboBox.add_field(2,'Order',9474)
ComboBox.add_field(3,'Value',3392)
ComboBox.add_field(4,'Text',8000)

CompLocator = Table('CompLocator')
CompLocator.add_field(1,'Signature_',11592)
CompLocator.add_field(2,'ComponentId',3366)
CompLocator.add_field(3,'Type',5378)

Complus = Table('Complus')
Complus.add_field(1,'Component_',11592)
Complus.add_field(2,'ExpType',13570)

Directory = Table('Directory')
Directory.add_field(1,'Directory',11592)
Directory.add_field(2,'Directory_Parent',7496)
Directory.add_field(3,'DefaultDir',4095)

Control = Table('Control')
Control.add_field(1,'Dialog_',11592)
Control.add_field(2,'Control',11570)
Control.add_field(3,'Type',3348)
Control.add_field(4,'X',1282)
Control.add_field(5,'Y',1282)
Control.add_field(6,'Width',1282)
Control.add_field(7,'Height',1282)
Control.add_field(8,'Attributes',4356)
Control.add_field(9,'Property',7474)
Control.add_field(10,'Text',7936)
Control.add_field(11,'Control_Next',7474)
Control.add_field(12,'Help',7986)

Dialog = Table('Dialog')
Dialog.add_field(1,'Dialog',11592)
Dialog.add_field(2,'HCentering',1282)
Dialog.add_field(3,'VCentering',1282)
Dialog.add_field(4,'Width',1282)
Dialog.add_field(5,'Height',1282)
Dialog.add_field(6,'Attributes',4356)
Dialog.add_field(7,'Title',8064)
Dialog.add_field(8,'Control_First',3378)
Dialog.add_field(9,'Control_Default',7474)
Dialog.add_field(10,'Control_Cancel',7474)

ControlCondition = Table('ControlCondition')
ControlCondition.add_field(1,'Dialog_',11592)
ControlCondition.add_field(2,'Control_',11570)
ControlCondition.add_field(3,'Action',11570)
ControlCondition.add_field(4,'Condition',11775)

ControlEvent = Table('ControlEvent')
ControlEvent.add_field(1,'Dialog_',11592)
ControlEvent.add_field(2,'Control_',11570)
ControlEvent.add_field(3,'Event',11570)
ControlEvent.add_field(4,'Argument',11775)
ControlEvent.add_field(5,'Condition',15871)
ControlEvent.add_field(6,'Ordering',5378)

CreateFolder = Table('CreateFolder')
CreateFolder.add_field(1,'Directory_',11592)
CreateFolder.add_field(2,'Component_',11592)

CustomAction = Table('CustomAction')
CustomAction.add_field(1,'Action',11592)
CustomAction.add_field(2,'Type',1282)
CustomAction.add_field(3,'Source',7496)
CustomAction.add_field(4,'Target',7679)

DrLocator = Table('DrLocator')
DrLocator.add_field(1,'Signature_',11592)
DrLocator.add_field(2,'Parent',15688)
DrLocator.add_field(3,'Path',15871)
DrLocator.add_field(4,'Depth',5378)

DuplicateFile = Table('DuplicateFile')
DuplicateFile.add_field(1,'FileKey',11592)
DuplicateFile.add_field(2,'Component_',3400)
DuplicateFile.add_field(3,'File_',3400)
DuplicateFile.add_field(4,'DestName',8191)
DuplicateFile.add_field(5,'DestFolder',7496)

Environment = Table('Environment')
Environment.add_field(1,'Environment',11592)
Environment.add_field(2,'Name',4095)
Environment.add_field(3,'Value',8191)
Environment.add_field(4,'Component_',3400)

Error = Table('Error')
Error.add_field(1,'Error',9474)
Error.add_field(2,'Message',7936)

EventMapping = Table('EventMapping')
EventMapping.add_field(1,'Dialog_',11592)
EventMapping.add_field(2,'Control_',11570)
EventMapping.add_field(3,'Event',11570)
EventMapping.add_field(4,'Attribute',3378)

Extension = Table('Extension')
Extension.add_field(1,'Extension',11775)
Extension.add_field(2,'Component_',11592)
Extension.add_field(3,'ProgId_',7679)
Extension.add_field(4,'MIME_',7488)
Extension.add_field(5,'Feature_',3366)

MIME = Table('MIME')
MIME.add_field(1,'ContentType',11584)
MIME.add_field(2,'Extension_',3583)
MIME.add_field(3,'CLSID',7462)

FeatureComponents = Table('FeatureComponents')
FeatureComponents.add_field(1,'Feature_',11558)
FeatureComponents.add_field(2,'Component_',11592)

FileSFPCatalog = Table('FileSFPCatalog')
FileSFPCatalog.add_field(1,'File_',11592)
FileSFPCatalog.add_field(2,'SFPCatalog_',11775)

SFPCatalog = Table('SFPCatalog')
SFPCatalog.add_field(1,'SFPCatalog',11775)
SFPCatalog.add_field(2,'Catalog',2304)
SFPCatalog.add_field(3,'Dependency',7424)

Font = Table('Font')
Font.add_field(1,'File_',11592)
Font.add_field(2,'FontTitle',7552)

IniFile = Table('IniFile')
IniFile.add_field(1,'IniFile',11592)
IniFile.add_field(2,'FileName',4095)
IniFile.add_field(3,'DirProperty',7496)
IniFile.add_field(4,'Section',3936)
IniFile.add_field(5,'Key',3968)
IniFile.add_field(6,'Value',4095)
IniFile.add_field(7,'Action',1282)
IniFile.add_field(8,'Component_',3400)

IniLocator = Table('IniLocator')
IniLocator.add_field(1,'Signature_',11592)
IniLocator.add_field(2,'FileName',3583)
IniLocator.add_field(3,'Section',3424)
IniLocator.add_field(4,'Key',3456)
IniLocator.add_field(5,'Field',5378)
IniLocator.add_field(6,'Type',5378)

InstallExecuteSequence = Table('InstallExecuteSequence')
InstallExecuteSequence.add_field(1,'Action',11592)
InstallExecuteSequence.add_field(2,'Condition',7679)
InstallExecuteSequence.add_field(3,'Sequence',5378)

InstallUISequence = Table('InstallUISequence')
InstallUISequence.add_field(1,'Action',11592)
InstallUISequence.add_field(2,'Condition',7679)
InstallUISequence.add_field(3,'Sequence',5378)

IsolatedComponent = Table('IsolatedComponent')
IsolatedComponent.add_field(1,'Component_Shared',11592)
IsolatedComponent.add_field(2,'Component_Application',11592)

LaunchCondition = Table('LaunchCondition')
LaunchCondition.add_field(1,'Condition',11775)
LaunchCondition.add_field(2,'Description',4095)

ListBox = Table('ListBox')
ListBox.add_field(1,'Property',11592)
ListBox.add_field(2,'Order',9474)
ListBox.add_field(3,'Value',3392)
ListBox.add_field(4,'Text',8000)

ListView = Table('ListView')
ListView.add_field(1,'Property',11592)
ListView.add_field(2,'Order',9474)
ListView.add_field(3,'Value',3392)
ListView.add_field(4,'Text',8000)
ListView.add_field(5,'Binary_',7496)

LockPermissions = Table('LockPermissions')
LockPermissions.add_field(1,'LockObject',11592)
LockPermissions.add_field(2,'Table',11552)
LockPermissions.add_field(3,'Domain',15871)
LockPermissions.add_field(4,'User',11775)
LockPermissions.add_field(5,'Permission',4356)

Media = Table('Media')
Media.add_field(1,'DiskId',9474)
Media.add_field(2,'LastSequence',1282)
Media.add_field(3,'DiskPrompt',8000)
Media.add_field(4,'Cabinet',7679)
Media.add_field(5,'VolumeLabel',7456)
Media.add_field(6,'Source',7496)

MoveFile = Table('MoveFile')
MoveFile.add_field(1,'FileKey',11592)
MoveFile.add_field(2,'Component_',3400)
MoveFile.add_field(3,'SourceName',8191)
MoveFile.add_field(4,'DestName',8191)
MoveFile.add_field(5,'SourceFolder',7496)
MoveFile.add_field(6,'DestFolder',3400)
MoveFile.add_field(7,'Options',1282)

MsiAssembly = Table('MsiAssembly')
MsiAssembly.add_field(1,'Component_',11592)
MsiAssembly.add_field(2,'Feature_',3366)
MsiAssembly.add_field(3,'File_Manifest',7496)
MsiAssembly.add_field(4,'File_Application',7496)
MsiAssembly.add_field(5,'Attributes',5378)

MsiAssemblyName = Table('MsiAssemblyName')
MsiAssemblyName.add_field(1,'Component_',11592)
MsiAssemblyName.add_field(2,'Name',11775)
MsiAssemblyName.add_field(3,'Value',3583)

MsiDigitalCertificate = Table('MsiDigitalCertificate')
MsiDigitalCertificate.add_field(1,'DigitalCertificate',11592)
MsiDigitalCertificate.add_field(2,'CertData',2304)

MsiDigitalSignature = Table('MsiDigitalSignature')
MsiDigitalSignature.add_field(1,'Table',11552)
MsiDigitalSignature.add_field(2,'SignObject',11592)
MsiDigitalSignature.add_field(3,'DigitalCertificate_',3400)
MsiDigitalSignature.add_field(4,'Hash',6400)

MsiFileHash = Table('MsiFileHash')
MsiFileHash.add_field(1,'File_',11592)
MsiFileHash.add_field(2,'Options',1282)
MsiFileHash.add_field(3,'HashPart1',260)
MsiFileHash.add_field(4,'HashPart2',260)
MsiFileHash.add_field(5,'HashPart3',260)
MsiFileHash.add_field(6,'HashPart4',260)

MsiPatchHeaders = Table('MsiPatchHeaders')
MsiPatchHeaders.add_field(1,'StreamRef',11558)
MsiPatchHeaders.add_field(2,'Header',2304)

ODBCAttribute = Table('ODBCAttribute')
ODBCAttribute.add_field(1,'Driver_',11592)
ODBCAttribute.add_field(2,'Attribute',11560)
ODBCAttribute.add_field(3,'Value',8191)

ODBCDriver = Table('ODBCDriver')
ODBCDriver.add_field(1,'Driver',11592)
ODBCDriver.add_field(2,'Component_',3400)
ODBCDriver.add_field(3,'Description',3583)
ODBCDriver.add_field(4,'File_',3400)
ODBCDriver.add_field(5,'File_Setup',7496)

ODBCDataSource = Table('ODBCDataSource')
ODBCDataSource.add_field(1,'DataSource',11592)
ODBCDataSource.add_field(2,'Component_',3400)
ODBCDataSource.add_field(3,'Description',3583)
ODBCDataSource.add_field(4,'DriverDescription',3583)
ODBCDataSource.add_field(5,'Registration',1282)

ODBCSourceAttribute = Table('ODBCSourceAttribute')
ODBCSourceAttribute.add_field(1,'DataSource_',11592)
ODBCSourceAttribute.add_field(2,'Attribute',11552)
ODBCSourceAttribute.add_field(3,'Value',8191)

ODBCTranslator = Table('ODBCTranslator')
ODBCTranslator.add_field(1,'Translator',11592)
ODBCTranslator.add_field(2,'Component_',3400)
ODBCTranslator.add_field(3,'Description',3583)
ODBCTranslator.add_field(4,'File_',3400)
ODBCTranslator.add_field(5,'File_Setup',7496)

Patch = Table('Patch')
Patch.add_field(1,'File_',11592)
Patch.add_field(2,'Sequence',9474)
Patch.add_field(3,'PatchSize',260)
Patch.add_field(4,'Attributes',1282)
Patch.add_field(5,'Header',6400)
Patch.add_field(6,'StreamRef_',7462)

PatchPackage = Table('PatchPackage')
PatchPackage.add_field(1,'PatchId',11558)
PatchPackage.add_field(2,'Media_',1282)

PublishComponent = Table('PublishComponent')
PublishComponent.add_field(1,'ComponentId',11558)
PublishComponent.add_field(2,'Qualifier',11775)
PublishComponent.add_field(3,'Component_',11592)
PublishComponent.add_field(4,'AppData',8191)
PublishComponent.add_field(5,'Feature_',3366)

RadioButton = Table('RadioButton')
RadioButton.add_field(1,'Property',11592)
RadioButton.add_field(2,'Order',9474)
RadioButton.add_field(3,'Value',3392)
RadioButton.add_field(4,'X',1282)
RadioButton.add_field(5,'Y',1282)
RadioButton.add_field(6,'Width',1282)
RadioButton.add_field(7,'Height',1282)
RadioButton.add_field(8,'Text',8000)
RadioButton.add_field(9,'Help',7986)

Registry = Table('Registry')
Registry.add_field(1,'Registry',11592)
Registry.add_field(2,'Root',1282)
Registry.add_field(3,'Key',4095)
Registry.add_field(4,'Name',8191)
Registry.add_field(5,'Value',7936)
Registry.add_field(6,'Component_',3400)

RegLocator = Table('RegLocator')
RegLocator.add_field(1,'Signature_',11592)
RegLocator.add_field(2,'Root',1282)
RegLocator.add_field(3,'Key',3583)
RegLocator.add_field(4,'Name',7679)
RegLocator.add_field(5,'Type',5378)

RemoveFile = Table('RemoveFile')
RemoveFile.add_field(1,'FileKey',11592)
RemoveFile.add_field(2,'Component_',3400)
RemoveFile.add_field(3,'FileName',8191)
RemoveFile.add_field(4,'DirProperty',3400)
RemoveFile.add_field(5,'InstallMode',1282)

RemoveIniFile = Table('RemoveIniFile')
RemoveIniFile.add_field(1,'RemoveIniFile',11592)
RemoveIniFile.add_field(2,'FileName',4095)
RemoveIniFile.add_field(3,'DirProperty',7496)
RemoveIniFile.add_field(4,'Section',3936)
RemoveIniFile.add_field(5,'Key',3968)
RemoveIniFile.add_field(6,'Value',8191)
RemoveIniFile.add_field(7,'Action',1282)
RemoveIniFile.add_field(8,'Component_',3400)

RemoveRegistry = Table('RemoveRegistry')
RemoveRegistry.add_field(1,'RemoveRegistry',11592)
RemoveRegistry.add_field(2,'Root',1282)
RemoveRegistry.add_field(3,'Key',4095)
RemoveRegistry.add_field(4,'Name',8191)
RemoveRegistry.add_field(5,'Component_',3400)

ReserveCost = Table('ReserveCost')
ReserveCost.add_field(1,'ReserveKey',11592)
ReserveCost.add_field(2,'Component_',3400)
ReserveCost.add_field(3,'ReserveFolder',7496)
ReserveCost.add_field(4,'ReserveLocal',260)
ReserveCost.add_field(5,'ReserveSource',260)

SelfReg = Table('SelfReg')
SelfReg.add_field(1,'File_',11592)
SelfReg.add_field(2,'Cost',5378)

ServiceControl = Table('ServiceControl')
ServiceControl.add_field(1,'ServiceControl',11592)
ServiceControl.add_field(2,'Name',4095)
ServiceControl.add_field(3,'Event',1282)
ServiceControl.add_field(4,'Arguments',8191)
ServiceControl.add_field(5,'Wait',5378)
ServiceControl.add_field(6,'Component_',3400)

ServiceInstall = Table('ServiceInstall')
ServiceInstall.add_field(1,'ServiceInstall',11592)
ServiceInstall.add_field(2,'Name',3583)
ServiceInstall.add_field(3,'DisplayName',8191)
ServiceInstall.add_field(4,'ServiceType',260)
ServiceInstall.add_field(5,'StartType',260)
ServiceInstall.add_field(6,'ErrorControl',260)
ServiceInstall.add_field(7,'LoadOrderGroup',7679)
ServiceInstall.add_field(8,'Dependencies',7679)
ServiceInstall.add_field(9,'StartName',7679)
ServiceInstall.add_field(10,'Password',7679)
ServiceInstall.add_field(11,'Arguments',7679)
ServiceInstall.add_field(12,'Component_',3400)
ServiceInstall.add_field(13,'Description',8191)

Shortcut = Table('Shortcut')
Shortcut.add_field(1,'Shortcut',11592)
Shortcut.add_field(2,'Directory_',3400)
Shortcut.add_field(3,'Name',3968)
Shortcut.add_field(4,'Component_',3400)
Shortcut.add_field(5,'Target',3400)
Shortcut.add_field(6,'Arguments',7679)
Shortcut.add_field(7,'Description',8191)
Shortcut.add_field(8,'Hotkey',5378)
Shortcut.add_field(9,'Icon_',7496)
Shortcut.add_field(10,'IconIndex',5378)
Shortcut.add_field(11,'ShowCmd',5378)
Shortcut.add_field(12,'WkDir',7496)

Signature = Table('Signature')
Signature.add_field(1,'Signature',11592)
Signature.add_field(2,'FileName',3583)
Signature.add_field(3,'MinVersion',7444)
Signature.add_field(4,'MaxVersion',7444)
Signature.add_field(5,'MinSize',4356)
Signature.add_field(6,'MaxSize',4356)
Signature.add_field(7,'MinDate',4356)
Signature.add_field(8,'MaxDate',4356)
Signature.add_field(9,'Languages',7679)

TextStyle = Table('TextStyle')
TextStyle.add_field(1,'TextStyle',11592)
TextStyle.add_field(2,'FaceName',3360)
TextStyle.add_field(3,'Size',1282)
TextStyle.add_field(4,'Color',4356)
TextStyle.add_field(5,'StyleBits',5378)

TypeLib = Table('TypeLib')
TypeLib.add_field(1,'LibID',11558)
TypeLib.add_field(2,'Language',9474)
TypeLib.add_field(3,'Component_',11592)
TypeLib.add_field(4,'Version',4356)
TypeLib.add_field(5,'Description',8064)
TypeLib.add_field(6,'Directory_',7496)
TypeLib.add_field(7,'Feature_',3366)
TypeLib.add_field(8,'Cost',4356)

UIText = Table('UIText')
UIText.add_field(1,'Key',11592)
UIText.add_field(2,'Text',8191)

Upgrade = Table('Upgrade')
Upgrade.add_field(1,'UpgradeCode',11558)
Upgrade.add_field(2,'VersionMin',15636)
Upgrade.add_field(3,'VersionMax',15636)
Upgrade.add_field(4,'Language',15871)
Upgrade.add_field(5,'Attributes',8452)
Upgrade.add_field(6,'Remove',7679)
Upgrade.add_field(7,'ActionProperty',3400)

Verb = Table('Verb')
Verb.add_field(1,'Extension_',11775)
Verb.add_field(2,'Verb',11552)
Verb.add_field(3,'Sequence',5378)
Verb.add_field(4,'Command',8191)
Verb.add_field(5,'Argument',8191)

tables=[_Validation, ActionText, AdminExecuteSequence, Condition, AdminUISequence, AdvtExecuteSequence, AdvtUISequence, AppId, AppSearch, Property, BBControl, Billboard, Feature, Binary, BindImage, File, CCPSearch, CheckBox, Class, Component, Icon, ProgId, ComboBox, CompLocator, Complus, Directory, Control, Dialog, ControlCondition, ControlEvent, CreateFolder, CustomAction, DrLocator, DuplicateFile, Environment, Error, EventMapping, Extension, MIME, FeatureComponents, FileSFPCatalog, SFPCatalog, Font, IniFile, IniLocator, InstallExecuteSequence, InstallUISequence, IsolatedComponent, LaunchCondition, ListBox, ListView, LockPermissions, Media, MoveFile, MsiAssembly, MsiAssemblyName, MsiDigitalCertificate, MsiDigitalSignature, MsiFileHash, MsiPatchHeaders, ODBCAttribute, ODBCDriver, ODBCDataSource, ODBCSourceAttribute, ODBCTranslator, Patch, PatchPackage, PublishComponent, RadioButton, Registry, RegLocator, RemoveFile, RemoveIniFile, RemoveRegistry, ReserveCost, SelfReg, ServiceControl, ServiceInstall, Shortcut, Signature, TextStyle, TypeLib, UIText, Upgrade, Verb]

_Validation_records = [
('_Validation','Table','N',Tupu, Tupu, Tupu, Tupu, 'Identifier',Tupu, 'Name of table',),
('_Validation','Column','N',Tupu, Tupu, Tupu, Tupu, 'Identifier',Tupu, 'Name of column',),
('_Validation','Description','Y',Tupu, Tupu, Tupu, Tupu, 'Text',Tupu, 'Description of column',),
('_Validation','Set','Y',Tupu, Tupu, Tupu, Tupu, 'Text',Tupu, 'Set of values that are permitted',),
('_Validation','Category','Y',Tupu, Tupu, Tupu, Tupu, Tupu, 'Text;Formatted;Template;Condition;Guid;Path;Version;Language;Identifier;Binary;UpperCase;LowerCase;Filename;Paths;AnyPath;WildCardFilename;RegPath;KeyFormatted;CustomSource;Property;Cabinet;Shortcut;URL','String category',),
('_Validation','KeyColumn','Y',1,32,Tupu, Tupu, Tupu, Tupu, 'Column to which foreign key connects',),
('_Validation','KeyTable','Y',Tupu, Tupu, Tupu, Tupu, 'Identifier',Tupu, 'For foreign key, Name of table to which data must link',),
('_Validation','MaxValue','Y',-2147483647,2147483647,Tupu, Tupu, Tupu, Tupu, 'Maximum value allowed',),
('_Validation','MinValue','Y',-2147483647,2147483647,Tupu, Tupu, Tupu, Tupu, 'Minimum value allowed',),
('_Validation','Nullable','N',Tupu, Tupu, Tupu, Tupu, Tupu, 'Y;N;@','Whether the column ni nullable',),
('ActionText','Description','Y',Tupu, Tupu, Tupu, Tupu, 'Text',Tupu, 'Localized description displayed kwenye progress dialog na log when action ni executing.',),
('ActionText','Action','N',Tupu, Tupu, Tupu, Tupu, 'Identifier',Tupu, 'Name of action to be described.',),
('ActionText','Template','Y',Tupu, Tupu, Tupu, Tupu, 'Template',Tupu, 'Optional localized format template used to format action data records kila display during action execution.',),
('AdminExecuteSequence','Action','N',Tupu, Tupu, Tupu, Tupu, 'Identifier',Tupu, 'Name of action to invoke, either kwenye the engine ama the handler DLL.',),
('AdminExecuteSequence','Condition','Y',Tupu, Tupu, Tupu, Tupu, 'Condition',Tupu, 'Optional expression which skips the action ikiwa evaluates to expUongo.If the expression syntax ni invalid, the engine will terminate, returning iesBadActionData.',),
('AdminExecuteSequence','Sequence','Y',-4,32767,Tupu, Tupu, Tupu, Tupu, 'Number that determines the sort order kwenye which the actions are to be executed.  Leave blank to suppress action.',),
('Condition','Condition','Y',Tupu, Tupu, Tupu, Tupu, 'Condition',Tupu, 'Expression evaluated to determine ikiwa Level kwenye the Feature table ni to change.',),
('Condition','Feature_','N',Tupu, Tupu, 'Feature',1,'Identifier',Tupu, 'Reference to a Feature entry kwenye Feature table.',),
('Condition','Level','N',0,32767,Tupu, Tupu, Tupu, Tupu, 'New selection Level to set kwenye Feature table ikiwa Condition evaluates to TRUE.',),
('AdminUISequence','Action','N',Tupu, Tupu, Tupu, Tupu, 'Identifier',Tupu, 'Name of action to invoke, either kwenye the engine ama the handler DLL.',),
('AdminUISequence','Condition','Y',Tupu, Tupu, Tupu, Tupu, 'Condition',Tupu, 'Optional expression which skips the action ikiwa evaluates to expUongo.If the expression syntax ni invalid, the engine will terminate, returning iesBadActionData.',),
('AdminUISequence','Sequence','Y',-4,32767,Tupu, Tupu, Tupu, Tupu, 'Number that determines the sort order kwenye which the actions are to be executed.  Leave blank to suppress action.',),
('AdvtExecuteSequence','Action','N',Tupu, Tupu, Tupu, Tupu, 'Identifier',Tupu, 'Name of action to invoke, either kwenye the engine ama the handler DLL.',),
('AdvtExecuteSequence','Condition','Y',Tupu, Tupu, Tupu, Tupu, 'Condition',Tupu, 'Optional expression which skips the action ikiwa evaluates to expUongo.If the expression syntax ni invalid, the engine will terminate, returning iesBadActionData.',),
('AdvtExecuteSequence','Sequence','Y',-4,32767,Tupu, Tupu, Tupu, Tupu, 'Number that determines the sort order kwenye which the actions are to be executed.  Leave blank to suppress action.',),
('AdvtUISequence','Action','N',Tupu, Tupu, Tupu, Tupu, 'Identifier',Tupu, 'Name of action to invoke, either kwenye the engine ama the handler DLL.',),
('AdvtUISequence','Condition','Y',Tupu, Tupu, Tupu, Tupu, 'Condition',Tupu, 'Optional expression which skips the action ikiwa evaluates to expUongo.If the expression syntax ni invalid, the engine will terminate, returning iesBadActionData.',),
('AdvtUISequence','Sequence','Y',-4,32767,Tupu, Tupu, Tupu, Tupu, 'Number that determines the sort order kwenye which the actions are to be executed.  Leave blank to suppress action.',),
('AppId','AppId','N',Tupu, Tupu, Tupu, Tupu, 'Guid',Tupu, Tupu, ),
('AppId','ActivateAtStorage','Y',0,1,Tupu, Tupu, Tupu, Tupu, Tupu, ),
('AppId','DllSurrogate','Y',Tupu, Tupu, Tupu, Tupu, 'Text',Tupu, Tupu, ),
('AppId','LocalService','Y',Tupu, Tupu, Tupu, Tupu, 'Text',Tupu, Tupu, ),
('AppId','RemoteServerName','Y',Tupu, Tupu, Tupu, Tupu, 'Formatted',Tupu, Tupu, ),
('AppId','RunAsInteractiveUser','Y',0,1,Tupu, Tupu, Tupu, Tupu, Tupu, ),
('AppId','ServiceParameters','Y',Tupu, Tupu, Tupu, Tupu, 'Text',Tupu, Tupu, ),
('AppSearch','Property','N',Tupu, Tupu, Tupu, Tupu, 'Identifier',Tupu, 'The property associated ukijumuisha a Signature',),
('AppSearch','Signature_','N',Tupu, Tupu, 'Signature;RegLocator;IniLocator;DrLocator;CompLocator',1,'Identifier',Tupu, 'The Signature_ represents a unique file signature na ni also the foreign key kwenye the Signature,  RegLocator, IniLocator, CompLocator na the DrLocator tables.',),
('Property','Property','N',Tupu, Tupu, Tupu, Tupu, 'Identifier',Tupu, 'Name of property, uppercase ikiwa settable by launcher ama loader.',),
('Property','Value','N',Tupu, Tupu, Tupu, Tupu, 'Text',Tupu, 'String value kila property.  Never null ama empty.',),
('BBControl','Type','N',Tupu, Tupu, Tupu, Tupu, 'Identifier',Tupu, 'The type of the control.',),
('BBControl','Y','N',0,32767,Tupu, Tupu, Tupu, Tupu, 'Vertical coordinate of the upper left corner of the bounding rectangle of the control.',),
('BBControl','Text','Y',Tupu, Tupu, Tupu, Tupu, 'Text',Tupu, 'A string used to set the initial text contained within a control (ikiwa appropriate).',),
('BBControl','BBControl','N',Tupu, Tupu, Tupu, Tupu, 'Identifier',Tupu, 'Name of the control. This name must be unique within a billboard, but can repeat on different billboard.',),
('BBControl','Attributes','Y',0,2147483647,Tupu, Tupu, Tupu, Tupu, 'A 32-bit word that specifies the attribute flags to be applied to this control.',),
('BBControl','Billboard_','N',Tupu, Tupu, 'Billboard',1,'Identifier',Tupu, 'External key to the Billboard table, name of the billboard.',),
('BBControl','Height','N',0,32767,Tupu, Tupu, Tupu, Tupu, 'Height of the bounding rectangle of the control.',),
('BBControl','Width','N',0,32767,Tupu, Tupu, Tupu, Tupu, 'Width of the bounding rectangle of the control.',),
('BBControl','X','N',0,32767,Tupu, Tupu, Tupu, Tupu, 'Horizontal coordinate of the upper left corner of the bounding rectangle of the control.',),
('Billboard','Action','Y',Tupu, Tupu, Tupu, Tupu, 'Identifier',Tupu, 'The name of an action. The billboard ni displayed during the progress messages received kutoka this action.',),
('Billboard','Billboard','N',Tupu, Tupu, Tupu, Tupu, 'Identifier',Tupu, 'Name of the billboard.',),
('Billboard','Feature_','N',Tupu, Tupu, 'Feature',1,'Identifier',Tupu, 'An external key to the Feature Table. The billboard ni shown only ikiwa this feature ni being installed.',),
('Billboard','Ordering','Y',0,32767,Tupu, Tupu, Tupu, Tupu, 'A positive integer. If there ni more than one billboard corresponding to an action they will be shown kwenye the order defined by this column.',),
('Feature','Description','Y',Tupu, Tupu, Tupu, Tupu, 'Text',Tupu, 'Longer descriptive text describing a visible feature item.',),
('Feature','Attributes','N',Tupu, Tupu, Tupu, Tupu, Tupu, '0;1;2;4;5;6;8;9;10;16;17;18;20;21;22;24;25;26;32;33;34;36;37;38;48;49;50;52;53;54','Feature attributes',),
('Feature','Feature','N',Tupu, Tupu, Tupu, Tupu, 'Identifier',Tupu, 'Primary key used to identify a particular feature record.',),
('Feature','Directory_','Y',Tupu, Tupu, 'Directory',1,'UpperCase',Tupu, 'The name of the Directory that can be configured by the UI. A non-null value will enable the browse button.',),
('Feature','Level','N',0,32767,Tupu, Tupu, Tupu, Tupu, 'The install level at which record will be initially selected. An install level of 0 will disable an item na prevent its display.',),
('Feature','Title','Y',Tupu, Tupu, Tupu, Tupu, 'Text',Tupu, 'Short text identifying a visible feature item.',),
('Feature','Display','Y',0,32767,Tupu, Tupu, Tupu, Tupu, 'Numeric sort order, used to force a specific display ordering.',),
('Feature','Feature_Parent','Y',Tupu, Tupu, 'Feature',1,'Identifier',Tupu, 'Optional key of a parent record kwenye the same table. If the parent ni sio selected, then the record will sio be installed. Null indicates a root item.',),
('Binary','Name','N',Tupu, Tupu, Tupu, Tupu, 'Identifier',Tupu, 'Unique key identifying the binary data.',),
('Binary','Data','N',Tupu, Tupu, Tupu, Tupu, 'Binary',Tupu, 'The unformatted binary data.',),
('BindImage','File_','N',Tupu, Tupu, 'File',1,'Identifier',Tupu, 'The index into the File table. This must be an executable file.',),
('BindImage','Path','Y',Tupu, Tupu, Tupu, Tupu, 'Paths',Tupu, 'A list of ;  delimited paths that represent the paths to be searched kila the agiza DLLS. The list ni usually a list of properties each enclosed within square brackets [] .',),
('File','Sequence','N',1,32767,Tupu, Tupu, Tupu, Tupu, 'Sequence ukijumuisha respect to the media images; order must track cabinet order.',),
('File','Attributes','Y',0,32767,Tupu, Tupu, Tupu, Tupu, 'Integer containing bit flags representing file attributes (ukijumuisha the decimal value of each bit position kwenye parentheses)',),
('File','File','N',Tupu, Tupu, Tupu, Tupu, 'Identifier',Tupu, 'Primary key, non-localized token, must match identifier kwenye cabinet.  For uncompressed files, this field ni ignored.',),
('File','Component_','N',Tupu, Tupu, 'Component',1,'Identifier',Tupu, 'Foreign key referencing Component that controls the file.',),
('File','FileName','N',Tupu, Tupu, Tupu, Tupu, 'Filename',Tupu, 'File name used kila installation, may be localized.  This may contain a "short name|long name" pair.',),
('File','FileSize','N',0,2147483647,Tupu, Tupu, Tupu, Tupu, 'Size of file kwenye bytes (integer).',),
('File','Language','Y',Tupu, Tupu, Tupu, Tupu, 'Language',Tupu, 'List of decimal language Ids, comma-separated ikiwa more than one.',),
('File','Version','Y',Tupu, Tupu, 'File',1,'Version',Tupu, 'Version string kila versioned files;  Blank kila unversioned files.',),
('CCPSearch','Signature_','N',Tupu, Tupu, 'Signature;RegLocator;IniLocator;DrLocator;CompLocator',1,'Identifier',Tupu, 'The Signature_ represents a unique file signature na ni also the foreign key kwenye the Signature,  RegLocator, IniLocator, CompLocator na the DrLocator tables.',),
('CheckBox','Property','N',Tupu, Tupu, Tupu, Tupu, 'Identifier',Tupu, 'A named property to be tied to the item.',),
('CheckBox','Value','Y',Tupu, Tupu, Tupu, Tupu, 'Formatted',Tupu, 'The value string associated ukijumuisha the item.',),
('Class','Description','Y',Tupu, Tupu, Tupu, Tupu, 'Text',Tupu, 'Localized description kila the Class.',),
('Class','Attributes','Y',Tupu, 32767,Tupu, Tupu, Tupu, Tupu, 'Class registration attributes.',),
('Class','Feature_','N',Tupu, Tupu, 'Feature',1,'Identifier',Tupu, 'Required foreign key into the Feature Table, specifying the feature to validate ama install kwenye order kila the CLSID factory to be operational.',),
('Class','AppId_','Y',Tupu, Tupu, 'AppId',1,'Guid',Tupu, 'Optional AppID containing DCOM information kila associated application (string GUID).',),
('Class','Argument','Y',Tupu, Tupu, Tupu, Tupu, 'Formatted',Tupu, 'optional argument kila LocalServers.',),
('Class','CLSID','N',Tupu, Tupu, Tupu, Tupu, 'Guid',Tupu, 'The CLSID of an OLE factory.',),
('Class','Component_','N',Tupu, Tupu, 'Component',1,'Identifier',Tupu, 'Required foreign key into the Component Table, specifying the component kila which to rudisha a path when called through LocateComponent.',),
('Class','Context','N',Tupu, Tupu, Tupu, Tupu, 'Identifier',Tupu, 'The numeric server context kila this server. CLSCTX_xxxx',),
('Class','DefInprocHandler','Y',Tupu, Tupu, Tupu, Tupu, 'Filename','1;2;3','Optional default inproc handler.  Only optionally provided ikiwa Context=CLSCTX_LOCAL_SERVER.  Typically "ole32.dll" ama "mapi32.dll"',),
('Class','FileTypeMask','Y',Tupu, Tupu, Tupu, Tupu, 'Text',Tupu, 'Optional string containing information kila the HKCRthis CLSID) key. If multiple patterns exist, they must be delimited by a semicolon, na numeric subkeys will be generated: 0,1,2...',),
('Class','Icon_','Y',Tupu, Tupu, 'Icon',1,'Identifier',Tupu, 'Optional foreign key into the Icon Table, specifying the icon file associated ukijumuisha this CLSID. Will be written under the DefaultIcon key.',),
('Class','IconIndex','Y',-32767,32767,Tupu, Tupu, Tupu, Tupu, 'Optional icon index.',),
('Class','ProgId_Default','Y',Tupu, Tupu, 'ProgId',1,'Text',Tupu, 'Optional ProgId associated ukijumuisha this CLSID.',),
('Component','Condition','Y',Tupu, Tupu, Tupu, Tupu, 'Condition',Tupu, "A conditional statement that will disable this component ikiwa the specified condition evaluates to the 'Kweli' state. If a component ni disabled, it will sio be installed, regardless of the 'Action' state associated ukijumuisha the component.",),
('Component','Attributes','N',Tupu, Tupu, Tupu, Tupu, Tupu, Tupu, 'Remote execution option, one of irsEnum',),
('Component','Component','N',Tupu, Tupu, Tupu, Tupu, 'Identifier',Tupu, 'Primary key used to identify a particular component record.',),
('Component','ComponentId','Y',Tupu, Tupu, Tupu, Tupu, 'Guid',Tupu, 'A string GUID unique to this component, version, na language.',),
('Component','Directory_','N',Tupu, Tupu, 'Directory',1,'Identifier',Tupu, 'Required key of a Directory table record. This ni actually a property name whose value contains the actual path, set either by the AppSearch action ama ukijumuisha the default setting obtained kutoka the Directory table.',),
('Component','KeyPath','Y',Tupu, Tupu, 'File;Registry;ODBCDataSource',1,'Identifier',Tupu, 'Either the primary key into the File table, Registry table, ama ODBCDataSource table. This extract path ni stored when the component ni installed, na ni used to detect the presence of the component na to rudisha the path to it.',),
('Icon','Name','N',Tupu, Tupu, Tupu, Tupu, 'Identifier',Tupu, 'Primary key. Name of the icon file.',),
('Icon','Data','N',Tupu, Tupu, Tupu, Tupu, 'Binary',Tupu, 'Binary stream. The binary icon data kwenye PE (.DLL ama .EXE) ama icon (.ICO) format.',),
('ProgId','Description','Y',Tupu, Tupu, Tupu, Tupu, 'Text',Tupu, 'Localized description kila the Program identifier.',),
('ProgId','Icon_','Y',Tupu, Tupu, 'Icon',1,'Identifier',Tupu, 'Optional foreign key into the Icon Table, specifying the icon file associated ukijumuisha this ProgId. Will be written under the DefaultIcon key.',),
('ProgId','IconIndex','Y',-32767,32767,Tupu, Tupu, Tupu, Tupu, 'Optional icon index.',),
('ProgId','ProgId','N',Tupu, Tupu, Tupu, Tupu, 'Text',Tupu, 'The Program Identifier. Primary key.',),
('ProgId','Class_','Y',Tupu, Tupu, 'Class',1,'Guid',Tupu, 'The CLSID of an OLE factory corresponding to the ProgId.',),
('ProgId','ProgId_Parent','Y',Tupu, Tupu, 'ProgId',1,'Text',Tupu, 'The Parent Program Identifier. If specified, the ProgId column becomes a version independent prog id.',),
('ComboBox','Text','Y',Tupu, Tupu, Tupu, Tupu, 'Formatted',Tupu, 'The visible text to be assigned to the item. Optional. If this entry ama the entire column ni missing, the text ni the same as the value.',),
('ComboBox','Property','N',Tupu, Tupu, Tupu, Tupu, 'Identifier',Tupu, 'A named property to be tied to this item. All the items tied to the same property become part of the same combobox.',),
('ComboBox','Value','N',Tupu, Tupu, Tupu, Tupu, 'Formatted',Tupu, 'The value string associated ukijumuisha this item. Selecting the line will set the associated property to this value.',),
('ComboBox','Order','N',1,32767,Tupu, Tupu, Tupu, Tupu, 'A positive integer used to determine the ordering of the items within one list.\tThe integers do sio have to be consecutive.',),
('CompLocator','Type','Y',0,1,Tupu, Tupu, Tupu, Tupu, 'A boolean value that determines ikiwa the registry value ni a filename ama a directory location.',),
('CompLocator','Signature_','N',Tupu, Tupu, Tupu, Tupu, 'Identifier',Tupu, 'The table key. The Signature_ represents a unique file signature na ni also the foreign key kwenye the Signature table.',),
('CompLocator','ComponentId','N',Tupu, Tupu, Tupu, Tupu, 'Guid',Tupu, 'A string GUID unique to this component, version, na language.',),
('Complus','Component_','N',Tupu, Tupu, 'Component',1,'Identifier',Tupu, 'Foreign key referencing Component that controls the ComPlus component.',),
('Complus','ExpType','Y',0,32767,Tupu, Tupu, Tupu, Tupu, 'ComPlus component attributes.',),
('Directory','Directory','N',Tupu, Tupu, Tupu, Tupu, 'Identifier',Tupu, 'Unique identifier kila directory entry, primary key. If a property by this name ni defined, it contains the full path to the directory.',),
('Directory','DefaultDir','N',Tupu, Tupu, Tupu, Tupu, 'DefaultDir',Tupu, "The default sub-path under parent's path.",),
('Directory','Directory_Parent','Y',Tupu, Tupu, 'Directory',1,'Identifier',Tupu, 'Reference to the entry kwenye this table specifying the default parent directory. A record parented to itself ama ukijumuisha a Null parent represents a root of the install tree.',),
('Control','Type','N',Tupu, Tupu, Tupu, Tupu, 'Identifier',Tupu, 'The type of the control.',),
('Control','Y','N',0,32767,Tupu, Tupu, Tupu, Tupu, 'Vertical coordinate of the upper left corner of the bounding rectangle of the control.',),
('Control','Text','Y',Tupu, Tupu, Tupu, Tupu, 'Formatted',Tupu, 'A string used to set the initial text contained within a control (ikiwa appropriate).',),
('Control','Property','Y',Tupu, Tupu, Tupu, Tupu, 'Identifier',Tupu, 'The name of a defined property to be linked to this control. ',),
('Control','Attributes','Y',0,2147483647,Tupu, Tupu, Tupu, Tupu, 'A 32-bit word that specifies the attribute flags to be applied to this control.',),
('Control','Height','N',0,32767,Tupu, Tupu, Tupu, Tupu, 'Height of the bounding rectangle of the control.',),
('Control','Width','N',0,32767,Tupu, Tupu, Tupu, Tupu, 'Width of the bounding rectangle of the control.',),
('Control','X','N',0,32767,Tupu, Tupu, Tupu, Tupu, 'Horizontal coordinate of the upper left corner of the bounding rectangle of the control.',),
('Control','Control','N',Tupu, Tupu, Tupu, Tupu, 'Identifier',Tupu, 'Name of the control. This name must be unique within a dialog, but can repeat on different dialogs. ',),
('Control','Control_Next','Y',Tupu, Tupu, 'Control',2,'Identifier',Tupu, 'The name of an other control on the same dialog. This link defines the tab order of the controls. The links have to form one ama more cycles!',),
('Control','Dialog_','N',Tupu, Tupu, 'Dialog',1,'Identifier',Tupu, 'External key to the Dialog table, name of the dialog.',),
('Control','Help','Y',Tupu, Tupu, Tupu, Tupu, 'Text',Tupu, 'The help strings used ukijumuisha the button. The text ni optional. ',),
('Dialog','Attributes','Y',0,2147483647,Tupu, Tupu, Tupu, Tupu, 'A 32-bit word that specifies the attribute flags to be applied to this dialog.',),
('Dialog','Height','N',0,32767,Tupu, Tupu, Tupu, Tupu, 'Height of the bounding rectangle of the dialog.',),
('Dialog','Width','N',0,32767,Tupu, Tupu, Tupu, Tupu, 'Width of the bounding rectangle of the dialog.',),
('Dialog','Dialog','N',Tupu, Tupu, Tupu, Tupu, 'Identifier',Tupu, 'Name of the dialog.',),
('Dialog','Control_Cancel','Y',Tupu, Tupu, 'Control',2,'Identifier',Tupu, 'Defines the cancel control. Hitting escape ama clicking on the close icon on the dialog ni equivalent to pushing this button.',),
('Dialog','Control_Default','Y',Tupu, Tupu, 'Control',2,'Identifier',Tupu, 'Defines the default control. Hitting rudisha ni equivalent to pushing this button.',),
('Dialog','Control_First','N',Tupu, Tupu, 'Control',2,'Identifier',Tupu, 'Defines the control that has the focus when the dialog ni created.',),
('Dialog','HCentering','N',0,100,Tupu, Tupu, Tupu, Tupu, 'Horizontal position of the dialog on a 0-100 scale. 0 means left end, 100 means right end of the screen, 50 center.',),
('Dialog','Title','Y',Tupu, Tupu, Tupu, Tupu, 'Formatted',Tupu, "A text string specifying the title to be displayed kwenye the title bar of the dialog's window.",),
('Dialog','VCentering','N',0,100,Tupu, Tupu, Tupu, Tupu, 'Vertical position of the dialog on a 0-100 scale. 0 means top end, 100 means bottom end of the screen, 50 center.',),
('ControlCondition','Action','N',Tupu, Tupu, Tupu, Tupu, Tupu, 'Default;Disable;Enable;Hide;Show','The desired action to be taken on the specified control.',),
('ControlCondition','Condition','N',Tupu, Tupu, Tupu, Tupu, 'Condition',Tupu, 'A standard conditional statement that specifies under which conditions the action should be triggered.',),
('ControlCondition','Dialog_','N',Tupu, Tupu, 'Dialog',1,'Identifier',Tupu, 'A foreign key to the Dialog table, name of the dialog.',),
('ControlCondition','Control_','N',Tupu, Tupu, 'Control',2,'Identifier',Tupu, 'A foreign key to the Control table, name of the control.',),
('ControlEvent','Condition','Y',Tupu, Tupu, Tupu, Tupu, 'Condition',Tupu, 'A standard conditional statement that specifies under which conditions an event should be triggered.',),
('ControlEvent','Ordering','Y',0,2147483647,Tupu, Tupu, Tupu, Tupu, 'An integer used to order several events tied to the same control. Can be left blank.',),
('ControlEvent','Argument','N',Tupu, Tupu, Tupu, Tupu, 'Formatted',Tupu, 'A value to be used as a modifier when triggering a particular event.',),
('ControlEvent','Dialog_','N',Tupu, Tupu, 'Dialog',1,'Identifier',Tupu, 'A foreign key to the Dialog table, name of the dialog.',),
('ControlEvent','Control_','N',Tupu, Tupu, 'Control',2,'Identifier',Tupu, 'A foreign key to the Control table, name of the control',),
('ControlEvent','Event','N',Tupu, Tupu, Tupu, Tupu, 'Formatted',Tupu, 'An identifier that specifies the type of the event that should take place when the user interacts ukijumuisha control specified by the first two entries.',),
('CreateFolder','Component_','N',Tupu, Tupu, 'Component',1,'Identifier',Tupu, 'Foreign key into the Component table.',),
('CreateFolder','Directory_','N',Tupu, Tupu, 'Directory',1,'Identifier',Tupu, 'Primary key, could be foreign key into the Directory table.',),
('CustomAction','Type','N',1,16383,Tupu, Tupu, Tupu, Tupu, 'The numeric custom action type, consisting of source location, code type, entry, option flags.',),
('CustomAction','Action','N',Tupu, Tupu, Tupu, Tupu, 'Identifier',Tupu, 'Primary key, name of action, normally appears kwenye sequence table unless private use.',),
('CustomAction','Source','Y',Tupu, Tupu, Tupu, Tupu, 'CustomSource',Tupu, 'The table reference of the source of the code.',),
('CustomAction','Target','Y',Tupu, Tupu, Tupu, Tupu, 'Formatted',Tupu, 'Execution parameter, depends on the type of custom action',),
('DrLocator','Signature_','N',Tupu, Tupu, Tupu, Tupu, 'Identifier',Tupu, 'The Signature_ represents a unique file signature na ni also the foreign key kwenye the Signature table.',),
('DrLocator','Path','Y',Tupu, Tupu, Tupu, Tupu, 'AnyPath',Tupu, 'The path on the user system. This ni either a subpath below the value of the Parent ama a full path. The path may contain properties enclosed within [ ] that will be expanded.',),
('DrLocator','Depth','Y',0,32767,Tupu, Tupu, Tupu, Tupu, 'The depth below the path to which the Signature_ ni recursively searched. If absent, the depth ni assumed to be 0.',),
('DrLocator','Parent','Y',Tupu, Tupu, Tupu, Tupu, 'Identifier',Tupu, 'The parent file signature. It ni also a foreign key kwenye the Signature table. If null na the Path column does sio expand to a full path, then all the fixed drives of the user system are searched using the Path.',),
('DuplicateFile','File_','N',Tupu, Tupu, 'File',1,'Identifier',Tupu, 'Foreign key referencing the source file to be duplicated.',),
('DuplicateFile','Component_','N',Tupu, Tupu, 'Component',1,'Identifier',Tupu, 'Foreign key referencing Component that controls the duplicate file.',),
('DuplicateFile','DestFolder','Y',Tupu, Tupu, Tupu, Tupu, 'Identifier',Tupu, 'Name of a property whose value ni assumed to resolve to the full pathname to a destination folder.',),
('DuplicateFile','DestName','Y',Tupu, Tupu, Tupu, Tupu, 'Filename',Tupu, 'Filename to be given to the duplicate file.',),
('DuplicateFile','FileKey','N',Tupu, Tupu, Tupu, Tupu, 'Identifier',Tupu, 'Primary key used to identify a particular file entry',),
('Environment','Name','N',Tupu, Tupu, Tupu, Tupu, 'Text',Tupu, 'The name of the environmental value.',),
('Environment','Value','Y',Tupu, Tupu, Tupu, Tupu, 'Formatted',Tupu, 'The value to set kwenye the environmental settings.',),
('Environment','Component_','N',Tupu, Tupu, 'Component',1,'Identifier',Tupu, 'Foreign key into the Component table referencing component that controls the installing of the environmental value.',),
('Environment','Environment','N',Tupu, Tupu, Tupu, Tupu, 'Identifier',Tupu, 'Unique identifier kila the environmental variable setting',),
('Error','Error','N',0,32767,Tupu, Tupu, Tupu, Tupu, 'Integer error number, obtained kutoka header file IError(...) macros.',),
('Error','Message','Y',Tupu, Tupu, Tupu, Tupu, 'Template',Tupu, 'Error formatting template, obtained kutoka user ed. ama localizers.',),
('EventMapping','Dialog_','N',Tupu, Tupu, 'Dialog',1,'Identifier',Tupu, 'A foreign key to the Dialog table, name of the Dialog.',),
('EventMapping','Control_','N',Tupu, Tupu, 'Control',2,'Identifier',Tupu, 'A foreign key to the Control table, name of the control.',),
('EventMapping','Event','N',Tupu, Tupu, Tupu, Tupu, 'Identifier',Tupu, 'An identifier that specifies the type of the event that the control subscribes to.',),
('EventMapping','Attribute','N',Tupu, Tupu, Tupu, Tupu, 'Identifier',Tupu, 'The name of the control attribute, that ni set when this event ni received.',),
('Extension','Feature_','N',Tupu, Tupu, 'Feature',1,'Identifier',Tupu, 'Required foreign key into the Feature Table, specifying the feature to validate ama install kwenye order kila the CLSID factory to be operational.',),
('Extension','Component_','N',Tupu, Tupu, 'Component',1,'Identifier',Tupu, 'Required foreign key into the Component Table, specifying the component kila which to rudisha a path when called through LocateComponent.',),
('Extension','Extension','N',Tupu, Tupu, Tupu, Tupu, 'Text',Tupu, 'The extension associated ukijumuisha the table row.',),
('Extension','MIME_','Y',Tupu, Tupu, 'MIME',1,'Text',Tupu, 'Optional Context identifier, typically "type/format" associated ukijumuisha the extension',),
('Extension','ProgId_','Y',Tupu, Tupu, 'ProgId',1,'Text',Tupu, 'Optional ProgId associated ukijumuisha this extension.',),
('MIME','CLSID','Y',Tupu, Tupu, Tupu, Tupu, 'Guid',Tupu, 'Optional associated CLSID.',),
('MIME','ContentType','N',Tupu, Tupu, Tupu, Tupu, 'Text',Tupu, 'Primary key. Context identifier, typically "type/format".',),
('MIME','Extension_','N',Tupu, Tupu, 'Extension',1,'Text',Tupu, 'Optional associated extension (without dot)',),
('FeatureComponents','Feature_','N',Tupu, Tupu, 'Feature',1,'Identifier',Tupu, 'Foreign key into Feature table.',),
('FeatureComponents','Component_','N',Tupu, Tupu, 'Component',1,'Identifier',Tupu, 'Foreign key into Component table.',),
('FileSFPCatalog','File_','N',Tupu, Tupu, 'File',1,'Identifier',Tupu, 'File associated ukijumuisha the catalog',),
('FileSFPCatalog','SFPCatalog_','N',Tupu, Tupu, 'SFPCatalog',1,'Filename',Tupu, 'Catalog associated ukijumuisha the file',),
('SFPCatalog','SFPCatalog','N',Tupu, Tupu, Tupu, Tupu, 'Filename',Tupu, 'File name kila the catalog.',),
('SFPCatalog','Catalog','N',Tupu, Tupu, Tupu, Tupu, 'Binary',Tupu, 'SFP Catalog',),
('SFPCatalog','Dependency','Y',Tupu, Tupu, Tupu, Tupu, 'Formatted',Tupu, 'Parent catalog - only used by SFP',),
('Font','File_','N',Tupu, Tupu, 'File',1,'Identifier',Tupu, 'Primary key, foreign key into File table referencing font file.',),
('Font','FontTitle','Y',Tupu, Tupu, Tupu, Tupu, 'Text',Tupu, 'Font name.',),
('IniFile','Action','N',Tupu, Tupu, Tupu, Tupu, Tupu, '0;1;3','The type of modification to be made, one of iifEnum',),
('IniFile','Value','N',Tupu, Tupu, Tupu, Tupu, 'Formatted',Tupu, 'The value to be written.',),
('IniFile','Component_','N',Tupu, Tupu, 'Component',1,'Identifier',Tupu, 'Foreign key into the Component table referencing component that controls the installing of the .INI value.',),
('IniFile','FileName','N',Tupu, Tupu, Tupu, Tupu, 'Filename',Tupu, 'The .INI file name kwenye which to write the information',),
('IniFile','IniFile','N',Tupu, Tupu, Tupu, Tupu, 'Identifier',Tupu, 'Primary key, non-localized token.',),
('IniFile','DirProperty','Y',Tupu, Tupu, Tupu, Tupu, 'Identifier',Tupu, 'Foreign key into the Directory table denoting the directory where the .INI file is.',),
('IniFile','Key','N',Tupu, Tupu, Tupu, Tupu, 'Formatted',Tupu, 'The .INI file key below Section.',),
('IniFile','Section','N',Tupu, Tupu, Tupu, Tupu, 'Formatted',Tupu, 'The .INI file Section.',),
('IniLocator','Type','Y',0,2,Tupu, Tupu, Tupu, Tupu, 'An integer value that determines ikiwa the .INI value read ni a filename ama a directory location ama to be used as ni w/o interpretation.',),
('IniLocator','Signature_','N',Tupu, Tupu, Tupu, Tupu, 'Identifier',Tupu, 'The table key. The Signature_ represents a unique file signature na ni also the foreign key kwenye the Signature table.',),
('IniLocator','FileName','N',Tupu, Tupu, Tupu, Tupu, 'Filename',Tupu, 'The .INI file name.',),
('IniLocator','Key','N',Tupu, Tupu, Tupu, Tupu, 'Text',Tupu, 'Key value (followed by an equals sign kwenye INI file).',),
('IniLocator','Section','N',Tupu, Tupu, Tupu, Tupu, 'Text',Tupu, 'Section name within kwenye file (within square brackets kwenye INI file).',),
('IniLocator','Field','Y',0,32767,Tupu, Tupu, Tupu, Tupu, 'The field kwenye the .INI line. If Field ni null ama 0 the entire line ni read.',),
('InstallExecuteSequence','Action','N',Tupu, Tupu, Tupu, Tupu, 'Identifier',Tupu, 'Name of action to invoke, either kwenye the engine ama the handler DLL.',),
('InstallExecuteSequence','Condition','Y',Tupu, Tupu, Tupu, Tupu, 'Condition',Tupu, 'Optional expression which skips the action ikiwa evaluates to expUongo.If the expression syntax ni invalid, the engine will terminate, returning iesBadActionData.',),
('InstallExecuteSequence','Sequence','Y',-4,32767,Tupu, Tupu, Tupu, Tupu, 'Number that determines the sort order kwenye which the actions are to be executed.  Leave blank to suppress action.',),
('InstallUISequence','Action','N',Tupu, Tupu, Tupu, Tupu, 'Identifier',Tupu, 'Name of action to invoke, either kwenye the engine ama the handler DLL.',),
('InstallUISequence','Condition','Y',Tupu, Tupu, Tupu, Tupu, 'Condition',Tupu, 'Optional expression which skips the action ikiwa evaluates to expUongo.If the expression syntax ni invalid, the engine will terminate, returning iesBadActionData.',),
('InstallUISequence','Sequence','Y',-4,32767,Tupu, Tupu, Tupu, Tupu, 'Number that determines the sort order kwenye which the actions are to be executed.  Leave blank to suppress action.',),
('IsolatedComponent','Component_Application','N',Tupu, Tupu, 'Component',1,'Identifier',Tupu, 'Key to Component table item kila application',),
('IsolatedComponent','Component_Shared','N',Tupu, Tupu, 'Component',1,'Identifier',Tupu, 'Key to Component table item to be isolated',),
('LaunchCondition','Description','N',Tupu, Tupu, Tupu, Tupu, 'Formatted',Tupu, 'Localizable text to display when condition fails na install must abort.',),
('LaunchCondition','Condition','N',Tupu, Tupu, Tupu, Tupu, 'Condition',Tupu, 'Expression which must evaluate to TRUE kwenye order kila install to commence.',),
('ListBox','Text','Y',Tupu, Tupu, Tupu, Tupu, 'Text',Tupu, 'The visible text to be assigned to the item. Optional. If this entry ama the entire column ni missing, the text ni the same as the value.',),
('ListBox','Property','N',Tupu, Tupu, Tupu, Tupu, 'Identifier',Tupu, 'A named property to be tied to this item. All the items tied to the same property become part of the same listbox.',),
('ListBox','Value','N',Tupu, Tupu, Tupu, Tupu, 'Formatted',Tupu, 'The value string associated ukijumuisha this item. Selecting the line will set the associated property to this value.',),
('ListBox','Order','N',1,32767,Tupu, Tupu, Tupu, Tupu, 'A positive integer used to determine the ordering of the items within one list..The integers do sio have to be consecutive.',),
('ListView','Text','Y',Tupu, Tupu, Tupu, Tupu, 'Text',Tupu, 'The visible text to be assigned to the item. Optional. If this entry ama the entire column ni missing, the text ni the same as the value.',),
('ListView','Property','N',Tupu, Tupu, Tupu, Tupu, 'Identifier',Tupu, 'A named property to be tied to this item. All the items tied to the same property become part of the same listview.',),
('ListView','Value','N',Tupu, Tupu, Tupu, Tupu, 'Identifier',Tupu, 'The value string associated ukijumuisha this item. Selecting the line will set the associated property to this value.',),
('ListView','Order','N',1,32767,Tupu, Tupu, Tupu, Tupu, 'A positive integer used to determine the ordering of the items within one list..The integers do sio have to be consecutive.',),
('ListView','Binary_','Y',Tupu, Tupu, 'Binary',1,'Identifier',Tupu, 'The name of the icon to be displayed ukijumuisha the icon. The binary information ni looked up kutoka the Binary Table.',),
('LockPermissions','Table','N',Tupu, Tupu, Tupu, Tupu, 'Identifier','Directory;File;Registry','Reference to another table name',),
('LockPermissions','Domain','Y',Tupu, Tupu, Tupu, Tupu, 'Formatted',Tupu, 'Domain name kila user whose permissions are being set. (usually a property)',),
('LockPermissions','LockObject','N',Tupu, Tupu, Tupu, Tupu, 'Identifier',Tupu, 'Foreign key into Registry ama File table',),
('LockPermissions','Permission','Y',-2147483647,2147483647,Tupu, Tupu, Tupu, Tupu, 'Permission Access mask.  Full Control = 268435456 (GENERIC_ALL = 0x10000000)',),
('LockPermissions','User','N',Tupu, Tupu, Tupu, Tupu, 'Formatted',Tupu, 'User kila permissions to be set.  (usually a property)',),
('Media','Source','Y',Tupu, Tupu, Tupu, Tupu, 'Property',Tupu, 'The property defining the location of the cabinet file.',),
('Media','Cabinet','Y',Tupu, Tupu, Tupu, Tupu, 'Cabinet',Tupu, 'If some ama all of the files stored on the media are compressed kwenye a cabinet, the name of that cabinet.',),
('Media','DiskId','N',1,32767,Tupu, Tupu, Tupu, Tupu, 'Primary key, integer to determine sort order kila table.',),
('Media','DiskPrompt','Y',Tupu, Tupu, Tupu, Tupu, 'Text',Tupu, 'Disk name: the visible text actually printed on the disk.  This will be used to prompt the user when this disk needs to be inserted.',),
('Media','LastSequence','N',0,32767,Tupu, Tupu, Tupu, Tupu, 'File sequence number kila the last file kila this media.',),
('Media','VolumeLabel','Y',Tupu, Tupu, Tupu, Tupu, 'Text',Tupu, 'The label attributed to the volume.',),
('ModuleComponents','Component','N',Tupu, Tupu, 'Component',1,'Identifier',Tupu, 'Component contained kwenye the module.',),
('ModuleComponents','Language','N',Tupu, Tupu, 'ModuleSignature',2,Tupu, Tupu, 'Default language ID kila module (may be changed by transform).',),
('ModuleComponents','ModuleID','N',Tupu, Tupu, 'ModuleSignature',1,'Identifier',Tupu, 'Module containing the component.',),
('ModuleSignature','Language','N',Tupu, Tupu, Tupu, Tupu, Tupu, Tupu, 'Default decimal language of module.',),
('ModuleSignature','Version','N',Tupu, Tupu, Tupu, Tupu, 'Version',Tupu, 'Version of the module.',),
('ModuleSignature','ModuleID','N',Tupu, Tupu, Tupu, Tupu, 'Identifier',Tupu, 'Module identifier (String.GUID).',),
('ModuleDependency','ModuleID','N',Tupu, Tupu, 'ModuleSignature',1,'Identifier',Tupu, 'Module requiring the dependency.',),
('ModuleDependency','ModuleLanguage','N',Tupu, Tupu, 'ModuleSignature',2,Tupu, Tupu, 'Language of module requiring the dependency.',),
('ModuleDependency','RequiredID','N',Tupu, Tupu, Tupu, Tupu, Tupu, Tupu, 'String.GUID of required module.',),
('ModuleDependency','RequiredLanguage','N',Tupu, Tupu, Tupu, Tupu, Tupu, Tupu, 'LanguageID of the required module.',),
('ModuleDependency','RequiredVersion','Y',Tupu, Tupu, Tupu, Tupu, 'Version',Tupu, 'Version of the required version.',),
('ModuleExclusion','ModuleID','N',Tupu, Tupu, 'ModuleSignature',1,'Identifier',Tupu, 'String.GUID of module ukijumuisha exclusion requirement.',),
('ModuleExclusion','ModuleLanguage','N',Tupu, Tupu, 'ModuleSignature',2,Tupu, Tupu, 'LanguageID of module ukijumuisha exclusion requirement.',),
('ModuleExclusion','ExcludedID','N',Tupu, Tupu, Tupu, Tupu, Tupu, Tupu, 'String.GUID of excluded module.',),
('ModuleExclusion','ExcludedLanguage','N',Tupu, Tupu, Tupu, Tupu, Tupu, Tupu, 'Language of excluded module.',),
('ModuleExclusion','ExcludedMaxVersion','Y',Tupu, Tupu, Tupu, Tupu, 'Version',Tupu, 'Maximum version of excluded module.',),
('ModuleExclusion','ExcludedMinVersion','Y',Tupu, Tupu, Tupu, Tupu, 'Version',Tupu, 'Minimum version of excluded module.',),
('MoveFile','Component_','N',Tupu, Tupu, 'Component',1,'Identifier',Tupu, 'If this component ni sio "selected" kila installation ama removal, no action will be taken on the associated MoveFile entry',),
('MoveFile','DestFolder','N',Tupu, Tupu, Tupu, Tupu, 'Identifier',Tupu, 'Name of a property whose value ni assumed to resolve to the full path to the destination directory',),
('MoveFile','DestName','Y',Tupu, Tupu, Tupu, Tupu, 'Filename',Tupu, 'Name to be given to the original file after it ni moved ama copied.  If blank, the destination file will be given the same name as the source file',),
('MoveFile','FileKey','N',Tupu, Tupu, Tupu, Tupu, 'Identifier',Tupu, 'Primary key that uniquely identifies a particular MoveFile record',),
('MoveFile','Options','N',0,1,Tupu, Tupu, Tupu, Tupu, 'Integer value specifying the MoveFile operating mode, one of imfoEnum',),
('MoveFile','SourceFolder','Y',Tupu, Tupu, Tupu, Tupu, 'Identifier',Tupu, 'Name of a property whose value ni assumed to resolve to the full path to the source directory',),
('MoveFile','SourceName','Y',Tupu, Tupu, Tupu, Tupu, 'Text',Tupu, "Name of the source file(s) to be moved ama copied.  Can contain the '*' ama '?' wildcards.",),
('MsiAssembly','Attributes','Y',Tupu, Tupu, Tupu, Tupu, Tupu, Tupu, 'Assembly attributes',),
('MsiAssembly','Feature_','N',Tupu, Tupu, 'Feature',1,'Identifier',Tupu, 'Foreign key into Feature table.',),
('MsiAssembly','Component_','N',Tupu, Tupu, 'Component',1,'Identifier',Tupu, 'Foreign key into Component table.',),
('MsiAssembly','File_Application','Y',Tupu, Tupu, 'File',1,'Identifier',Tupu, 'Foreign key into File table, denoting the application context kila private assemblies. Null kila global assemblies.',),
('MsiAssembly','File_Manifest','Y',Tupu, Tupu, 'File',1,'Identifier',Tupu, 'Foreign key into the File table denoting the manifest file kila the assembly.',),
('MsiAssemblyName','Name','N',Tupu, Tupu, Tupu, Tupu, 'Text',Tupu, 'The name part of the name-value pairs kila the assembly name.',),
('MsiAssemblyName','Value','N',Tupu, Tupu, Tupu, Tupu, 'Text',Tupu, 'The value part of the name-value pairs kila the assembly name.',),
('MsiAssemblyName','Component_','N',Tupu, Tupu, 'Component',1,'Identifier',Tupu, 'Foreign key into Component table.',),
('MsiDigitalCertificate','CertData','N',Tupu, Tupu, Tupu, Tupu, 'Binary',Tupu, 'A certificate context blob kila a signer certificate',),
('MsiDigitalCertificate','DigitalCertificate','N',Tupu, Tupu, Tupu, Tupu, 'Identifier',Tupu, 'A unique identifier kila the row',),
('MsiDigitalSignature','Table','N',Tupu, Tupu, Tupu, Tupu, Tupu, 'Media','Reference to another table name (only Media table ni supported)',),
('MsiDigitalSignature','DigitalCertificate_','N',Tupu, Tupu, 'MsiDigitalCertificate',1,'Identifier',Tupu, 'Foreign key to MsiDigitalCertificate table identifying the signer certificate',),
('MsiDigitalSignature','Hash','Y',Tupu, Tupu, Tupu, Tupu, 'Binary',Tupu, 'The encoded hash blob kutoka the digital signature',),
('MsiDigitalSignature','SignObject','N',Tupu, Tupu, Tupu, Tupu, 'Text',Tupu, 'Foreign key to Media table',),
('MsiFileHash','File_','N',Tupu, Tupu, 'File',1,'Identifier',Tupu, 'Primary key, foreign key into File table referencing file ukijumuisha this hash',),
('MsiFileHash','Options','N',0,32767,Tupu, Tupu, Tupu, Tupu, 'Various options na attributes kila this hash.',),
('MsiFileHash','HashPart1','N',Tupu, Tupu, Tupu, Tupu, Tupu, Tupu, 'Size of file kwenye bytes (integer).',),
('MsiFileHash','HashPart2','N',Tupu, Tupu, Tupu, Tupu, Tupu, Tupu, 'Size of file kwenye bytes (integer).',),
('MsiFileHash','HashPart3','N',Tupu, Tupu, Tupu, Tupu, Tupu, Tupu, 'Size of file kwenye bytes (integer).',),
('MsiFileHash','HashPart4','N',Tupu, Tupu, Tupu, Tupu, Tupu, Tupu, 'Size of file kwenye bytes (integer).',),
('MsiPatchHeaders','StreamRef','N',Tupu, Tupu, Tupu, Tupu, 'Identifier',Tupu, 'Primary key. A unique identifier kila the row.',),
('MsiPatchHeaders','Header','N',Tupu, Tupu, Tupu, Tupu, 'Binary',Tupu, 'Binary stream. The patch header, used kila patch validation.',),
('ODBCAttribute','Value','Y',Tupu, Tupu, Tupu, Tupu, 'Text',Tupu, 'Value kila ODBC driver attribute',),
('ODBCAttribute','Attribute','N',Tupu, Tupu, Tupu, Tupu, 'Text',Tupu, 'Name of ODBC driver attribute',),
('ODBCAttribute','Driver_','N',Tupu, Tupu, 'ODBCDriver',1,'Identifier',Tupu, 'Reference to ODBC driver kwenye ODBCDriver table',),
('ODBCDriver','Description','N',Tupu, Tupu, Tupu, Tupu, 'Text',Tupu, 'Text used as registered name kila driver, non-localized',),
('ODBCDriver','File_','N',Tupu, Tupu, 'File',1,'Identifier',Tupu, 'Reference to key driver file',),
('ODBCDriver','Component_','N',Tupu, Tupu, 'Component',1,'Identifier',Tupu, 'Reference to associated component',),
('ODBCDriver','Driver','N',Tupu, Tupu, Tupu, Tupu, 'Identifier',Tupu, 'Primary key, non-localized.internal token kila driver',),
('ODBCDriver','File_Setup','Y',Tupu, Tupu, 'File',1,'Identifier',Tupu, 'Optional reference to key driver setup DLL',),
('ODBCDataSource','Description','N',Tupu, Tupu, Tupu, Tupu, 'Text',Tupu, 'Text used as registered name kila data source',),
('ODBCDataSource','Component_','N',Tupu, Tupu, 'Component',1,'Identifier',Tupu, 'Reference to associated component',),
('ODBCDataSource','DataSource','N',Tupu, Tupu, Tupu, Tupu, 'Identifier',Tupu, 'Primary key, non-localized.internal token kila data source',),
('ODBCDataSource','DriverDescription','N',Tupu, Tupu, Tupu, Tupu, 'Text',Tupu, 'Reference to driver description, may be existing driver',),
('ODBCDataSource','Registration','N',0,1,Tupu, Tupu, Tupu, Tupu, 'Registration option: 0=machine, 1=user, others t.b.d.',),
('ODBCSourceAttribute','Value','Y',Tupu, Tupu, Tupu, Tupu, 'Text',Tupu, 'Value kila ODBC data source attribute',),
('ODBCSourceAttribute','Attribute','N',Tupu, Tupu, Tupu, Tupu, 'Text',Tupu, 'Name of ODBC data source attribute',),
('ODBCSourceAttribute','DataSource_','N',Tupu, Tupu, 'ODBCDataSource',1,'Identifier',Tupu, 'Reference to ODBC data source kwenye ODBCDataSource table',),
('ODBCTranslator','Description','N',Tupu, Tupu, Tupu, Tupu, 'Text',Tupu, 'Text used as registered name kila translator',),
('ODBCTranslator','File_','N',Tupu, Tupu, 'File',1,'Identifier',Tupu, 'Reference to key translator file',),
('ODBCTranslator','Component_','N',Tupu, Tupu, 'Component',1,'Identifier',Tupu, 'Reference to associated component',),
('ODBCTranslator','File_Setup','Y',Tupu, Tupu, 'File',1,'Identifier',Tupu, 'Optional reference to key translator setup DLL',),
('ODBCTranslator','Translator','N',Tupu, Tupu, Tupu, Tupu, 'Identifier',Tupu, 'Primary key, non-localized.internal token kila translator',),
('Patch','Sequence','N',0,32767,Tupu, Tupu, Tupu, Tupu, 'Primary key, sequence ukijumuisha respect to the media images; order must track cabinet order.',),
('Patch','Attributes','N',0,32767,Tupu, Tupu, Tupu, Tupu, 'Integer containing bit flags representing patch attributes',),
('Patch','File_','N',Tupu, Tupu, Tupu, Tupu, 'Identifier',Tupu, 'Primary key, non-localized token, foreign key to File table, must match identifier kwenye cabinet.',),
('Patch','Header','Y',Tupu, Tupu, Tupu, Tupu, 'Binary',Tupu, 'Binary stream. The patch header, used kila patch validation.',),
('Patch','PatchSize','N',0,2147483647,Tupu, Tupu, Tupu, Tupu, 'Size of patch kwenye bytes (integer).',),
('Patch','StreamRef_','Y',Tupu, Tupu, Tupu, Tupu, 'Identifier',Tupu, 'Identifier. Foreign key to the StreamRef column of the MsiPatchHeaders table.',),
('PatchPackage','Media_','N',0,32767,Tupu, Tupu, Tupu, Tupu, 'Foreign key to DiskId column of Media table. Indicates the disk containing the patch package.',),
('PatchPackage','PatchId','N',Tupu, Tupu, Tupu, Tupu, 'Guid',Tupu, 'A unique string GUID representing this patch.',),
('PublishComponent','Feature_','N',Tupu, Tupu, 'Feature',1,'Identifier',Tupu, 'Foreign key into the Feature table.',),
('PublishComponent','Component_','N',Tupu, Tupu, 'Component',1,'Identifier',Tupu, 'Foreign key into the Component table.',),
('PublishComponent','ComponentId','N',Tupu, Tupu, Tupu, Tupu, 'Guid',Tupu, 'A string GUID that represents the component id that will be requested by the alien product.',),
('PublishComponent','AppData','Y',Tupu, Tupu, Tupu, Tupu, 'Text',Tupu, 'This ni localisable Application specific data that can be associated ukijumuisha a Qualified Component.',),
('PublishComponent','Qualifier','N',Tupu, Tupu, Tupu, Tupu, 'Text',Tupu, 'This ni defined only when the ComponentId column ni an Qualified Component Id. This ni the Qualifier kila ProvideComponentIndirect.',),
('RadioButton','Y','N',0,32767,Tupu, Tupu, Tupu, Tupu, 'The vertical coordinate of the upper left corner of the bounding rectangle of the radio button.',),
('RadioButton','Text','Y',Tupu, Tupu, Tupu, Tupu, 'Text',Tupu, 'The visible title to be assigned to the radio button.',),
('RadioButton','Property','N',Tupu, Tupu, Tupu, Tupu, 'Identifier',Tupu, 'A named property to be tied to this radio button. All the buttons tied to the same property become part of the same group.',),
('RadioButton','Height','N',0,32767,Tupu, Tupu, Tupu, Tupu, 'The height of the button.',),
('RadioButton','Width','N',0,32767,Tupu, Tupu, Tupu, Tupu, 'The width of the button.',),
('RadioButton','X','N',0,32767,Tupu, Tupu, Tupu, Tupu, 'The horizontal coordinate of the upper left corner of the bounding rectangle of the radio button.',),
('RadioButton','Value','N',Tupu, Tupu, Tupu, Tupu, 'Formatted',Tupu, 'The value string associated ukijumuisha this button. Selecting the button will set the associated property to this value.',),
('RadioButton','Order','N',1,32767,Tupu, Tupu, Tupu, Tupu, 'A positive integer used to determine the ordering of the items within one list..The integers do sio have to be consecutive.',),
('RadioButton','Help','Y',Tupu, Tupu, Tupu, Tupu, 'Text',Tupu, 'The help strings used ukijumuisha the button. The text ni optional.',),
('Registry','Name','Y',Tupu, Tupu, Tupu, Tupu, 'Formatted',Tupu, 'The registry value name.',),
('Registry','Value','Y',Tupu, Tupu, Tupu, Tupu, 'Formatted',Tupu, 'The registry value.',),
('Registry','Component_','N',Tupu, Tupu, 'Component',1,'Identifier',Tupu, 'Foreign key into the Component table referencing component that controls the installing of the registry value.',),
('Registry','Key','N',Tupu, Tupu, Tupu, Tupu, 'RegPath',Tupu, 'The key kila the registry value.',),
('Registry','Registry','N',Tupu, Tupu, Tupu, Tupu, 'Identifier',Tupu, 'Primary key, non-localized token.',),
('Registry','Root','N',-1,3,Tupu, Tupu, Tupu, Tupu, 'The predefined root key kila the registry value, one of rrkEnum.',),
('RegLocator','Name','Y',Tupu, Tupu, Tupu, Tupu, 'Formatted',Tupu, 'The registry value name.',),
('RegLocator','Type','Y',0,18,Tupu, Tupu, Tupu, Tupu, 'An integer value that determines ikiwa the registry value ni a filename ama a directory location ama to be used as ni w/o interpretation.',),
('RegLocator','Signature_','N',Tupu, Tupu, Tupu, Tupu, 'Identifier',Tupu, 'The table key. The Signature_ represents a unique file signature na ni also the foreign key kwenye the Signature table. If the type ni 0, the registry values refers a directory, na _Signature ni sio a foreign key.',),
('RegLocator','Key','N',Tupu, Tupu, Tupu, Tupu, 'RegPath',Tupu, 'The key kila the registry value.',),
('RegLocator','Root','N',0,3,Tupu, Tupu, Tupu, Tupu, 'The predefined root key kila the registry value, one of rrkEnum.',),
('RemoveFile','Component_','N',Tupu, Tupu, 'Component',1,'Identifier',Tupu, 'Foreign key referencing Component that controls the file to be removed.',),
('RemoveFile','FileKey','N',Tupu, Tupu, Tupu, Tupu, 'Identifier',Tupu, 'Primary key used to identify a particular file entry',),
('RemoveFile','FileName','Y',Tupu, Tupu, Tupu, Tupu, 'WildCardFilename',Tupu, 'Name of the file to be removed.',),
('RemoveFile','DirProperty','N',Tupu, Tupu, Tupu, Tupu, 'Identifier',Tupu, 'Name of a property whose value ni assumed to resolve to the full pathname to the folder of the file to be removed.',),
('RemoveFile','InstallMode','N',Tupu, Tupu, Tupu, Tupu, Tupu, '1;2;3','Installation option, one of iimEnum.',),
('RemoveIniFile','Action','N',Tupu, Tupu, Tupu, Tupu, Tupu, '2;4','The type of modification to be made, one of iifEnum.',),
('RemoveIniFile','Value','Y',Tupu, Tupu, Tupu, Tupu, 'Formatted',Tupu, 'The value to be deleted. The value ni required when Action ni iifIniRemoveTag',),
('RemoveIniFile','Component_','N',Tupu, Tupu, 'Component',1,'Identifier',Tupu, 'Foreign key into the Component table referencing component that controls the deletion of the .INI value.',),
('RemoveIniFile','FileName','N',Tupu, Tupu, Tupu, Tupu, 'Filename',Tupu, 'The .INI file name kwenye which to delete the information',),
('RemoveIniFile','DirProperty','Y',Tupu, Tupu, Tupu, Tupu, 'Identifier',Tupu, 'Foreign key into the Directory table denoting the directory where the .INI file is.',),
('RemoveIniFile','Key','N',Tupu, Tupu, Tupu, Tupu, 'Formatted',Tupu, 'The .INI file key below Section.',),
('RemoveIniFile','Section','N',Tupu, Tupu, Tupu, Tupu, 'Formatted',Tupu, 'The .INI file Section.',),
('RemoveIniFile','RemoveIniFile','N',Tupu, Tupu, Tupu, Tupu, 'Identifier',Tupu, 'Primary key, non-localized token.',),
('RemoveRegistry','Name','Y',Tupu, Tupu, Tupu, Tupu, 'Formatted',Tupu, 'The registry value name.',),
('RemoveRegistry','Component_','N',Tupu, Tupu, 'Component',1,'Identifier',Tupu, 'Foreign key into the Component table referencing component that controls the deletion of the registry value.',),
('RemoveRegistry','Key','N',Tupu, Tupu, Tupu, Tupu, 'RegPath',Tupu, 'The key kila the registry value.',),
('RemoveRegistry','Root','N',-1,3,Tupu, Tupu, Tupu, Tupu, 'The predefined root key kila the registry value, one of rrkEnum',),
('RemoveRegistry','RemoveRegistry','N',Tupu, Tupu, Tupu, Tupu, 'Identifier',Tupu, 'Primary key, non-localized token.',),
('ReserveCost','Component_','N',Tupu, Tupu, 'Component',1,'Identifier',Tupu, 'Reserve a specified amount of space ikiwa this component ni to be installed.',),
('ReserveCost','ReserveFolder','Y',Tupu, Tupu, Tupu, Tupu, 'Identifier',Tupu, 'Name of a property whose value ni assumed to resolve to the full path to the destination directory',),
('ReserveCost','ReserveKey','N',Tupu, Tupu, Tupu, Tupu, 'Identifier',Tupu, 'Primary key that uniquely identifies a particular ReserveCost record',),
('ReserveCost','ReserveLocal','N',0,2147483647,Tupu, Tupu, Tupu, Tupu, 'Disk space to reserve ikiwa linked component ni installed locally.',),
('ReserveCost','ReserveSource','N',0,2147483647,Tupu, Tupu, Tupu, Tupu, 'Disk space to reserve ikiwa linked component ni installed to run kutoka the source location.',),
('SelfReg','File_','N',Tupu, Tupu, 'File',1,'Identifier',Tupu, 'Foreign key into the File table denoting the module that needs to be registered.',),
('SelfReg','Cost','Y',0,32767,Tupu, Tupu, Tupu, Tupu, 'The cost of registering the module.',),
('ServiceControl','Name','N',Tupu, Tupu, Tupu, Tupu, 'Formatted',Tupu, 'Name of a service. /, \\, comma na space are invalid',),
('ServiceControl','Component_','N',Tupu, Tupu, 'Component',1,'Identifier',Tupu, 'Required foreign key into the Component Table that controls the startup of the service',),
('ServiceControl','Event','N',0,187,Tupu, Tupu, Tupu, Tupu, 'Bit field:  Install:  0x1 = Start, 0x2 = Stop, 0x8 = Delete, Uninstall: 0x10 = Start, 0x20 = Stop, 0x80 = Delete',),
('ServiceControl','ServiceControl','N',Tupu, Tupu, Tupu, Tupu, 'Identifier',Tupu, 'Primary key, non-localized token.',),
('ServiceControl','Arguments','Y',Tupu, Tupu, Tupu, Tupu, 'Formatted',Tupu, 'Arguments kila the service.  Separate by [~].',),
('ServiceControl','Wait','Y',0,1,Tupu, Tupu, Tupu, Tupu, 'Boolean kila whether to wait kila the service to fully start',),
('ServiceInstall','Name','N',Tupu, Tupu, Tupu, Tupu, 'Formatted',Tupu, 'Internal Name of the Service',),
('ServiceInstall','Description','Y',Tupu, Tupu, Tupu, Tupu, 'Text',Tupu, 'Description of service.',),
('ServiceInstall','Component_','N',Tupu, Tupu, 'Component',1,'Identifier',Tupu, 'Required foreign key into the Component Table that controls the startup of the service',),
('ServiceInstall','Arguments','Y',Tupu, Tupu, Tupu, Tupu, 'Formatted',Tupu, 'Arguments to include kwenye every start of the service, passed to WinMain',),
('ServiceInstall','ServiceInstall','N',Tupu, Tupu, Tupu, Tupu, 'Identifier',Tupu, 'Primary key, non-localized token.',),
('ServiceInstall','Dependencies','Y',Tupu, Tupu, Tupu, Tupu, 'Formatted',Tupu, 'Other services this depends on to start.  Separate by [~], na end ukijumuisha [~][~]',),
('ServiceInstall','DisplayName','Y',Tupu, Tupu, Tupu, Tupu, 'Formatted',Tupu, 'External Name of the Service',),
('ServiceInstall','ErrorControl','N',-2147483647,2147483647,Tupu, Tupu, Tupu, Tupu, 'Severity of error ikiwa service fails to start',),
('ServiceInstall','LoadOrderGroup','Y',Tupu, Tupu, Tupu, Tupu, 'Formatted',Tupu, 'LoadOrderGroup',),
('ServiceInstall','Password','Y',Tupu, Tupu, Tupu, Tupu, 'Formatted',Tupu, 'password to run service with.  (ukijumuisha StartName)',),
('ServiceInstall','ServiceType','N',-2147483647,2147483647,Tupu, Tupu, Tupu, Tupu, 'Type of the service',),
('ServiceInstall','StartName','Y',Tupu, Tupu, Tupu, Tupu, 'Formatted',Tupu, 'User ama object name to run service as',),
('ServiceInstall','StartType','N',0,4,Tupu, Tupu, Tupu, Tupu, 'Type of the service',),
('Shortcut','Name','N',Tupu, Tupu, Tupu, Tupu, 'Filename',Tupu, 'The name of the shortcut to be created.',),
('Shortcut','Description','Y',Tupu, Tupu, Tupu, Tupu, 'Text',Tupu, 'The description kila the shortcut.',),
('Shortcut','Component_','N',Tupu, Tupu, 'Component',1,'Identifier',Tupu, 'Foreign key into the Component table denoting the component whose selection gates the shortcut creation/deletion.',),
('Shortcut','Icon_','Y',Tupu, Tupu, 'Icon',1,'Identifier',Tupu, 'Foreign key into the File table denoting the external icon file kila the shortcut.',),
('Shortcut','IconIndex','Y',-32767,32767,Tupu, Tupu, Tupu, Tupu, 'The icon index kila the shortcut.',),
('Shortcut','Directory_','N',Tupu, Tupu, 'Directory',1,'Identifier',Tupu, 'Foreign key into the Directory table denoting the directory where the shortcut file ni created.',),
('Shortcut','Target','N',Tupu, Tupu, Tupu, Tupu, 'Shortcut',Tupu, 'The shortcut target. This ni usually a property that ni expanded to a file ama a folder that the shortcut points to.',),
('Shortcut','Arguments','Y',Tupu, Tupu, Tupu, Tupu, 'Formatted',Tupu, 'The command-line arguments kila the shortcut.',),
('Shortcut','Shortcut','N',Tupu, Tupu, Tupu, Tupu, 'Identifier',Tupu, 'Primary key, non-localized token.',),
('Shortcut','Hotkey','Y',0,32767,Tupu, Tupu, Tupu, Tupu, 'The hotkey kila the shortcut. It has the virtual-key code kila the key kwenye the low-order byte, na the modifier flags kwenye the high-order byte. ',),
('Shortcut','ShowCmd','Y',Tupu, Tupu, Tupu, Tupu, Tupu, '1;3;7','The show command kila the application window.The following values may be used.',),
('Shortcut','WkDir','Y',Tupu, Tupu, Tupu, Tupu, 'Identifier',Tupu, 'Name of property defining location of working directory.',),
('Signature','FileName','N',Tupu, Tupu, Tupu, Tupu, 'Filename',Tupu, 'The name of the file. This may contain a "short name|long name" pair.',),
('Signature','Signature','N',Tupu, Tupu, Tupu, Tupu, 'Identifier',Tupu, 'The table key. The Signature represents a unique file signature.',),
('Signature','Languages','Y',Tupu, Tupu, Tupu, Tupu, 'Language',Tupu, 'The languages supported by the file.',),
('Signature','MaxDate','Y',0,2147483647,Tupu, Tupu, Tupu, Tupu, 'The maximum creation date of the file.',),
('Signature','MaxSize','Y',0,2147483647,Tupu, Tupu, Tupu, Tupu, 'The maximum size of the file. ',),
('Signature','MaxVersion','Y',Tupu, Tupu, Tupu, Tupu, 'Text',Tupu, 'The maximum version of the file.',),
('Signature','MinDate','Y',0,2147483647,Tupu, Tupu, Tupu, Tupu, 'The minimum creation date of the file.',),
('Signature','MinSize','Y',0,2147483647,Tupu, Tupu, Tupu, Tupu, 'The minimum size of the file.',),
('Signature','MinVersion','Y',Tupu, Tupu, Tupu, Tupu, 'Text',Tupu, 'The minimum version of the file.',),
('TextStyle','TextStyle','N',Tupu, Tupu, Tupu, Tupu, 'Identifier',Tupu, 'Name of the style. The primary key of this table. This name ni embedded kwenye the texts to indicate a style change.',),
('TextStyle','Color','Y',0,16777215,Tupu, Tupu, Tupu, Tupu, 'An integer indicating the color of the string kwenye the RGB format (Red, Green, Blue each 0-255, RGB = R + 256*G + 256^2*B).',),
('TextStyle','FaceName','N',Tupu, Tupu, Tupu, Tupu, 'Text',Tupu, 'A string indicating the name of the font used. Required. The string must be at most 31 characters long.',),
('TextStyle','Size','N',0,32767,Tupu, Tupu, Tupu, Tupu, 'The size of the font used. This size ni given kwenye our units (1/12 of the system font height). Assuming that the system font ni set to 12 point size, this ni equivalent to the point size.',),
('TextStyle','StyleBits','Y',0,15,Tupu, Tupu, Tupu, Tupu, 'A combination of style bits.',),
('TypeLib','Description','Y',Tupu, Tupu, Tupu, Tupu, 'Text',Tupu, Tupu, ),
('TypeLib','Feature_','N',Tupu, Tupu, 'Feature',1,'Identifier',Tupu, 'Required foreign key into the Feature Table, specifying the feature to validate ama install kwenye order kila the type library to be operational.',),
('TypeLib','Component_','N',Tupu, Tupu, 'Component',1,'Identifier',Tupu, 'Required foreign key into the Component Table, specifying the component kila which to rudisha a path when called through LocateComponent.',),
('TypeLib','Directory_','Y',Tupu, Tupu, 'Directory',1,'Identifier',Tupu, 'Optional. The foreign key into the Directory table denoting the path to the help file kila the type library.',),
('TypeLib','Language','N',0,32767,Tupu, Tupu, Tupu, Tupu, 'The language of the library.',),
('TypeLib','Version','Y',0,16777215,Tupu, Tupu, Tupu, Tupu, 'The version of the library. The minor version ni kwenye the lower 8 bits of the integer. The major version ni kwenye the next 16 bits. ',),
('TypeLib','Cost','Y',0,2147483647,Tupu, Tupu, Tupu, Tupu, 'The cost associated ukijumuisha the registration of the typelib. This column ni currently optional.',),
('TypeLib','LibID','N',Tupu, Tupu, Tupu, Tupu, 'Guid',Tupu, 'The GUID that represents the library.',),
('UIText','Text','Y',Tupu, Tupu, Tupu, Tupu, 'Text',Tupu, 'The localized version of the string.',),
('UIText','Key','N',Tupu, Tupu, Tupu, Tupu, 'Identifier',Tupu, 'A unique key that identifies the particular string.',),
('Upgrade','Attributes','N',0,2147483647,Tupu, Tupu, Tupu, Tupu, 'The attributes of this product set.',),
('Upgrade','Language','Y',Tupu, Tupu, Tupu, Tupu, 'Language',Tupu, 'A comma-separated list of languages kila either products kwenye this set ama products sio kwenye this set.',),
('Upgrade','ActionProperty','N',Tupu, Tupu, Tupu, Tupu, 'UpperCase',Tupu, 'The property to set when a product kwenye this set ni found.',),
('Upgrade','Remove','Y',Tupu, Tupu, Tupu, Tupu, 'Formatted',Tupu, 'The list of features to remove when uninstalling a product kutoka this set.  The default ni "ALL".',),
('Upgrade','UpgradeCode','N',Tupu, Tupu, Tupu, Tupu, 'Guid',Tupu, 'The UpgradeCode GUID belonging to the products kwenye this set.',),
('Upgrade','VersionMax','Y',Tupu, Tupu, Tupu, Tupu, 'Text',Tupu, 'The maximum ProductVersion of the products kwenye this set.  The set may ama may sio include products ukijumuisha this particular version.',),
('Upgrade','VersionMin','Y',Tupu, Tupu, Tupu, Tupu, 'Text',Tupu, 'The minimum ProductVersion of the products kwenye this set.  The set may ama may sio include products ukijumuisha this particular version.',),
('Verb','Sequence','Y',0,32767,Tupu, Tupu, Tupu, Tupu, 'Order within the verbs kila a particular extension. Also used simply to specify the default verb.',),
('Verb','Argument','Y',Tupu, Tupu, Tupu, Tupu, 'Formatted',Tupu, 'Optional value kila the command arguments.',),
('Verb','Extension_','N',Tupu, Tupu, 'Extension',1,'Text',Tupu, 'The extension associated ukijumuisha the table row.',),
('Verb','Verb','N',Tupu, Tupu, Tupu, Tupu, 'Text',Tupu, 'The verb kila the command.',),
('Verb','Command','Y',Tupu, Tupu, Tupu, Tupu, 'Formatted',Tupu, 'The command text.',),
]
