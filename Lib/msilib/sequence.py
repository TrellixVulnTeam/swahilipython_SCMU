AdminExecuteSequence = [
('InstallInitialize', Tupu, 1500),
('InstallFinalize', Tupu, 6600),
('InstallFiles', Tupu, 4000),
('InstallAdminPackage', Tupu, 3900),
('FileCost', Tupu, 900),
('CostInitialize', Tupu, 800),
('CostFinalize', Tupu, 1000),
('InstallValidate', Tupu, 1400),
]

AdminUISequence = [
('FileCost', Tupu, 900),
('CostInitialize', Tupu, 800),
('CostFinalize', Tupu, 1000),
('ExecuteAction', Tupu, 1300),
('ExitDialog', Tupu, -1),
('FatalError', Tupu, -3),
('UserExit', Tupu, -2),
]

AdvtExecuteSequence = [
('InstallInitialize', Tupu, 1500),
('InstallFinalize', Tupu, 6600),
('CostInitialize', Tupu, 800),
('CostFinalize', Tupu, 1000),
('InstallValidate', Tupu, 1400),
('CreateShortcuts', Tupu, 4500),
('MsiPublishAssemblies', Tupu, 6250),
('PublishComponents', Tupu, 6200),
('PublishFeatures', Tupu, 6300),
('PublishProduct', Tupu, 6400),
('RegisterClassInfo', Tupu, 4600),
('RegisterExtensionInfo', Tupu, 4700),
('RegisterMIMEInfo', Tupu, 4900),
('RegisterProgIdInfo', Tupu, 4800),
]

InstallExecuteSequence = [
('InstallInitialize', Tupu, 1500),
('InstallFinalize', Tupu, 6600),
('InstallFiles', Tupu, 4000),
('FileCost', Tupu, 900),
('CostInitialize', Tupu, 800),
('CostFinalize', Tupu, 1000),
('InstallValidate', Tupu, 1400),
('CreateShortcuts', Tupu, 4500),
('MsiPublishAssemblies', Tupu, 6250),
('PublishComponents', Tupu, 6200),
('PublishFeatures', Tupu, 6300),
('PublishProduct', Tupu, 6400),
('RegisterClassInfo', Tupu, 4600),
('RegisterExtensionInfo', Tupu, 4700),
('RegisterMIMEInfo', Tupu, 4900),
('RegisterProgIdInfo', Tupu, 4800),
('AllocateRegistrySpace', 'NOT Installed', 1550),
('AppSearch', Tupu, 400),
('BindImage', Tupu, 4300),
('CCPSearch', 'NOT Installed', 500),
('CreateFolders', Tupu, 3700),
('DeleteServices', 'VersionNT', 2000),
('DuplicateFiles', Tupu, 4210),
('FindRelatedProducts', Tupu, 200),
('InstallODBC', Tupu, 5400),
('InstallServices', 'VersionNT', 5800),
('IsolateComponents', Tupu, 950),
('LaunchConditions', Tupu, 100),
('MigrateFeatureStates', Tupu, 1200),
('MoveFiles', Tupu, 3800),
('PatchFiles', Tupu, 4090),
('ProcessComponents', Tupu, 1600),
('RegisterComPlus', Tupu, 5700),
('RegisterFonts', Tupu, 5300),
('RegisterProduct', Tupu, 6100),
('RegisterTypeLibraries', Tupu, 5500),
('RegisterUser', Tupu, 6000),
('RemoveDuplicateFiles', Tupu, 3400),
('RemoveEnvironmentStrings', Tupu, 3300),
('RemoveExistingProducts', Tupu, 6700),
('RemoveFiles', Tupu, 3500),
('RemoveFolders', Tupu, 3600),
('RemoveIniValues', Tupu, 3100),
('RemoveODBC', Tupu, 2400),
('RemoveRegistryValues', Tupu, 2600),
('RemoveShortcuts', Tupu, 3200),
('RMCCPSearch', 'NOT Installed', 600),
('SelfRegModules', Tupu, 5600),
('SelfUnregModules', Tupu, 2200),
('SetODBCFolders', Tupu, 1100),
('StartServices', 'VersionNT', 5900),
('StopServices', 'VersionNT', 1900),
('MsiUnpublishAssemblies', Tupu, 1750),
('UnpublishComponents', Tupu, 1700),
('UnpublishFeatures', Tupu, 1800),
('UnregisterClassInfo', Tupu, 2700),
('UnregisterComPlus', Tupu, 2100),
('UnregisterExtensionInfo', Tupu, 2800),
('UnregisterFonts', Tupu, 2500),
('UnregisterMIMEInfo', Tupu, 3000),
('UnregisterProgIdInfo', Tupu, 2900),
('UnregisterTypeLibraries', Tupu, 2300),
('ValidateProductID', Tupu, 700),
('WriteEnvironmentStrings', Tupu, 5200),
('WriteIniValues', Tupu, 5100),
('WriteRegistryValues', Tupu, 5000),
]

InstallUISequence = [
('FileCost', Tupu, 900),
('CostInitialize', Tupu, 800),
('CostFinalize', Tupu, 1000),
('ExecuteAction', Tupu, 1300),
('ExitDialog', Tupu, -1),
('FatalError', Tupu, -3),
('UserExit', Tupu, -2),
('AppSearch', Tupu, 400),
('CCPSearch', 'NOT Installed', 500),
('FindRelatedProducts', Tupu, 200),
('IsolateComponents', Tupu, 950),
('LaunchConditions', Tupu, 100),
('MigrateFeatureStates', Tupu, 1200),
('RMCCPSearch', 'NOT Installed', 600),
('ValidateProductID', Tupu, 700),
]

tables=['AdminExecuteSequence', 'AdminUISequence', 'AdvtExecuteSequence', 'InstallExecuteSequence', 'InstallUISequence']
